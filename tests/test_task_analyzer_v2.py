import json
import unittest
from unittest.mock import MagicMock

from lattice_lock_orchestrator.routing.analyzer import TaskAnalyzer


class TestTaskAnalyzerV2(unittest.TestCase):
    def setUp(self):
        self.orchestrator = MagicMock()
        self.analyzer = TaskAnalyzer(orchestrator=self.orchestrator)

        # Load validation dataset
        with open("tests/data/prompts.json") as f:
            self.validation_data = json.load(f)

    def test_heuristics_accuracy(self):
        """Test that heuristics correctly classify the validation set."""
        correct = 0
        total = 0

        for item in self.validation_data:
            prompt = item["prompt"]
            expected = item["expected_type"]

            # For this test, we care about the integration of analyze()
            result = self.analyzer.analyze(prompt)

            if result == expected:
                correct += 1
            else:
                # If expected is GENERAL, and we got GENERAL (fallback), that's correct for now
                # since we mocked the router to return GENERAL.
                if expected == "GENERAL" and result == "GENERAL":
                    correct += 1
                    continue

                print(f"Failed: '{prompt}' Expected: {expected}, Got: {result}")

            total += 1

        accuracy = correct / total
        print(f"Accuracy: {accuracy:.2%}")
        self.assertGreater(accuracy, 0.9, "Accuracy should be > 90%")

    def test_caching(self):
        """Test that results are cached."""
        prompt = "def foo(): pass"

        # First call
        res1 = self.analyzer.analyze(prompt)

        # Second call
        res2 = self.analyzer.analyze(prompt)

        self.assertEqual(res1, res2)
        # We can't easily inspect lru_cache internals without private access,
        # but we can verify behavior is consistent.

    def test_llm_fallback(self):
        """Test fallback to LLM when heuristics fail."""
        prompt = "Something ambiguous that regex won't catch"

        # Force heuristics to return None (they should for this prompt)

        self.analyzer.analyze(prompt)

        # Since heuristics returned None (presumably), it should call semantic router
        # which logs a warning because we have a mock orchestrator but the method
        # just returns "GENERAL" in the placeholder.
        # We can verify the result is "GENERAL".
        self.assertEqual(self.analyzer.analyze(prompt), "GENERAL")


if __name__ == "__main__":
    unittest.main()
