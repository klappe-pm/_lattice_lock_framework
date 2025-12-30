"""
Tests for rollback state management.
"""

import time

import pytest
from lattice_lock.rollback.checkpoint import CheckpointManager
from lattice_lock.rollback.state import RollbackState
from lattice_lock.rollback.storage import CheckpointStorage


@pytest.fixture
def sample_state():
    """
    Create a sample RollbackState representing a simple test snapshot.

    Returns:
        RollbackState: Instance with the current timestamp, files set to
            {'/path/to/file1': 'hash1', '/path/to/file2': 'hash2'},
            config {'key': 'value'}, schema_version '1.0.0', and description 'Test state'.
    """
    return RollbackState(
        timestamp=time.time(),
        files={"/path/to/file1": "hash1", "/path/to/file2": "hash2"},
        config={"key": "value"},
        schema_version="1.0.0",
        description="Test state",
    )


@pytest.fixture
def storage_dir(tmp_path):
    """
    Provide a Path for a temporary "checkpoints" directory inside the pytest tmp_path.

    Parameters:
        tmp_path (pathlib.Path): Base temporary directory provided by pytest.

    Returns:
        path (pathlib.Path): Path to the "checkpoints" subdirectory under `tmp_path`.
    """
    return tmp_path / "checkpoints"


def test_rollback_state_serialization(sample_state):
    """Test serialization and deserialization of RollbackState."""
    json_str = sample_state.to_json()
    restored_state = RollbackState.from_json(json_str)

    assert restored_state.timestamp == sample_state.timestamp
    assert restored_state.files == sample_state.files
    assert restored_state.config == sample_state.config
    assert restored_state.schema_version == sample_state.schema_version
    assert restored_state.description == sample_state.description


def test_rollback_state_diff():
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

    assert "f2" in diff["files_changed"]
    assert "f3" in diff["files_added"]
    assert diff["config_changed"] is True
    assert diff["schema_version_changed"] is True

    # Test removal
    state3 = RollbackState(
        timestamp=300.0,
        files={"f1": "h1"},  # f2, f3 removed
        config={"c": 2},
        schema_version="1.1",
    )

    # Diff state3 against state2 (changes from state2 to state3)
    diff_rem = state3.diff(state2)
    assert "f2" in diff_rem["files_removed"]
    assert "f3" in diff_rem["files_removed"]


def test_storage_save_load(storage_dir, sample_state):
    """Test saving and loading states."""
    storage = CheckpointStorage(str(storage_dir))
    checkpoint_id = storage.save_state(sample_state)

    assert checkpoint_id is not None

    loaded_state = storage.load_state(checkpoint_id)
    assert loaded_state is not None
    assert loaded_state.files == sample_state.files


def test_storage_list_delete(storage_dir, sample_state):
    """Test listing and deleting states."""
    storage = CheckpointStorage(str(storage_dir))

    # Create two states
    id1 = storage.save_state(sample_state)
    time.sleep(0.01)  # Ensure timestamp difference
    sample_state.timestamp = time.time()
    id2 = storage.save_state(sample_state)

    states = storage.list_states()
    assert len(states) == 2
    assert states[0] == id2  # Newest first
    assert states[1] == id1

    # Delete one
    assert storage.delete_state(id1) is True
    states = storage.list_states()
    assert len(states) == 1
    assert states[0] == id2

    # Delete non-existent
    assert storage.delete_state("non_existent") is False


def test_storage_prune(storage_dir, sample_state):
    """Test pruning states."""
    storage = CheckpointStorage(str(storage_dir))

    ids = []
    for _ in range(5):
        sample_state.timestamp = time.time()
        ids.append(storage.save_state(sample_state))
        time.sleep(0.01)

    states = storage.list_states()
    assert len(states) == 5

    storage.prune_states(3)
    remaining = storage.list_states()
    assert len(remaining) == 3
    assert remaining[0] == ids[-1]  # Newest should be kept


def test_checkpoint_manager(storage_dir):
    """Test CheckpointManager high-level API."""
    storage = CheckpointStorage(str(storage_dir))
    manager = CheckpointManager(storage)

    files = {"f1": "h1"}
    config = {"c": 1}

    cp_id = manager.create_checkpoint(files, config, "1.0", "Initial")
    assert cp_id is not None

    cp = manager.get_checkpoint(cp_id)
    assert cp.files == files
    assert cp.description == "Initial"

    checkpoints = manager.list_checkpoints()
    assert len(checkpoints) == 1

    manager.delete_checkpoint(cp_id)
    checkpoints = manager.list_checkpoints()
    assert len(checkpoints) == 0
