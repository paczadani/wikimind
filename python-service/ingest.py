import os
import time
import wikipedia
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "wiki_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"

TOPICS = [
    "Artificial intelligence",
    "Machine learning",
    "Neural network",
    "Natural language processing",
    "Transformer (machine learning model)",
]
MIN_PARAGRAPH_LEN = 100


def fetch_paragraphs(title: str) -> list[dict]:
    try:
        page = wikipedia.page(title, auto_suggest=False)
    except wikipedia.exceptions.DisambiguationError as e:
        page = wikipedia.page(e.options[0], auto_suggest=False)
    except wikipedia.exceptions.PageError:
        print(f"  Page not found: {title}")
        return []

    paragraphs = []
    for para in page.content.split("\n"):
        para = para.strip()
        if len(para) >= MIN_PARAGRAPH_LEN:
            paragraphs.append({"text": para, "source": page.url})
    return paragraphs


def main():
    print(f"Initialising ChromaDB at {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    all_docs, all_ids, all_metas = [], [], []
    doc_id = 0

    for topic in TOPICS:
        print(f"Fetching: {topic}")
        paras = fetch_paragraphs(topic)
        print(f"  {len(paras)} paragraphs")
        for p in paras:
            all_docs.append(p["text"])
            all_ids.append(f"doc_{doc_id}")
            all_metas.append({"source": p["source"], "topic": topic})
            doc_id += 1

    print(f"\nEmbedding and storing {len(all_docs)} chunks ...")
    t0 = time.time()
    BATCH = 500
    for i in range(0, len(all_docs), BATCH):
        collection.add(
            documents=all_docs[i:i + BATCH],
            ids=all_ids[i:i + BATCH],
            metadatas=all_metas[i:i + BATCH],
        )
    elapsed = time.time() - t0
    print(f"Done. {len(all_docs)} chunks stored in {elapsed:.1f}s")
    print(f"ChromaDB persisted to {CHROMA_PATH}")


if __name__ == "__main__":
    main()
