"""
Embedding and retrieval for the Campus Dining Unofficial Guide.

Spec source: planning.md — Retrieval Approach section.
  model:       all-MiniLM-L6-v2 (sentence-transformers, local, no API key)
  vector store: ChromaDB (persistent local collection)
  distance:    cosine
  top-k:       3

Usage:
    python embed.py          # embed all chunks from documents/chunks.json
    python embed.py --test   # run retrieval tests against 3 eval-plan queries
"""

import argparse
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = Path("documents/chunks.json")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "dining_guide"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 3

# ---------------------------------------------------------------------------
# Embed and store
# ---------------------------------------------------------------------------

def load_chunks():
    with open(CHUNKS_PATH, encoding="utf-8") as f:
        return json.load(f)


def embed_and_store(chunks):
    """Embed all chunks and store in a local ChromaDB collection."""
    model = SentenceTransformer(EMBED_MODEL)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Drop existing collection so re-runs don't accumulate duplicates
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    # cosine distance: 0.0 = identical, 1.0 = orthogonal
    # The milestone guideline (>0.6 = weak match) is calibrated for cosine.
    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c["text"] for c in chunks]
    metadatas = [{"source_url": c["source_url"]} for c in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    print(f"Embedding {len(chunks)} chunks with {EMBED_MODEL}...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    collection.add(
        documents=texts,
        embeddings=[e.tolist() for e in embeddings],
        metadatas=metadatas,
        ids=ids,
    )

    print(f"\nStored {collection.count()} chunks in ChromaDB at {CHROMA_DIR}/")
    return collection


# ---------------------------------------------------------------------------
# Retrieval — lazy singletons so the model loads once per process,
# not once per query (avoids 3-5s startup overhead in the Gradio app)
# ---------------------------------------------------------------------------

_model = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query: str, k: int = TOP_K):
    """
    Embed a query and return the top-k most similar chunks.

    Returns a list of dicts: {text, source_url, distance}
    Distance is cosine distance (lower = more similar).
    """
    query_embedding = _get_model().encode([query])[0].tolist()
    results = _get_collection().query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": doc,
            "source_url": meta["source_url"],
            "distance": dist,
        })
    return chunks


# ---------------------------------------------------------------------------
# Retrieval tests — 3 of the 5 eval-plan queries (sources confirmed fetched)
# ---------------------------------------------------------------------------

TEST_QUERIES = [
    # Eval Q1 — Cornell Daily Sun article is in the corpus
    "What dining hall does the Cornell Daily Sun name as Cornell's best?",
    # Eval Q2 — Miami Hurricane article is in the corpus
    "What do University of Miami students say about vegan options on campus?",
    # Eval Q4 — Harvard Crimson HUDS menu article is in the corpus
    "How do Harvard students describe the food quality changes after HUDS updated its menu?",
]


def run_tests():
    print("\n" + "=" * 64)
    print("RETRIEVAL TEST — 3 eval-plan queries")
    print("Threshold: distance < 0.5 = good match, > 0.6 = weak match")
    print("=" * 64)

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 64)
        results = retrieve(query)
        for j, chunk in enumerate(results, 1):
            source = chunk["source_url"].split("//")[-1].split("/")[0]
            flag = "  OK " if chunk["distance"] < 0.5 else "WEAK "
            print(f"  [{j}] dist={chunk['distance']:.4f} {flag}| {source}")
            print(f"       {chunk['text'][:180]}{'...' if len(chunk['text']) > 180 else ''}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true",
                        help="Run retrieval tests instead of embedding")
    args = parser.parse_args()

    if args.test:
        run_tests()
    else:
        chunks = load_chunks()
        embed_and_store(chunks)
        print("\nRun `python embed.py --test` to validate retrieval quality.")
