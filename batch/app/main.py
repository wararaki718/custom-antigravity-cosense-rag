import os
import time
import urllib.parse

import httpx
from dotenv import load_dotenv
from tqdm import tqdm

from elasticsearch import Elasticsearch, helpers

try:
    from .logger import logger
    from .setup_index import INDEX_NAME, setup_index
except ImportError:
    from logger import logger
    from setup_index import INDEX_NAME, setup_index

load_dotenv()

# Configuration
COSENSE_PROJECT = os.getenv("COSENSE_PROJECT")
COSENSE_SID = os.getenv("COSENSE_SID")  # connect.sid cookie for private projects
ENCODER_URL = os.getenv("ENCODER_URL", "http://localhost:8001")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

if not COSENSE_PROJECT:
    logger.warning("COSENSE_PROJECT is not set. Ingestion will fail.")

client = httpx.Client(timeout=30.0)
es = Elasticsearch(ELASTICSEARCH_URL)


def wait_for_encoder():
    """Wait for the encoder service to be ready."""
    logger.info(f"Waiting for encoder at {ENCODER_URL}...")
    for i in range(30):
        try:
            response = client.get(f"{ENCODER_URL}/health")
            if response.status_code == 200:
                logger.info("Encoder is ready!")
                return True
        except Exception as e:
            logger.warning(f"Encoder not ready yet (attempt {i+1}/30): {e}")
        time.sleep(5)
    logger.error("Encoder service timed out.")
    return False


def fetch_pages():
    """Fetch all page titles from the Cosense project."""
    url = f"https://scrapbox.io/api/pages/{COSENSE_PROJECT}"
    headers = {}
    if COSENSE_SID:
        headers["Cookie"] = f"connect.sid={COSENSE_SID}"

    all_pages = []
    skip = 0
    limit = 100

    while True:
        params = {"skip": skip, "limit": limit}
        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        pages = data.get("pages", [])
        if not pages:
            break
        all_pages.extend(pages)
        skip += limit
        if skip >= data.get("count", 0):
            break
        time.sleep(1)  # Rate limiting

    return all_pages


def fetch_page_detail(title):
    """Fetch the full content of a specific page."""
    encoded_title = urllib.parse.quote(title, safe="")
    url = f"https://scrapbox.io/api/pages/{COSENSE_PROJECT}/{encoded_title}"
    headers = {}
    if COSENSE_SID:
        headers["Cookie"] = f"connect.sid={COSENSE_SID}"

    response = client.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_vector(text):
    """Call the encoder service to get the SPLADE vector."""
    try:
        response = client.post(f"{ENCODER_URL}/encode", json={"text": text})
        response.raise_for_status()
        return response.json()["vectors"]
    except Exception as e:
        logger.error(f"Error encoding text: {e}")
        return {}


def run_ingestion():
    if not COSENSE_PROJECT:
        logger.error("COSENSE_PROJECT is not set.")
        return

    logger.info("Setting up index...")
    setup_index()

    if not wait_for_encoder():
        logger.error("Aborting ingestion: encoder not ready.")
        return

    logger.info(f"Fetching pages for project: {COSENSE_PROJECT}")
    pages = fetch_pages()
    total_pages = len(pages)
    logger.info(f"Found {total_pages} pages.")

    actions = []
    processed_count = 0
    for page in tqdm(pages, desc="Ingesting pages"):
        try:
            title = page["title"]
            detail = fetch_page_detail(title)

            # Combine lines for content
            content = "\n".join([line["text"] for line in detail.get("lines", [])])

            # Get SPLADE vector
            vectors = get_vector(content)

            doc = {
                "_index": INDEX_NAME,
                "_id": page["id"],
                "title": title,
                "content": content,
                "url": f"https://scrapbox.io/{COSENSE_PROJECT}/{title}",
                "updated": detail.get("updated"),
                "vectors": vectors,
            }
            actions.append(doc)
            processed_count += 1

            # Periodic progress logging
            if processed_count % 10 == 0:
                logger.info(f"Processed {processed_count}/{total_pages} pages...")

            # Bulk index every 50 docs
            if len(actions) >= 50:
                helpers.bulk(es, actions)
                actions = []

            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            logger.error(f"Error processing page {page.get('title')}: {e}")

    if actions:
        helpers.bulk(es, actions)

    logger.info("Ingestion complete.")


if __name__ == "__main__":
    run_ingestion()
