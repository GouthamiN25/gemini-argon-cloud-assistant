from evaluate import load_questions
from retrieve import retrieve


def evaluate_at_k(questions: list[dict], k: int) -> dict:
    hits = 0
    recalls = []
    reciprocal_ranks = []

    for item in questions:
        expected = set(item["relevant_chunk_ids"])
        results = retrieve(item["question"], top_k=k)
        retrieved = [result["chunk_id"] for result in results]

        relevant_ranks = [
            rank
            for rank, chunk_id in enumerate(retrieved, start=1)
            if chunk_id in expected
        ]

        hits += int(bool(relevant_ranks))
        recalls.append(
            len(set(retrieved) & expected) / len(expected)
        )
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
    print("| Cutoff | Hit Rate@k | Mean Recall@k | MRR@k |")
    print("|---:|---:|---:|---:|")

    for k in (1, 3, 5):
        metrics = evaluate_at_k(questions, k)
        print(
            f"| {k} "
            f"| {metrics['hit_rate']:.3f} "
            f"| {metrics['mean_recall']:.3f} "
            f"| {metrics['mrr']:.3f} |"
        )
