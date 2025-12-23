"""
File-based storage for rollback checkpoints.
"""

import glob
import gzip
import json
import os
import uuid
from pathlib import Path

from .state import RollbackState


class CheckpointStorage:
    """
    Manages storage of RollbackState objects on disk.
    Uses gzip compression for efficiency.
    """

    def __init__(self, storage_dir: str = ".lattice-lock/checkpoints"):
        self.storage_dir = Path(storage_dir)
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """Ensure the storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_state(self, state: RollbackState) -> str:
        """
        Save a RollbackState to disk.
        Returns the checkpoint ID.
        """
        checkpoint_id = str(uuid.uuid4())
        filename = f"{state.timestamp}_{checkpoint_id}.json.gz"
        filepath = self.storage_dir / filename

        json_str = state.to_json()
        with gzip.open(filepath, "wt", encoding="utf-8") as f:
            f.write(json_str)

        return checkpoint_id

    def load_state(self, checkpoint_id: str) -> RollbackState | None:
        """
        Load a RollbackState by checkpoint ID.
        """
        # We need to find the file since it has a timestamp prefix
        pattern = str(self.storage_dir / f"*_{checkpoint_id}.json.gz")
        files = glob.glob(pattern)

        if not files:
            return None

        filepath = files[0]
        try:
            with gzip.open(filepath, "rt", encoding="utf-8") as f:
                json_str = f.read()
            return RollbackState.from_json(json_str)
        except (OSError, json.JSONDecodeError):
            return None

    def list_states(self) -> list[str]:
        """
        List all available checkpoint IDs, sorted by timestamp (newest first).
        """
        pattern = str(self.storage_dir / "*.json.gz")
        files = glob.glob(pattern)

        # Sort by filename (which starts with timestamp)
        files.sort(reverse=True)

        checkpoint_ids = []
        for filepath in files:
            # Filename format: timestamp_uuid.json.gz
            filename = os.path.basename(filepath)
            try:
                # Extract UUID part
                parts = filename.split("_")
                if len(parts) >= 2:
                    uuid_part = parts[1].replace(".json.gz", "")
                    checkpoint_ids.append(uuid_part)
            except IndexError:
                continue

        return checkpoint_ids

    def delete_state(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint by ID.
        Returns True if deleted, False if not found.
        """
        pattern = str(self.storage_dir / f"*_{checkpoint_id}.json.gz")
        files = glob.glob(pattern)

        if not files:
            return False

        try:
            os.remove(files[0])
            return True
        except OSError:
            return False

    def prune_states(self, keep_n: int):
        """
        Keep only the N most recent checkpoints.
        """
        if keep_n < 0:
            return

        all_ids = self.list_states()
        if len(all_ids) <= keep_n:
            return

        ids_to_delete = all_ids[keep_n:]
        for checkpoint_id in ids_to_delete:
            self.delete_state(checkpoint_id)

    def _get_backup_path(self, checkpoint_id: str, filepath: str) -> Path:
        """Get the full path for a file backup inside a checkpoint."""
        # Sanitize filepath to avoid tree traversal
        # We flat-map the directory structure or use a hash of the path
        # Simple approach: hash the path to use as filename
        import hashlib
        path_hash = hashlib.sha256(filepath.encode()).hexdigest()
        
        # Use a subdirectory for the checkpoint
        checkpoint_dir = self.storage_dir / checkpoint_id
        checkpoint_dir.mkdir(exist_ok=True)
        
        return checkpoint_dir / f"{path_hash}.gz"

    def save_file_content(self, checkpoint_id: str, filepath: str, content: str | bytes):
        """Save a file's content associated with a checkpoint."""
        backup_path = self._get_backup_path(checkpoint_id, filepath)
        
        mode = "wb" if isinstance(content, bytes) else "wt"
        encoding = None if isinstance(content, bytes) else "utf-8"
        
        with gzip.open(backup_path, mode, encoding=encoding) as f:
            f.write(content)

    def load_file_content(self, checkpoint_id: str, filepath: str) -> str | bytes | None:
        """Load a file's content from a checkpoint."""
        backup_path = self._get_backup_path(checkpoint_id, filepath)
        
        if not backup_path.exists():
            return None
            
        try:
            # Try reading as text first, if fails assume bytes? 
            # Ideally we know the type. For now, let's assume text for code files.
            # But safer to read as bytes and decode if needed?
            # Existing save_file_content implies we know. 
            # Let's try text.
            with gzip.open(backup_path, "rt", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return None
        except UnicodeDecodeError:
             # Fallback to bytes
             with gzip.open(backup_path, "rb") as f:
                return f.read()
