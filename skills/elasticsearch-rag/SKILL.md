---
name: elasticsearch-rag
description: "Instructions for Elasticsearch indexing and retrieval for RAG."
---

# Elasticsearch RAG Skill

## Goal
Index sparse vectors into Elasticsearch and perform queries to retrieve relevant documents.

## Index Mapping
The index should use `kuromoji` analyzer for text and `rank_features` for SPLADE vectors.

```json
{
  "settings": {
    "index": {
      "analysis": {
        "analyzer": {
          "japanese_analyzer": {
            "type": "custom",
            "tokenizer": "kuromoji_tokenizer"
          }
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": { "type": "text", "analyzer": "japanese_analyzer" },
      "content": { "type": "text", "analyzer": "japanese_analyzer" },
      "url": { "type": "keyword" },
      "vectors": { "type": "rank_features" }
    }
  }
}
```

## Retrieval Logic (Hybrid Search)
Search using `rank_feature` query for sparse retrieval.

```json
{
  "query": {
    "bool": {
      "should": [
        { "match": { "content": "query text" } },
        { "rank_feature": { "field": "vectors.vector_name", "boost": 1.0 } }
      ]
    }
  }
}
```

## Implementation Notes
- Use the `elasticsearch` Python client.
- When indexing, the SPLADE output (dict of token: weight) should be flattened into the `vectors` object.
- Ensure the number of features per document doesn't exceed Elasticsearch limits if using many tokens.
