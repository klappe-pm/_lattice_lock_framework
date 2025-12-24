"""
Tests for rollback state management.
"""

import shutil
import tempfile
import time
import unittest
from pathlib import Path

from lattice_lock.rollback.checkpoint import CheckpointManager
from lattice_lock.rollback.state import RollbackState
from lattice_lock.rollback.storage import CheckpointStorage


class TestRollbackState(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.storage_dir = Path(self.test_dir) / "checkpoints"

        self.sample_state = RollbackState(
            timestamp=time.time(),
            files={"/path/to/file1": "hash1", "/path/to/file2": "hash2"},
            config={"key": "value"},
            schema_version="1.0.0",
            description="Test state",
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_rollback_state_serialization(self):
        """Test serialization and deserialization of RollbackState."""
        json_str = self.sample_state.to_json()
        restored_state = RollbackState.from_json(json_str)

        self.assertEqual(restored_state.timestamp, self.sample_state.timestamp)
        self.assertEqual(restored_state.files, self.sample_state.files)
        self.assertEqual(restored_state.config, self.sample_state.config)
        self.assertEqual(restored_state.schema_version, self.sample_state.schema_version)
        self.assertEqual(restored_state.description, self.sample_state.description)

    def test_rollback_state_diff(self):
        """Test state comparison."""
        state1 = RollbackState(
            timestamp=100.0, files={"f1": "h1", "f2": "h2"}, config={"c": 1}, schema_version="1.0"
        )
        state2 = RollbackState(
            timestamp=200.0,
            files={"f1": "h1", "f2": "h2_new", "f3": "h3"},
            config={"c": 2},
            schema_version="1.1",
        )

        diff = state2.diff(state1)

        self.assertIn("f2", diff["files_changed"])
        self.assertIn("f3", diff["files_added"])
        self.assertTrue(diff["config_changed"])
        self.assertTrue(diff["schema_version_changed"])

        # Test removal
        state3 = RollbackState(
            timestamp=300.0,
            files={"f1": "h1"},  # f2, f3 removed
            config={"c": 2},
            schema_version="1.1",
        )

        # Diff state3 against state2 (changes from state2 to state3)
        diff_rem = state3.diff(state2)
        self.assertIn("f2", diff_rem["files_removed"])
        self.assertIn("f3", diff_rem["files_removed"])

    def test_storage_save_load(self):
        """Test saving and loading states."""
        storage = CheckpointStorage(str(self.storage_dir))
        checkpoint_id = storage.save_state(self.sample_state)

        self.assertIsNotNone(checkpoint_id)

        loaded_state = storage.load_state(checkpoint_id)
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state.files, self.sample_state.files)

    def test_storage_list_delete(self):
        """Test listing and deleting states."""
        storage = CheckpointStorage(str(self.storage_dir))

        # Create two states
        id1 = storage.save_state(self.sample_state)
        time.sleep(0.01)  # Ensure timestamp difference
        self.sample_state.timestamp = time.time()
        id2 = storage.save_state(self.sample_state)

        states = storage.list_states()
        self.assertEqual(len(states), 2)
        self.assertEqual(states[0], id2)  # Newest first
        self.assertEqual(states[1], id1)

        # Delete one
        self.assertTrue(storage.delete_state(id1))
        states = storage.list_states()
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0], id2)

        # Delete non-existent
        self.assertFalse(storage.delete_state("non_existent"))

    def test_storage_prune(self):
        """Test pruning states."""
        storage = CheckpointStorage(str(self.storage_dir))

        ids = []
        for _ in range(5):
            self.sample_state.timestamp = time.time()
            ids.append(storage.save_state(self.sample_state))
            time.sleep(0.01)

        self.assertEqual(len(storage.list_states()), 5)

        storage.prune_states(3)
        remaining = storage.list_states()
        self.assertEqual(len(remaining), 3)
        self.assertEqual(remaining[0], ids[-1])  # Newest should be kept

    def test_checkpoint_manager(self):
        """Test CheckpointManager high-level API."""
        storage = CheckpointStorage(str(self.storage_dir))
        manager = CheckpointManager(storage)

        files = {"f1": "h1"}
        config = {"c": 1}

        cp_id = manager.create_checkpoint(files, config, "1.0", "Initial")
        self.assertIsNotNone(cp_id)

        cp = manager.get_checkpoint(cp_id)
        self.assertEqual(cp.files, files)
        self.assertEqual(cp.description, "Initial")

        self.assertEqual(len(manager.list_checkpoints()), 1)

        manager.delete_checkpoint(cp_id)
        self.assertEqual(len(manager.list_checkpoints()), 0)


if __name__ == "__main__":
    unittest.main()
