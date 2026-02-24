# Cosense RAG System

This project is a Retrieval-Augmented Generation (RAG) system for Cosense (Scrapbox) pages. It uses hybrid search (BM25 + SPLADE sparse vectors) with Elasticsearch and generates answers using Ollama with the Gemma3 model.

## Architecture

- **UI**: React + Vite frontend for search.
- **Search API**: FastAPI backend that coordinates search and LLM generation.
- **Encoder**: FastAPI service that generates SPLADE sparse vectors using Hugging Face models.
- **Batch Ingestion**: CLI tool to fetch pages from Cosense and index them into Elasticsearch.
- **Elasticsearch**: Vector-capable search engine.

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose.
- [Ollama](https://ollama.com/) installed on your host machine.

## Setup Instructions

### 1. Ollama and Gemma3

The system uses [Gemma 3](https://ollama.com/library/gemma3) for answer generation.

1.  **Install Ollama**: Download and install from [ollama.com](https://ollama.com/).
2.  **Pull the model**:
    ```bash
    ollama pull gemma3
    ```
3.  **Ensure Ollama is running**: The Search API connects to `http://host.docker.internal:11434` (mapped to `localhost:11434` on your host).

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
SCRAPBOX_PROJECT=your-project-name
SCRAPBOX_SID=your-connect.sid-cookie  # Required for private projects
ELASTICSEARCH_URL=http://elasticsearch:9200
ENCODER_URL=http://encoder:8001
OLLAMA_URL=http://host.docker.internal:11434
```

### 3. Start the Infrastructure

```bash
make up
```
This starts Elasticsearch, the Encoder, the Search API, and the UI.

### 4. Ingest Data

Run the batch ingestion script to index your Cosense pages:

```bash
make batch
```

## Usage

1. Open your browser to `http://localhost:3000`.
2. Enter a query related to your Cosense pages.
3. The system will retrieve relevant context and generate an answer using Gemma3.

## Maintenance

- **Linting**: `make lint`
- **Testing**: `make test`
- **Clean up**: `make down`