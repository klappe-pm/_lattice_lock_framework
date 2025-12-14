"""Unit tests for the Feedback System."""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from lattice_lock.feedback.collector import FeedbackCollector

class TestFeedbackCollector(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.feedback_file = Path(self.test_dir) / "feedback.json"
        self.collector = FeedbackCollector(storage_path=str(self.feedback_file))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_initialization_creates_file(self):
        """Test that storage file is created on init."""
        self.assertTrue(self.feedback_file.exists())
        with open(self.feedback_file) as f:
            data = json.load(f)
            self.assertEqual(data, [])

    def test_submit_feedback(self):
        """Test submitting feedback."""
        entry = self.collector.submit_feedback(5, "Great tool!", "feature")
        
        self.assertEqual(entry["rating"], 5)
        self.assertEqual(entry["comment"], "Great tool!")
        self.assertEqual(entry["category"], "feature")
        self.assertIn("id", entry)
        self.assertIn("timestamp", entry)
        
        # Verify persistence
        with open(self.feedback_file) as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["id"], entry["id"])

    def test_invalid_rating(self):
        """Test that invalid ratings raise ValueError."""
        with self.assertRaises(ValueError):
            self.collector.submit_feedback(6, "Too good")
        
        with self.assertRaises(ValueError):
            self.collector.submit_feedback(0, "Too bad")

    def test_get_summary(self):
        """Test summary statistics."""
        self.collector.submit_feedback(5, "Good", "general")
        self.collector.submit_feedback(3, "Okay", "bug")
        self.collector.submit_feedback(5, "Excellent", "general")
        
        summary = self.collector.get_summary()
        
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["average_rating"], 4.33)
        self.assertEqual(summary["categories"]["general"], 2)
        self.assertEqual(summary["categories"]["bug"], 1)

    def test_empty_summary(self):
        """Test summary with no feedback."""
        summary = self.collector.get_summary()
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["average_rating"], 0.0)

if __name__ == '__main__':
    unittest.main()
