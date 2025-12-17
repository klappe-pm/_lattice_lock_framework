"""
High-level checkpoint management.
"""

import hashlib
import time
from typing import Any

from .state import RollbackState
from .storage import CheckpointStorage


class CheckpointManager:
    """
    Manages creation, retrieval, and deletion of checkpoints.
    """

    def __init__(self, storage: CheckpointStorage = None):
        self.storage = storage or CheckpointStorage()

    def create_checkpoint(
        self,
        files: dict[str, str],
        config: dict[str, Any],
        schema_version: str,
        description: str = "",
    ) -> str:
        """
        Create a new checkpoint with the given state.

        Args:
            files: Dictionary mapping file paths to their content hashes.
            config: Current configuration dictionary.
            schema_version: Current schema version string.
            description: Optional description for the checkpoint.

        Returns:
            The ID of the created checkpoint.
        """
        state = RollbackState(
            timestamp=time.time(),
            files=files,
            config=config,
            schema_version=schema_version,
            description=description,
        )
        return self.storage.save_state(state)

    def list_checkpoints(self) -> list[str]:
        """
        List all available checkpoint IDs.
        """
        return self.storage.list_states()

    def get_checkpoint(self, checkpoint_id: str) -> RollbackState | None:
        """
        Retrieve a specific checkpoint by ID.
        """
        return self.storage.load_state(checkpoint_id)

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint by ID.
        """
        return self.storage.delete_state(checkpoint_id)

    def prune_checkpoints(self, keep_n: int):
        """
        Keep only the last N checkpoints.
        """
        self.storage.prune_states(keep_n)

    @staticmethod
    def calculate_file_hash(filepath: str) -> str:
        """
        Helper to calculate SHA256 hash of a file.
        """
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except FileNotFoundError:
            return ""
