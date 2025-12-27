import os

import pytest

from lattice_lock.rollback.checkpoint import CheckpointManager
from lattice_lock.rollback.storage import CheckpointStorage


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace for file ops."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


def test_rollback_restoration_cycle(temp_workspace):
    """
    Test the full cycle:
    1. Create file
    2. Checkpoint
    3. Modify file
    4. Restore
    5. Verify
    """
    # Setup
    storage_dir = temp_workspace / ".lattice-lock/checkpoints"
    storage = CheckpointStorage(str(storage_dir))
    manager = CheckpointManager(storage)

    filename = "test_file.txt"
    original_content = "Original Content v1"

    # 1. Create file
    with open(filename, "w") as f:
        f.write(original_content)

    file_hash = manager.calculate_file_hash(filename)

    # 2. Checkpoint
    checkpoint_id = manager.create_checkpoint(
        files={filename: file_hash}, config={}, schema_version="1.0", description="Initial state"
    )

    assert checkpoint_id is not None

    # 3. Modify file
    with open(filename, "w") as f:
        f.write("Modified Content v2")

    assert open(filename).read() != original_content

    # 4. Restore
    success = manager.restore_file(checkpoint_id, filename)
    assert success is True

    # 5. Verify
    restored_content = open(filename).read()
    assert restored_content == original_content


def test_restore_missing_file_returns_false(temp_workspace):
    """Test restoring a file that wasn't backed up."""
    storage_dir = temp_workspace / ".lattice-lock/checkpoints"
    storage = CheckpointStorage(str(storage_dir))
    manager = CheckpointManager(storage)

    # Build a checkpoint but without files
    checkpoint_id = manager.create_checkpoint(files={}, config={}, schema_version="1.0")

    success = manager.restore_file(checkpoint_id, "non_existent.txt")
    assert success is False
