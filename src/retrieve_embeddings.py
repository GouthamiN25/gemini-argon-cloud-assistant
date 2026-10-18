import json
import sys
from functools import lru_cache
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_FILE = ROOT / "data" / "processed" / "chunks.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_index():
    """Load the model and encode documents once per process."""
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            "No chunks found. Run 'python src/ingest.py' first."
        )

    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))

    if not chunks:
        raise ValueError("The chunk file is empty.")

    model = SentenceTransformer(MODEL_NAME)
    documents = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        documents,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return chunks, model, embeddings


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Rank chunks by cosine similarity between embeddings."""
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    chunks, model, document_embeddings = load_index()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    scores = cosine_similarity(
        query_embedding, document_embeddings
    )[0]

    ranked_indices = scores.argsort()[::-1][:top_k]

    results = []

    for index in ranked_indices:
        result = chunks[int(index)].copy()
        result["score"] = round(float(scores[index]), 4)
        results.append(result)

    return results


if __name__ == "__main__":
    query = " ".join(sys.argv[1:])

    if not query:
        query = input("Ask a question: ")

    try:
        results = retrieve(query)

        for rank, result in enumerate(results, start=1):
            print(f"\n--- Result {rank} ---")
            print(f"Similarity: {result['score']}")
            print(f"Source: {result['source']}")
            print(f"Chunk: {result['chunk_id']}")
            print(result["text"])

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)
