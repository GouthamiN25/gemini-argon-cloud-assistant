import sys

from retrieve_embeddings import retrieve

MIN_SIMILARITY = 0.20
TOP_K = 3


def run_query(query: str) -> None:
    if not query.strip():
        print("Please enter a question.")
        return

    results = retrieve(query, top_k=TOP_K)
    top_score = results[0]["score"]

    print(f"Top similarity: {top_score:.4f}")

    if top_score < MIN_SIMILARITY:
        print(
            "\nI don't have sufficiently similar information "
            "in the current document collection to support this query."
        )
        return

    print("\nRetrieved evidence (not a generated answer):")

    for rank, result in enumerate(results, start=1):
        print(f"\n--- Result {rank} ---")
        print(f"Similarity: {result['score']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Chunk: {result['chunk_id']}")
        print(result["text"])


if __name__ == "__main__":
    query = " ".join(sys.argv[1:])

    if not query:
        query = input("Ask a question: ")

    try:
        run_query(query)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)
