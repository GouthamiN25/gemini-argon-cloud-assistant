import json
from pathlib import Path

from retrieve import retrieve as bm25_retrieve
from retrieve_embeddings import retrieve as embedding_retrieve

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_FILE = ROOT / "data" / "processed" / "chunks.json"

RRF_K = 60


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Combine keyword and embedding rankings with Reciprocal Rank Fusion."""
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            "No chunks found. Run 'python src/ingest.py' first."
        )

    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))

    if not chunks:
        raise ValueError("The chunk file is empty.")

    # Retrieve every chunk so both methods contribute complete rankings.
    candidate_count = len(chunks)
    bm25_results = bm25_retrieve(query, top_k=candidate_count)
    embedding_results = embedding_retrieve(query, top_k=candidate_count)

    fused_scores = {}
    chunk_lookup = {}

    for ranking in (bm25_results, embedding_results):
        for rank, result in enumerate(ranking, start=1):
            chunk_id = result["chunk_id"]
            chunk_lookup[chunk_id] = result
            fused_scores[chunk_id] = (
                fused_scores.get(chunk_id, 0.0)
                + 1.0 / (RRF_K + rank)
            )

    ranked_ids = sorted(
        fused_scores,
        key=fused_scores.get,
        reverse=True,
    )

    results = []

    for chunk_id in ranked_ids[:top_k]:
        result = chunk_lookup[chunk_id].copy()
        result["rrf_score"] = round(fused_scores[chunk_id], 6)
        results.append(result)

    return results
