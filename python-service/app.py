import os
import time
import logging
import requests
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import chromadb
from chromadb.utils import embedding_functions

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "wiki_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
TOP_K = int(os.getenv("TOP_K", "4"))

collection = None
ef = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global collection, ef
    if not os.path.exists(CHROMA_PATH):
        logger.warning("chroma_db/ not found. Run ingest.py first.")
    else:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
            logger.info(f"Loaded collection '{COLLECTION_NAME}' with {collection.count()} chunks")
        except Exception as e:
            logger.warning(f"Collection '{COLLECTION_NAME}' not found: {e}. Run ingest.py first.")
    yield


app = FastAPI(title="RAG Document Assistant", version="1.0.0", lifespan=lifespan)


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, description="The question to answer")


class RagResponse(BaseModel):
    answer: str
    sources: list[str]


class HealthResponse(BaseModel):
    status: str
    db_loaded: bool
    chunk_count: int


def retrieve_context(question: str) -> tuple[str, list[str]]:
    t0 = time.time()
    results = collection.query(
        query_texts=[question],
        n_results=TOP_K,
        include=["documents", "metadatas"],
    )
    elapsed_ms = (time.time() - t0) * 1000
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    sources = list({m["source"] for m in metas})
    logger.info(f"Retrieved {len(docs)} chunks in {elapsed_ms:.1f}ms for: {question!r}")
    context = "\n\n".join(docs)
    return context, sources


def call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["response"]
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Ollama unreachable: {e}")


@app.post("/ask-rag", response_model=RagResponse)
def ask_rag(req: QuestionRequest):
    if collection is None:
        raise HTTPException(status_code=503, detail="ChromaDB not loaded. Run ingest.py first.")
    context, sources = retrieve_context(req.question)
    prompt = (
        "You are a helpful assistant. Use ONLY the context below to answer the question. "
        "If the context does not contain enough information, say so.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {req.question}\n\n"
        "Answer:"
    )
    answer = call_ollama(prompt)
    return RagResponse(answer=answer.strip(), sources=sources)


@app.get("/health", response_model=HealthResponse)
def health():
    db_loaded = collection is not None
    count = collection.count() if db_loaded else 0
    return HealthResponse(status="ok", db_loaded=db_loaded, chunk_count=count)
