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
    logger.info(f"Connecting to Elasticsearch at: {ELASTICSEARCH_URL}")
    if not ELASTICSEARCH_URL or "elasticsearch" not in ELASTICSEARCH_URL:
        logger.warning(f"ELASTICSEARCH_URL might be incorrect: {ELASTICSEARCH_URL}")

    es = Elasticsearch(
        ELASTICSEARCH_URL,
        request_timeout=30,
        verify_certs=False,  # Ignore cert issues for local debug
    )

    # Wait for ES to be ready
    is_ready = False
    for i in range(20):  # More attempts
        try:
            logger.info(f"Pinging Elasticsearch (attempt {i+1}/20)...")
            if es.ping():
                logger.info("Elasticsearch is ready!")
                is_ready = True
                break
            else:
                logger.warning("Elasticsearch ping returned False.")
        except Exception as e:
            logger.error(f"Elasticsearch ping failed: {type(e).__name__}: {e}")
        time.sleep(3)

    if not is_ready:
        logger.error("Could not connect to Elasticsearch after several attempts.")
        return

    logger.info(f"Checking if index '{INDEX_NAME}' exists...")
    try:
        if es.indices.exists(index=INDEX_NAME):
            logger.info(f"Index {INDEX_NAME} already exists.")
            return

        settings = {
            "analysis": {
                "analyzer": {
                    "japanese_analyzer": {
                        "type": "custom",
                        "tokenizer": "kuromoji_tokenizer",
                    }
                }
            }
        }
        mappings = {
            "properties": {
                "title": {"type": "text", "analyzer": "japanese_analyzer"},
                "content": {"type": "text", "analyzer": "japanese_analyzer"},
                "url": {"type": "keyword"},
                "updated": {"type": "date"},
                "vectors": {"type": "rank_features"},
            }
        }

        es.indices.create(index=INDEX_NAME, settings=settings, mappings=mappings)
        logger.info(f"Index {INDEX_NAME} created successfully.")
    except Exception as e:
        logger.error(f"Error during index setup: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    setup_index()
