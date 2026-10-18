
import json
from pathlib import Path

from retrieve import retrieve

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_FILE = ROOT / "eval" / "questions.json"
REPORT_FILE = ROOT / "reports" / "retrieval_evaluation.md"

TOP_K = 3


def load_questions() -> list[dict]:
    """Load questions and manually labeled relevant chunk IDs."""
    questions = json.loads(
        QUESTIONS_FILE.read_text(encoding="utf-8")
    )

    if not questions:
        raise ValueError("Evaluation dataset is empty.")

    for item in questions:
        if not item.get("question", "").strip():
            raise ValueError("Every test case needs a question.")

        if not item.get("relevant_chunk_ids"):
            raise ValueError(
                f"Missing relevant chunk IDs: {item['question']}"
            )

    return questions


def evaluate(questions: list[dict], k: int = TOP_K) -> dict:
    """Calculate Hit Rate@k, Recall@k, and MRR."""
    if k < 1:
        raise ValueError("k must be at least 1.")

    hits = 0
    reciprocal_ranks = []
    recalls = []
    details = []

    for item in questions:
        expected = set(item["relevant_chunk_ids"])
        results = retrieve(item["question"], top_k=k)
        retrieved_ids = [result["chunk_id"] for result in results]

        relevant_ranks = [
            rank
            for rank, chunk_id in enumerate(retrieved_ids, start=1)
            if chunk_id in expected
        ]

        hit = bool(relevant_ranks)
        hits += int(hit)

        reciprocal_rank = (
            1 / relevant_ranks[0] if relevant_ranks else 0.0
        )
        recall = len(set(retrieved_ids) & expected) / len(expected)

        reciprocal_ranks.append(reciprocal_rank)
        recalls.append(recall)

        details.append({
            "question": item["question"],
            "expected": sorted(expected),
            "retrieved": retrieved_ids,
            "hit": hit,
            "recall": recall,
            "reciprocal_rank": reciprocal_rank,
        })

    count = len(questions)

    return {
        "k": k,
        "question_count": count,
        "hit_rate": hits / count,
        "mean_recall": sum(recalls) / count,
        "mrr": sum(reciprocal_ranks) / count,
        "details": details,
    }


def write_report(results: dict) -> None:
    """Save the metrics and per-question results as Markdown."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Retrieval Evaluation",
        "",
        f"- Questions evaluated: {results['question_count']}",
        f"- Ranking cutoff (k): {results['k']}",
        f"- Hit Rate@{results['k']}: {results['hit_rate']:.3f}",
        f"- Recall@{results['k']}: {results['mean_recall']:.3f}",
        f"- MRR: {results['mrr']:.3f}",
        "",
        "## Per-question results",
        "",
        "| Question | Hit | Recall | Reciprocal rank |",
        "|---|---:|---:|---:|",
    ]

    for item in results["details"]:
        question = item["question"].replace("|", "\\|")
        lines.append(
            f"| {question} | {item['hit']} "
            f"| {item['recall']:.3f} "
            f"| {item['reciprocal_rank']:.3f} |"
        )

    lines.extend(["", "## Retrieved passages", ""])

    for item in results["details"]:
        lines.extend([
            f"### {item['question']}",
            "",
            f"- Expected: {', '.join(item['expected'])}",
            f"- Retrieved: {', '.join(item['retrieved']) or 'None'}",
            "",
        ])

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nReport saved to: {REPORT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    results = evaluate(load_questions())
    write_report(results)
