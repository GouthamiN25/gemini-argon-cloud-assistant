
import json
import re
import sys
from pathlib import Path

from rank_bm25 import BM25L

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_FILE = ROOT / "data" / "processed" / "chunks.json"
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "does", "for",
    "from", "how", "in", "is", "it", "of", "on", "or", "the", "to",
    "today", "what", "with",
}


def tokenize(text: str) -> list[str]:
    """Normalize text and remove common words that do not aid retrieval."""
    return [
        token
        for token in re.findall(r"\b[a-z0-9_]+\b", text.lower())
        if token not in STOP_WORDS
    ]


def load_chunks() -> list[dict]:
    """Load the chunks produced by ingest.py."""
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            "No chunks found. Run 'python src/ingest.py' first."
        )

    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))

    if not chunks:
        raise ValueError(
            "The chunk file is empty. Add documents to data/raw/ "
            "and rerun ingestion."
        )

    return chunks


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Return the highest-scoring document chunks for a query."""
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    chunks = load_chunks()
    tokenized_docs = [tokenize(chunk["text"]) for chunk in chunks]
    tokenized_query = tokenize(query)

    if not tokenized_query:
        return []

    # BM25L keeps IDF values positive even in a very small corpus.  Standard
    # BM25Okapi can assign negative scores when a term appears in every
    # document (including the one-document corpus used by this project).
    bm25 = BM25L(tokenized_docs)
    scores = bm25.get_scores(tokenized_query)

    ranked_indices = sorted(
        range(len(chunks)),
        key=lambda index: scores[index],
        reverse=True,
    )

    results = []

    for index in ranked_indices:
        score = float(scores[index])

        # Do not return unrelated passages with no lexical match.
        if score <= 0:
            continue

        result = chunks[index].copy()
        result["score"] = round(score, 4)
        results.append(result)

        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    query = " ".join(sys.argv[1:])

    if not query:
        query = input("Ask a question: ")

    try:
        results = retrieve(query)

        if not results:
            print("No relevant passages found.")
        else:
            for rank, result in enumerate(results, start=1):
                print(f"\n--- Result {rank} ---")
                print(f"Score: {result['score']}")
                print(f"Source: {result['source']}")
                print(f"Chunk: {result['chunk_id']}")
                print(result["text"])

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)
