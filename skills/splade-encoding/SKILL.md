---
name: splade-encoding
description: "Instructions for SPLADE sparse vector encoding."
---

# SPLADE Encoding Skill

## Goal
Encode text documents and queries into sparse vectors using the SPLADE (Sparse Lexical and Expansion) model.

## Service Details
- The `encoder` should be a standalone Python FastAPI service.
- **Endpoint**: `POST /encode`
- **Request Body**: `{"text": "input text"}`
- **Response**: `{"vectors": {"token1": weight1, "token2": weight2, ...}}`

## Model Details
- Use `hotchpotch/japanese-splade-v2-distil-base-v1` or similar.
- Library: `transformers` and `torch`.

## Encoding Logic
1. Tokenize input text (Japanese support via `fugashi`/`unidic`).
2. Forward pass through the SPLADE model.
3. Compute max-pooling over the log of (1 + ReLU(output)).
4. Extract non-zero dimensions and their scores to create a sparse representation.

## Data Format
- Store as a mapping of `token_id` (or string token) to `weight`.
- For Elasticsearch, this should be compatible with the `rank_features` field type.

## Example Python Implementation
```python
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

model_id = "naver/splade-v2-distil-cocondenser-ensembled"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForMaskedLM.from_pretrained(model_id)

def encode(text):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Compute SPLADE scores
    logits = outputs.logits
    # max-over-time (dim=1)
    scores = torch.max(torch.log1p(torch.relu(logits)), dim=1).values[0]
    
    # Get non-zero dimensions
    cols = torch.nonzero(scores).flatten().tolist()
    weights = scores[cols].tolist()
    
    return {tokenizer.decode([c]): w for c, w in zip(cols, weights)}
```
