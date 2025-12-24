import shutil
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lattice_lock.orchestrator.cost.models import UsageRecord
from lattice_lock.orchestrator.cost.storage import CostStorage
from lattice_lock.orchestrator.cost.tracker import CostTracker
from lattice_lock.orchestrator.registry import ModelRegistry
from lattice_lock.orchestrator.types import APIResponse, ModelCapabilities


class TestCostStorage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / "test_cost.db"
        self.storage = CostStorage(str(self.db_path))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_add_and_get_record(self):
        record = UsageRecord(
            timestamp=datetime.now(),
            session_id="sess_1",
            trace_id="trace_1",
            model_id="gpt-4o",
            provider="openai",
            task_type="coding",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
        )
        self.storage.add_record(record)

        total = self.storage.get_session_total("sess_1")
        self.assertAlmostEqual(total, 0.01)

    def test_aggregates(self):
        self.storage.add_record(
            UsageRecord(
                timestamp=datetime.now(),
                session_id="sess_1",
                trace_id="trace_1",
                model_id="gpt-4",
                provider="openai",
                task_type="coding",
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.10,
            )
        )
        self.storage.add_record(
            UsageRecord(
                timestamp=datetime.now(),
                session_id="sess_1",
                trace_id="trace_2",
                model_id="claude-3",
                provider="anthropic",
                task_type="writing",
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.05,
            )
        )

        aggregates = self.storage.get_aggregates(days=7)
        self.assertAlmostEqual(aggregates["total_cost"], 0.15)
        self.assertAlmostEqual(aggregates["by_provider"]["openai"], 0.10)
        self.assertAlmostEqual(aggregates["by_provider"]["anthropic"], 0.05)


class TestCostTracker(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / "tracker_test.db"

        # Mock Registry
        self.registry = MagicMock(spec=ModelRegistry)
        self.registry.models = {
            "test-model": MagicMock(
                spec=ModelCapabilities,
                input_cost=10.0,  # $10 per 1M tokens
                output_cost=30.0,  # $30 per 1M tokens
            )
        }

        self.tracker = CostTracker(self.registry, db_path=str(self.db_path))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_record_transaction_calculates_cost(self):
        response = APIResponse(
            content="test",
            model="test-model",
            provider="openai",
            usage={"input_tokens": 1_000, "output_tokens": 1_000},
            latency_ms=100,
        )

        self.tracker.record_transaction(response)

        # Expected Cost:
        # Input: 1000/1M * 10 = 0.01
        # Output: 1000/1M * 30 = 0.03
        # Total: 0.04

        report = self.tracker.get_report()
        self.assertAlmostEqual(report["total_cost"], 0.04)

    def test_record_transaction_unknown_model(self):
        response = APIResponse(
            content="test",
            model="unknown-model",
            provider="openai",
            usage={"input_tokens": 100, "output_tokens": 100},
            latency_ms=100,
        )
        self.tracker.record_transaction(response)

        # Should record 0 cost but still log usage
        report = self.tracker.get_report()
        self.assertEqual(report["total_cost"], 0.0)


if __name__ == "__main__":
    unittest.main()
