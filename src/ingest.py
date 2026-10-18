
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_FILE = ROOT / "data" / "processed" / "chunks.json"

SUPPORTED_EXTENSIONS = {".md", ".txt"}
MAX_CHARS = 1200


def split_into_chunks(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Group paragraphs into chunks without splitting them unnecessarily."""
    paragraphs = [
        re.sub(r"\s+", " ", p).strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        # Split unusually long paragraphs into smaller pieces.
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""

            for start in range(0, len(paragraph), max_chars):
                chunks.append(paragraph[start:start + max_chars])
            continue

        candidate = f"{current}\n\n{paragraph}" if current else paragraph

        if len(candidate) > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


def ingest_documents() -> list[dict]:
    """Read local documents and create searchable chunks."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(
        path
        for path in RAW_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    records = []

    for file_path in files:
        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        relative_source = file_path.relative_to(RAW_DIR).as_posix()
        title = file_path.stem.replace("_", " ").replace("-", " ").title()

        for index, chunk in enumerate(split_into_chunks(text)):
            records.append({
                "chunk_id": f"{relative_source}::chunk-{index}",
                "source": relative_source,
                "title": title,
                "chunk_index": index,
                "text": chunk,
            })

    OUTPUT_FILE.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Documents processed: {len(files)}")
    print(f"Chunks created: {len(records)}")
    print(f"Output written to: {OUTPUT_FILE.relative_to(ROOT)}")

    return records


if __name__ == "__main__":
    ingest_documents()
