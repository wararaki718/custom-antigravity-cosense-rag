---
name: cosense-ingestion
description: "Instructions for fetching data from Cosense (Scrapbox) API."
---

# Cosense Ingestion Skill

## Goal
Fetch pages and their content from a specific Cosense project for indexing into Elasticsearch.

## API Usage
- **Endpoint**: `https://scrapbox.io/api/pages/{project_name}`
- **Page Detail**: `https://scrapbox.io/api/pages/{project_name}/{page_title}`
- **Authentication**: Authentication may be required for private projects via `connect.sid` cookie.

## Inter-service Communication
- The `batch` service should call the `encoder` service's `/encode` endpoint to get sparse vectors for each page's content before indexing to Elasticsearch.

## Implementation Steps
1. Fetch pages from Cosense API.
2. For each page:
    a. Prepare text for encoding.
    b. Call `encoder` API: `POST http://encoder:8001/encode`.
    c. Transform response into Elasticsearch compatible `rank_features`.
    d. Index doc into Elasticsearch.

## Best Practices
- Respect rate limits.
- Cache fetched data to avoid redundant API calls.
- Handle deleted pages or updates by checking the `updated` timestamp.
