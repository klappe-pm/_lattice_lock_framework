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
    
    All methods are synchronous for ease of use.
    """

    def __init__(self, storage: CheckpointStorage = None):
        """
        Initialize the CheckpointManager with a checkpoint storage backend.
        
        Parameters:
            storage (CheckpointStorage | None): Storage backend used for persisting checkpoints. If None, a default CheckpointStorage instance is created.
        """
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
        checkpoint_id = self.storage.save_state(state)
        
        # Backup file contents
        for filepath in files:
            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                    self.storage.save_file_content(checkpoint_id, filepath, content)
            except (FileNotFoundError, PermissionError):
                continue
                
        return checkpoint_id

    def restore_file(self, checkpoint_id: str, filepath: str) -> bool:
        """
        Restore a file from a checkpoint.
        Returns True if successful, False if backup not found.
        """
        content = self.storage.load_file_content(checkpoint_id, filepath)
        if content is None:
            return False
            
        try:
            mode = "wb" if isinstance(content, bytes) else "w"
            encoding = None if isinstance(content, bytes) else "utf-8"
            
            # Ensure directory exists
            import os
            dirname = os.path.dirname(filepath)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            
            with open(filepath, mode, encoding=encoding) as f:
                f.write(content)
            return True
        except OSError:
            return False

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