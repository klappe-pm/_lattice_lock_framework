"""
Checkpoint storage with synchronous and asynchronous backends.
"""
import glob
import gzip
import json
import os
import uuid
from pathlib import Path
from typing import Protocol, runtime_checkable

from .state import RollbackState


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol for storage backends (Local, S3, etc.)"""
    def ensure_path(self, path: str): ...
    def save(self, path: str, content: str | bytes, compressed: bool = True): ...
    def load(self, path: str, compressed: bool = True) -> str | bytes | None: ...
    def list_files(self, pattern: str) -> list[str]: ...
    def delete(self, path: str) -> bool: ...
    def exists(self, path: str) -> bool: ...


class FileBackend:
    """Local filesystem implementation of StorageBackend (synchronous)."""
    
    def ensure_path(self, path: str):
        p = Path(path)
        if p.suffix:  # It's a file
            p.parent.mkdir(parents=True, exist_ok=True)
        else:
            p.mkdir(parents=True, exist_ok=True)

    def save(self, path: str, content: str | bytes, compressed: bool = True):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        if compressed:
            mode = "wt" if isinstance(content, str) else "wb"
            encoding = "utf-8" if isinstance(content, str) else None
            with gzip.open(path, mode, encoding=encoding) as f:
                f.write(content)
        else:
            mode = "w" if isinstance(content, str) else "wb"
            encoding = "utf-8" if isinstance(content, str) else None
            with open(path, mode, encoding=encoding) as f:
                f.write(content)

    def load(self, path: str, compressed: bool = True) -> str | bytes | None:
        if not Path(path).exists():
            return None
            
        try:
            if compressed:
                try:
                    with gzip.open(path, "rt", encoding="utf-8") as f:
                        return f.read()
                except UnicodeDecodeError:
                    with gzip.open(path, "rb") as f:
                        return f.read()
            else:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return f.read()
                except UnicodeDecodeError:
                    with open(path, "rb") as f:
                        return f.read()
        except OSError:
            return None

    def list_files(self, pattern: str) -> list[str]:
        return glob.glob(pattern)

    def delete(self, path: str) -> bool:
        if Path(path).exists():
            os.remove(path)
            return True
        return False

    def exists(self, path: str) -> bool:
        return Path(path).exists()


class CheckpointStorage:
    """
    Manages storage of RollbackState objects using a configurable backend.
    
    All methods are synchronous for ease of use.
    """

    def __init__(self, storage_dir: str = ".lattice-lock/checkpoints", backend: StorageBackend | None = None):
        self.storage_dir = Path(storage_dir)
        self.backend = backend or FileBackend()
        # Ensure base directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_state(self, state: RollbackState) -> str:
        """Save a RollbackState. Returns the checkpoint ID."""
        checkpoint_id = str(uuid.uuid4())
        filename = f"{state.timestamp}_{checkpoint_id}.json.gz"
        filepath = str(self.storage_dir / filename)

        json_str = state.to_json()
        self.backend.save(filepath, json_str, compressed=True)
        return checkpoint_id

    def load_state(self, checkpoint_id: str) -> RollbackState | None:
        """Load a RollbackState by checkpoint ID."""
        pattern = str(self.storage_dir / f"*_{checkpoint_id}.json.gz")
        files = self.backend.list_files(pattern)

        if not files:
            return None

        content = self.backend.load(files[0], compressed=True)
        if content and isinstance(content, str):
            try:
                return RollbackState.from_json(content)
            except json.JSONDecodeError:
                return None
        return None

    def list_states(self) -> list[str]:
        """List all available checkpoint IDs, newest first."""
        pattern = str(self.storage_dir / "*.json.gz")
        files = self.backend.list_files(pattern)
        files.sort(reverse=True)

        checkpoint_ids = []
        for filepath in files:
            filename = os.path.basename(filepath)
            try:
                parts = filename.split("_")
                if len(parts) >= 2:
                    uuid_part = parts[1].replace(".json.gz", "")
                    checkpoint_ids.append(uuid_part)
            except IndexError:
                continue
        return checkpoint_ids

    def delete_state(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint by ID."""
        pattern = str(self.storage_dir / f"*_{checkpoint_id}.json.gz")
        files = self.backend.list_files(pattern)

        if not files:
            return False

        return self.backend.delete(files[0])

    def prune_states(self, keep_n: int):
        """Keep only the N most recent checkpoints."""
        if keep_n < 0:
            return

        all_ids = self.list_states()
        if len(all_ids) <= keep_n:
            return

        ids_to_delete = all_ids[keep_n:]
        for checkpoint_id in ids_to_delete:
            self.delete_state(checkpoint_id)

    def save_file_content(self, checkpoint_id: str, filepath: str, content: str | bytes):
        """Save a file's content associated with a checkpoint."""
        import hashlib
        path_hash = hashlib.sha256(filepath.encode()).hexdigest()
        backup_path = str(self.storage_dir / checkpoint_id / f"{path_hash}.gz")
        self.backend.save(backup_path, content, compressed=True)

    def load_file_content(self, checkpoint_id: str, filepath: str) -> str | bytes | None:
        """Load a file's content from a checkpoint."""
        import hashlib
        path_hash = hashlib.sha256(filepath.encode()).hexdigest()
        backup_path = str(self.storage_dir / checkpoint_id / f"{path_hash}.gz")
        return self.backend.load(backup_path, compressed=True)
