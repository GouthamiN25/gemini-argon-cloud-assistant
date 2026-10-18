import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from query import MIN_SIMILARITY, run_query


class QueryTests(unittest.TestCase):
    def test_low_similarity_query_abstains(self):
        results = [
            {
                "score": 0.1282,
                "source": "cloud_run_deployment.md",
                "chunk_id": "cloud_run_deployment.md::chunk-0",
                "text": "Cloud Run hosts containerized applications.",
            }
        ]

        output = StringIO()

        with patch("query.retrieve", return_value=results):
            with redirect_stdout(output):
                run_query("How do I bake a chocolate cake?")

        self.assertIn("don't have sufficiently similar", output.getvalue())
        self.assertNotIn("Retrieved evidence", output.getvalue())

    def test_high_similarity_query_returns_evidence(self):
        results = [
            {
                "score": 0.5855,
                "source": "cloud_run_deployment.md",
                "chunk_id": "cloud_run_deployment.md::chunk-0",
                "text": "Cloud Run hosts containerized applications.",
            }
        ]

        output = StringIO()

        with patch("query.retrieve", return_value=results):
            with redirect_stdout(output):
                run_query("What platform hosts containerized applications?")

        self.assertIn("Retrieved evidence", output.getvalue())
        self.assertIn("Cloud Run hosts containerized applications.", output.getvalue())

    def test_threshold_boundary_is_accepted(self):
        results = [
            {
                "score": MIN_SIMILARITY,
                "source": "example.md",
                "chunk_id": "example.md::chunk-0",
                "text": "Example evidence.",
            }
        ]

        output = StringIO()

        with patch("query.retrieve", return_value=results):
            with redirect_stdout(output):
                run_query("A test question")

        self.assertIn("Retrieved evidence", output.getvalue())

    def test_blank_query_does_not_call_retriever(self):
        output = StringIO()

        with patch("query.retrieve") as mock_retrieve:
            with redirect_stdout(output):
                run_query("   ")

        mock_retrieve.assert_not_called()
        self.assertIn("Please enter a question.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
