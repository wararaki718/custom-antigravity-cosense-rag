import os
import time

from elasticsearch import Elasticsearch
try:
    from .logger import logger
except ImportError:
    from logger import logger

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX_NAME = os.getenv("INDEX_NAME", "cosense-pages")


def setup_index():
    es = Elasticsearch(ELASTICSEARCH_URL)

    # Wait for ES to be ready
    for i in range(10):
        try:
            if es.ping():
                break
        except Exception:
            pass
        logger.info("Waiting for Elasticsearch...")
        time.sleep(5)

    if es.indices.exists(index=INDEX_NAME):
        logger.info(f"Index {INDEX_NAME} already exists.")
        return

    mapping = {
        "settings": {
            "index": {
                "analysis": {
                    "analyzer": {
                        "japanese_analyzer": {
                            "type": "custom",
                            "tokenizer": "kuromoji_tokenizer",
                        }
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "title": {"type": "text", "analyzer": "japanese_analyzer"},
                "content": {"type": "text", "analyzer": "japanese_analyzer"},
                "url": {"type": "keyword"},
                "updated": {"type": "date"},
                "vectors": {"type": "rank_features"},
            }
        },
    }

    es.indices.create(index=INDEX_NAME, body=mapping)
    logger.info(f"Index {INDEX_NAME} created successfully.")


if __name__ == "__main__":
    setup_index()
