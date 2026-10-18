import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retrieve import retrieve as bm25_retrieve
from retrieve_embeddings import retrieve as embedding_retrieve
from retrieve_hybrid import retrieve as hybrid_retrieve


CHUNKS_FILE = ROOT / "data" / "processed" / "chunks.json"


class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chunks = json.loads(
            CHUNKS_FILE.read_text(encoding="utf-8")
        )
        cls.valid_chunk_ids = {
            chunk["chunk_id"] for chunk in cls.chunks
        }

    def test_each_retriever_returns_valid_chunks(self):
        methods = [
            bm25_retrieve,
            embedding_retrieve,
            hybrid_retrieve,
        ]

        question = "What platform can host a containerized AI application?"

        for retriever in methods:
            with self.subTest(retriever=retriever.__module__):
                results = retriever(question, top_k=3)

                self.assertGreater(len(results), 0)
                self.assertLessEqual(len(results), 3)

                for result in results:
                    self.assertIn(
                        result["chunk_id"],
                        self.valid_chunk_ids,
                    )

    def test_empty_query_is_rejected(self):
        methods = [
            bm25_retrieve,
            embedding_retrieve,
            hybrid_retrieve,
        ]

        for retriever in methods:
            with self.subTest(retriever=retriever.__module__):
                with self.assertRaises(ValueError):
                    retriever("   ")

    def test_invalid_top_k_is_rejected(self):
        methods = [
            bm25_retrieve,
            embedding_retrieve,
            hybrid_retrieve,
        ]

        for retriever in methods:
            with self.subTest(retriever=retriever.__module__):
                with self.assertRaises(ValueError):
                    retriever(
                        "What is retrieval?",
                        top_k=0,
                    )


if __name__ == "__main__":
    unittest.main()
