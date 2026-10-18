from evaluate import load_questions
from retrieve import retrieve as bm25_retrieve
from retrieve_embeddings import retrieve as embedding_retrieve
from retrieve_hybrid import retrieve as hybrid_retrieve


def evaluate_retriever(retriever, questions, k):
    hits = 0
    recalls = []
    reciprocal_ranks = []

    for item in questions:
        expected = set(item["relevant_chunk_ids"])
        results = retriever(item["question"], top_k=k)
        retrieved = [result["chunk_id"] for result in results]

        relevant_ranks = [
            rank
            for rank, chunk_id in enumerate(retrieved, start=1)
            if chunk_id in expected
        ]

        hits += int(bool(relevant_ranks))
        recalls.append(len(set(retrieved) & expected) / len(expected))
        reciprocal_ranks.append(
            1 / relevant_ranks[0] if relevant_ranks else 0.0
        )

    count = len(questions)

    return {
        "hit_rate": hits / count,
        "mean_recall": sum(recalls) / count,
        "mrr": sum(reciprocal_ranks) / count,
    }


if __name__ == "__main__":
    questions = load_questions()

    print(f"Questions evaluated: {len(questions)}")
    print()
    print("| Method | Cutoff | Hit Rate@k | Mean Recall@k | MRR@k |")
    print("|---|---:|---:|---:|---:|")

    methods = [
        ("BM25L", bm25_retrieve),
        ("Embeddings", embedding_retrieve),
        ("Hybrid RRF", hybrid_retrieve),
    ]

    for method_name, retriever in methods:
        for k in (1, 3, 5):
            metrics = evaluate_retriever(retriever, questions, k)

            print(
                f"| {method_name} | {k} "
                f"| {metrics['hit_rate']:.3f} "
                f"| {metrics['mean_recall']:.3f} "
                f"| {metrics['mrr']:.3f} |"
            )
