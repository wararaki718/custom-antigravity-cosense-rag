import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from elasticsearch import Elasticsearch

load_dotenv()

app = FastAPI(title="Cosense RAG Search API")

# Configuration
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ENCODER_URL = os.getenv("ENCODER_URL", "http://localhost:8001")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
INDEX_NAME = os.getenv("INDEX_NAME", "cosense-pages")

es = Elasticsearch(ELASTICSEARCH_URL)
client = httpx.Client(timeout=60.0)


class QueryRequest(BaseModel):
    query: str


class SearchResult(BaseModel):
    title: str
    content: str
    url: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    results: list[SearchResult]


@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    query_text = request.query
    if not query_text.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # 1. Encode query to sparse vector
        encoder_resp = client.post(f"{ENCODER_URL}/encode", json={"text": query_text})
        encoder_resp.raise_for_status()
        query_vectors = encoder_resp.json()["vectors"]

        # 2. Search Elasticsearch
        # Hybrid search: Match on content + Rank features
        search_query = {
            "bool": {
                "should": [
                    {"match": {"content": query_text}},
                    {
                        "rank_feature": {
                            "field": f"vectors.{list(query_vectors.keys())[0]}",
                            "boost": 1.0,
                        }
                    }
                    if query_vectors
                    else {"match_none": {}},
                ]
            }
        }

        # Actually, for multiple rank features, we might want to iterate or use
        # a more complex query. But rank_feature only supports one feature per clause.
        # Efficient way for SPLADE is usually multiple should rank_feature clauses:
        if query_vectors:
            rank_clauses = [
                {"rank_feature": {"field": f"vectors.{token}", "boost": weight}}
                for token, weight in query_vectors.items()
            ]
            # Limit number of clauses to avoid ES limits if necessary
            search_query["bool"]["should"] = [
                {"match": {"content": query_text}}
            ] + rank_clauses[:50]  # Top 50 tokens
        else:
            search_query["bool"]["should"] = [{"match": {"content": query_text}}]

        resp = es.search(index=INDEX_NAME, query=search_query, size=5)
        hits = resp["hits"]["hits"]

        results = [
            SearchResult(
                title=hit["_source"]["title"],
                content=hit["_source"]["content"],
                url=hit["_source"]["url"],
                score=hit["_score"],
            )
            for hit in hits
        ]

        # 3. Generate answer using Ollama
        context = "\n\n".join(
            [f"Title: {r.title}\nContent: {r.content}" for r in results]
        )

        prompt = f"""以下のコンテキスト情報に基づいて質問に答えてください。
コンテキストに情報がない場合は「わかりません」と答えてください。

Context:
{context}

Question:
{query_text}

Answer:"""

        ollama_payload = {
            "model": "gemma3",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }

        try:
            ollama_resp = client.post(f"{OLLAMA_URL}/api/chat", json=ollama_payload)
            ollama_resp.raise_for_status()
            answer = ollama_resp.json()["message"]["content"]
        except Exception as e:
            print(f"Ollama error: {e}")
            answer = (
                "Sorry, I couldn't generate an answer due to an error with the LLM."
            )

        return QueryResponse(answer=answer, results=results)

    except Exception as e:
        print(f"Search API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
