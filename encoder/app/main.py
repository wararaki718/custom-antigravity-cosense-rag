import os

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForMaskedLM, BertJapaneseTokenizer

app = FastAPI(title="Japanese SPLADE Encoder")

# Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "hotchpotch/japanese-splade-base-v1")

# Load model and tokenizer
print(f"Loading model: {MODEL_NAME}")
# Explicitly use BertJapaneseTokenizer for this Japanese model
tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME)
print("Model loaded successfully.")


class EncodeRequest(BaseModel):
    text: str


class EncodeResponse(BaseModel):
    vectors: dict[str, float]


@app.post("/encode", response_model=EncodeResponse)
async def encode(request: EncodeRequest):
    if not request.text.strip():
        return EncodeResponse(vectors={})

    try:
        inputs = tokenizer(request.text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)

        # Compute SPLADE scores
        logits = outputs.logits
        # max-pooling over log(1 + ReLU(output))
        scores = torch.max(torch.log1p(torch.relu(logits)), dim=1).values[0]

        # Get non-zero dimensions
        cols = torch.nonzero(scores).flatten().tolist()
        weights = scores[cols].tolist()

        # Map back to tokens
        THRESHOLD = 0.05  # Standard threshold
        vectors = {}
        for c, w in zip(cols, weights):
            if w > THRESHOLD:
                token = tokenizer.decode([c]).strip()
                if token:
                    # Clean up subword prefix if exists (## for BERT)
                    token = token.replace("##", "")
                    if token:
                        vectors[token] = max(vectors.get(token, 0), float(w))

        return EncodeResponse(vectors=vectors)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
