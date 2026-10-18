import json
from pathlib import Path

from query import MIN_SIMILARITY
from retrieve_embeddings import retrieve


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_FILE = PROJECT_ROOT / "eval" / "abstention_questions.json"


def main() -> None:
    with QUESTIONS_FILE.open(encoding="utf-8") as file:
        questions = json.load(file)

    out_of_scope = [
        item for item in questions
        if item["category"] == "out_of_scope"
    ]
    false_acceptances = 0
    correct_abstentions = 0

    print(f"Similarity threshold: {MIN_SIMILARITY:.2f}\n")

    for item in questions:
        results = retrieve(item["question"], top_k=1)

        if not results:
            raise RuntimeError(
                f"No retrieval results for: {item['question']}"
            )

        score = results[0]["score"]
        prediction = (
            "ACCEPT" if score >= MIN_SIMILARITY else "ABSTAIN"
        )

        print(f"Category:   {item['category']}")
        print(f"Question:   {item['question']}")
        print(f"Top score:  {score:.4f}")
        print(f"Prediction: {prediction}\n")

        if item["category"] == "out_of_scope":
            if prediction == "ABSTAIN":
                correct_abstentions += 1
            else:
                false_acceptances += 1

    total = len(out_of_scope)

    print("--- Out-of-scope evaluation ---")
    print(f"Questions:             {total}")
    print(f"Correct abstentions:   {correct_abstentions}")
    print(f"False acceptances:     {false_acceptances}")

    if total:
        print(
            f"Out-of-scope rejection rate: "
            f"{correct_abstentions / total:.1%}"
        )

    print(
        "\nNote: This is a small, manually selected probe set. "
        "It does not establish production reliability."
    )


if __name__ == "__main__":
    main()
