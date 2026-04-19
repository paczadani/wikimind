# WikiMind

A RAG (Retrieval-Augmented Generation) assistant that answers questions based on Wikipedia articles. A Python/FastAPI service handles document retrieval and LLM inference via Ollama, and a Spring Boot service acts as a REST gateway.

## Architecture

```
Browser → Streamlit (8501) → Spring Boot (8080) → Python FastAPI (8000) → ChromaDB + Ollama
```

- **streamlit-service** — simple web UI for asking questions and viewing answers with sources
- **springboot-service** — Spring Boot REST gateway that proxies questions to the Python service
- **python-service** — ingests Wikipedia articles into ChromaDB, retrieves relevant chunks, and generates answers using a local LLM via Ollama
- **ollama** — runs the LLM locally (default: `llama3.2`)

## Getting Started

### Prerequisites

- Docker & Docker Compose

### 1. Ingest Wikipedia data

Before running the app, populate the ChromaDB vector store. By default it ingests 5 AI/ML topics, but you can customise them:

```bash
# Default topics
docker-compose run --rm python-service python ingest.py

# Custom topics via CLI args
docker-compose run --rm python-service python ingest.py "Quantum computing" "Large language model"

# Custom topics via env var
TOPICS="Quantum computing,Large language model" docker-compose run --rm python-service python ingest.py
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

The Spring Boot gateway will be available at `http://localhost:8080` and the Streamlit UI at `http://localhost:8501`.

> **Note:** On first start, Ollama will pull the `llama3.2` model which may take a few minutes.

## API

### Ask a question

**POST** `http://localhost:8080/ask`

```json
{
  "question": "What is a transformer model?"
}
```

**Response:**

```json
{
  "answer": "A transformer model is...",
  "sources": [
    "https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)"
  ]
}
```

### Health check

**GET** `http://localhost:8080/health`

```json
{
  "status": "ok",
  "db_loaded": true,
  "chunk_count": 342
}
```

## Configuration

Environment variables (set in `docker-compose.yml`):

| Variable | Default | Description |
|---|---|---|
| `TOPICS` | *(see defaults)* | Comma-separated Wikipedia topics to ingest (also accepts CLI args) |
| `OLLAMA_MODEL` | `llama3.2` | LLM model to use |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama service URL |
| `TOP_K` | `4` | Number of document chunks retrieved per query |
| `PYTHON_SERVICE_BASE_URL` | `http://python-service:8000` | Python service URL (Spring Boot) |

## Tech Stack

- Python 3.11, FastAPI, ChromaDB, sentence-transformers, Ollama
- Streamlit (web UI)
- Java 17, Spring Boot 3.2
- Docker Compose
