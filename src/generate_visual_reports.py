import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from compare_retrievers import evaluate_retriever
from evaluate import load_questions
from query import MIN_SIMILARITY
from retrieve import retrieve as bm25_retrieve
from retrieve_embeddings import retrieve as embedding_retrieve
from retrieve_hybrid import retrieve as hybrid_retrieve

REPORTS = ROOT / "reports"
METHODS = [
    ("BM25L", bm25_retrieve),
    ("Embeddings", embedding_retrieve),
    ("Hybrid RRF", hybrid_retrieve),
]


def save_svg(path, title, labels, values, max_value=1.0,
             threshold=None, colors=None, value_label="Score"):
    width, height = 1050, 520
    left, right, top, bottom = 90, 35, 75, 135
    plot_w = width - left - right
    plot_h = height - top - bottom
    colors = colors or ["#4776B4"] * len(values)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="35" text-anchor="middle" '
        f'font-family="Arial" font-size="22" font-weight="bold">'
        f'{html.escape(title)}</text>',
    ]

    for tick in range(6):
        value = max_value * tick / 5
        y = top + plot_h * (1 - value / max_value)
        parts.append(
            f'<line x1="{left}" y1="{y}" x2="{width-right}" y2="{y}" '
            'stroke="#dddddd"/>'
        )
        parts.append(
            f'<text x="{left-12}" y="{y+5}" text-anchor="end" '
            f'font-family="Arial" font-size="13">{value:.2f}</text>'
        )

    if threshold is not None:
        y = top + plot_h * (1 - threshold / max_value)
        parts.extend([
            f'<line x1="{left}" y1="{y}" x2="{width-right}" y2="{y}" '
            'stroke="#c2410c" stroke-width="2" stroke-dasharray="7 5"/>',
            f'<text x="{width-right-5}" y="{y-8}" text-anchor="end" '
            'font-family="Arial" font-size="13" fill="#c2410c">'
            f'Threshold {threshold:.2f}</text>',
        ])

    slot = plot_w / len(values)
    bar_w = min(65, slot * 0.55)

    for i, (label, value) in enumerate(zip(labels, values)):
        x = left + i * slot + (slot - bar_w) / 2
        bar_h = max(0, plot_h * value / max_value)
        y = top + plot_h - bar_h
        parts.extend([
            f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" '
            f'fill="{colors[i]}"/>',
            f'<text x="{x+bar_w/2}" y="{y-8}" text-anchor="middle" '
            f'font-family="Arial" font-size="13">{value:.3f}</text>',
            f'<text transform="translate({x+bar_w/2},{top+plot_h+18}) '
            f'rotate(35)" text-anchor="start" font-family="Arial" '
            f'font-size="12">{html.escape(label)}</text>',
        ])

    parts.append(
        f'<text transform="translate(25,{top+plot_h/2}) rotate(-90)" '
        f'text-anchor="middle" font-family="Arial" font-size="14">'
        f'{html.escape(value_label)}</text>'
    )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main():
    REPORTS.mkdir(exist_ok=True)
    questions = load_questions()

    # Recompute retrieval comparison metrics from the labeled benchmark.
    rows = []
    for name, retriever in METHODS:
        for k in (1, 3, 5):
            metrics = evaluate_retriever(retriever, questions, k)
            rows.append((name, k, metrics))

    lines = [
        "# Retrieval Comparison",
        "",
        f"Questions evaluated: **{len(questions)}**",
        "",
        "Metrics are calculated from manually labeled relevant chunk IDs.",
        "",
        "| Method | k | Hit Rate@k | Mean Recall@k | MRR@k |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, k, m in rows:
        lines.append(
            f"| {name} | {k} | {m['hit_rate']:.3f} "
            f"| {m['mean_recall']:.3f} | {m['mrr']:.3f} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "Hybrid RRF ranked relevant evidence well on this small benchmark. "
        "These results do not establish that it will outperform other "
        "methods on unseen questions.",
        "",
    ])
    (REPORTS / "retrieval_comparison.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    # Plot MRR at each cutoff for all three retrieval methods.
    cutoffs = [1, 3, 5]
    series = {}
    for name, k, m in rows:
        series.setdefault(name, []).append(m["mrr"])

    # One bar per method/cutoff keeps this plot dependency-free.
    labels = [f"{name} k={k}" for name, k, _ in rows]
    values = [m["mrr"] for _, _, m in rows]
    colors = [
        {"BM25L": "#64748b", "Embeddings": "#2563eb",
         "Hybrid RRF": "#0f766e"}[name]
        for name, _, _ in rows
    ]
    save_svg(
        REPORTS / "retrieval_comparison.svg",
        "Retrieval ranking quality: MRR by method and cutoff",
        labels, values, colors=colors, value_label="MRR",
    )

    # Recompute the actual abstention probe results.
    import json
    probes = json.loads(
        (ROOT / "eval" / "abstention_questions.json").read_text(
            encoding="utf-8"
        )
    )
    details = []
    for item in probes:
        result = embedding_retrieve(item["question"], top_k=1)[0]
        score = result["score"]
        prediction = "ACCEPT" if score >= MIN_SIMILARITY else "ABSTAIN"
        details.append({
            "category": item["category"],
            "question": item["question"],
            "score": score,
            "prediction": prediction,
            "chunk_id": result["chunk_id"],
            "source": result["source"],
        })

    out_of_scope = [d for d in details if d["category"] == "out_of_scope"]
    correct = sum(d["prediction"] == "ABSTAIN" for d in out_of_scope)
    false_accepts = len(out_of_scope) - correct

    lines = [
        "# Abstention Evaluation",
        "",
        f"- Similarity threshold: **{MIN_SIMILARITY:.2f}**",
        f"- Out-of-scope questions: **{len(out_of_scope)}**",
        f"- Correct abstentions: **{correct}**",
        f"- False acceptances: **{false_accepts}**",
        f"- Out-of-scope rejection rate: **{correct / len(out_of_scope):.1%}**",
        "",
        "## Per-question results",
        "",
        "| Category | Question | Top similarity | Prediction | Top source | Chunk |",
        "|---|---|---:|---|---|---|",
    ]
    for d in details:
        question = d["question"].replace("|", "\\|")
        lines.append(
            f"| {d['category']} | {question} | {d['score']:.4f} "
            f"| {d['prediction']} | {d['source']} | {d['chunk_id']} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "The BigQuery pricing question may score highly because it is "
        "semantically related to Google Cloud content. Acceptance means "
        "only that its similarity score passed the threshold; it does not "
        "prove the documents contain current pricing information.",
        "",
        "This is a small, manually selected probe set, not a production "
        "reliability estimate. Similarity is not calibrated confidence.",
        "",
    ])
    (REPORTS / "abstention_evaluation.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    score_colors = []
    for d in details:
        if d["category"] == "out_of_scope" and d["prediction"] == "ACCEPT":
            score_colors.append("#dc2626")  # False acceptance
        elif d["prediction"] == "ABSTAIN":
            score_colors.append("#0f766e")
        else:
            score_colors.append("#2563eb")

    labels = [
        "Cake", "World Series", "BigQuery price",
        "Weather", "Cloud Run cost", "IAM roles",
    ]
    save_svg(
        REPORTS / "abstention_scores.svg",
        "Question similarity scores vs. abstention threshold",
        labels, [d["score"] for d in details],
        max_value=max(0.7, MIN_SIMILARITY),
        threshold=MIN_SIMILARITY,
        colors=score_colors,
        value_label="Cosine similarity",
    )

    print("Saved reports:")
    for name in (
        "retrieval_comparison.md",
        "retrieval_comparison.svg",
        "abstention_evaluation.md",
        "abstention_scores.svg",
    ):
        print(f"  reports/{name}")
    print(f"\nOut-of-scope rejection rate: {correct}/{len(out_of_scope)}")
    print("No new Python dependencies were added.")


if __name__ == "__main__":
    main()
