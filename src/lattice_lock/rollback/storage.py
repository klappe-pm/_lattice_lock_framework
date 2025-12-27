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
    def ensure_path(self, path: str): """
Ensure the filesystem path exists, creating directories as needed.

Parameters:
    path (str): Target filesystem path. If the path appears to include a file suffix it is treated as a file path and the parent directory is created; otherwise the path is treated as a directory and the directory (and any missing parents) is created.
"""
...
    def save(self, path: str, content: str | bytes, compressed: bool = True): """
Save content to the given filesystem path, optionally using gzip compression.

Parameters:
    path (str): Destination filesystem path. Parent directories will be created as needed.
    content (str | bytes): Data to write; str values are encoded as UTF-8.
    compressed (bool): If True, store the content in gzip-compressed form; if False, store as a regular file.
"""
...
    def load(self, path: str, compressed: bool = True) -> str | bytes | None: """
Load file content from the storage backend, optionally treating the file as gzip-compressed.

Parameters:
    path (str): Filesystem path to the file to load.
    compressed (bool): If True, attempt to read the file as gzip-compressed; otherwise read as a plain file.

Returns:
    str | bytes | None: The file content as a UTF-8 decoded string when text decoding succeeds, as raw bytes when decoding fails, or None if the path does not exist or an OS-level read error occurs.
"""
...
    def list_files(self, pattern: str) -> list[str]: """
List filesystem paths that match the given glob pattern.

Parameters:
	pattern (str): A glob pattern (e.g., "*.json.gz" or "dir/**/*.txt") used to select files.

Returns:
	A list of matching file path strings (may be empty if no files match).
"""
...
    def delete(self, path: str) -> bool: """
Delete the file at the given path if it exists.

Parameters:
    path (str): File path to remove.

Returns:
    bool: `True` if the file was removed, `False` if the file did not exist.
"""
...
    def exists(self, path: str) -> bool: """
Check whether the given filesystem path exists.

Parameters:
    path (str): Path to check; may refer to a file or directory.

Returns:
    bool: `True` if the path exists, `False` otherwise.
"""
...


class FileBackend:
    """Local filesystem implementation of StorageBackend (synchronous)."""
    
    def ensure_path(self, path: str):
        """
        Ensure a filesystem path exists, creating directories as needed.
        
        If the given path string appears to reference a file (has a suffix), create its parent directories.
        Otherwise create the directory at the given path. Existing directories are left unchanged.
        
        Parameters:
            path (str): Path to a file or directory to ensure exists.
        """
        p = Path(path)
        if p.suffix:  # It's a file
            p.parent.mkdir(parents=True, exist_ok=True)
        else:
            p.mkdir(parents=True, exist_ok=True)

    def save(self, path: str, content: str | bytes, compressed: bool = True):
        """
        Save content to a filesystem path, optionally using gzip compression.
        
        Parameters:
        	path (str): Target filesystem path where content will be written. Parent directories are created if they do not exist.
        	content (str | bytes): Data to write; text is encoded as UTF-8 when appropriate.
        	compressed (bool): If True, write the file using gzip compression; otherwise write a plain file. Default is True.
        """
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
        """
        Load content from a file, attempting UTF-8 text first and falling back to binary.
        
        Parameters:
        	path (str): Filesystem path to the file to load.
        	compressed (bool): If True, treat the file as gzip-compressed; otherwise treat it as a plain file.
        
        Returns:
        	str | bytes | None: The file content as a UTF-8 decoded string if text decoding succeeds, otherwise as raw bytes;
        	None if the path does not exist or an I/O error occurs.
        """
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
        """
        Return file paths that match the given glob pattern.
        
        Parameters:
        	pattern (str): A glob pattern used to match filesystem paths (e.g., '/tmp/*.txt' or 'dir/**/*.gz').
        
        Returns:
        	list[str]: A list of matching file paths as strings; an empty list if no files match.
        """
        return glob.glob(pattern)

    def delete(self, path: str) -> bool:
        """
        Delete the file at the given path if it exists.
        
        Parameters:
        	path (str): Filesystem path to the file to remove.
        
        Returns:
        	deleted (bool): `True` if the file existed and was removed, `False` if the file did not exist.
        """
        if Path(path).exists():
            os.remove(path)
            return True
        return False

    def exists(self, path: str) -> bool:
        """
        Check whether the given filesystem path exists.
        
        Returns:
            True if the path exists, False otherwise.
        """
        return Path(path).exists()


class CheckpointStorage:
    """
    Manages storage of RollbackState objects using a configurable backend.
    
    All methods are synchronous for ease of use.
    """

    def __init__(self, storage_dir: str = ".lattice-lock/checkpoints", backend: StorageBackend | None = None):
        """
        Initialize the CheckpointStorage with a base storage directory and storage backend.
        
        Parameters:
            storage_dir (str): Filesystem path where checkpoints will be stored; created if it does not exist.
            backend (StorageBackend | None): Backend used for storage operations; defaults to a local FileBackend.
        """
        self.storage_dir = Path(storage_dir)
        self.backend = backend or FileBackend()
        # Ensure base directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_state(self, state: RollbackState) -> str:
        """
        Save the given RollbackState as a new checkpoint.
        
        Returns:
            checkpoint_id (str): The UUID assigned to the newly created checkpoint.
        """
        checkpoint_id = str(uuid.uuid4())
        filename = f"{state.timestamp}_{checkpoint_id}.json.gz"
        filepath = str(self.storage_dir / filename)

        json_str = state.to_json()
        self.backend.save(filepath, json_str, compressed=True)
        return checkpoint_id

    def load_state(self, checkpoint_id: str) -> RollbackState | None:
        """
        Load the RollbackState corresponding to the given checkpoint ID.
        
        Returns:
            RollbackState if a matching checkpoint file is found and parsed successfully, `None` otherwise.
        """
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
        """
        List all available checkpoint IDs, newest first.
        
        Scans the storage directory for files matching "*.json.gz" and extracts the checkpoint ID from filenames of the form "<timestamp>_<checkpoint_id>.json.gz".
        
        Returns:
            list[str]: Checkpoint IDs ordered newest first (by filename sort).
        """
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
        """
        Delete the checkpoint file identified by the given checkpoint ID.
        
        Attempts to locate a checkpoint file named "*_{checkpoint_id}.json.gz" in the storage directory and deletes the first match found.
        
        Returns:
            bool: `True` if a matching checkpoint file was deleted, `False` if no match was found.
        """
        pattern = str(self.storage_dir / f"*_{checkpoint_id}.json.gz")
        files = self.backend.list_files(pattern)

        if not files:
            return False

        return self.backend.delete(files[0])

    def prune_states(self, keep_n: int):
        """
        Keep only the N most recent checkpoints.
        
        If there are more than keep_n checkpoints, delete older checkpoints beyond the most recent keep_n. A negative keep_n is treated as no-op.
        
        Parameters:
            keep_n (int): Number of most-recent checkpoints to retain; older checkpoints are removed.
        """
        if keep_n < 0:
            return

        all_ids = self.list_states()
        if len(all_ids) <= keep_n:
            return

        ids_to_delete = all_ids[keep_n:]
        for checkpoint_id in ids_to_delete:
            self.delete_state(checkpoint_id)

    def save_file_content(self, checkpoint_id: str, filepath: str, content: str | bytes):
        """
        Save the provided file content as a backup tied to a specific checkpoint.
        
        Parameters:
            checkpoint_id (str): Identifier of the checkpoint under which the content will be stored.
            filepath (str): Original file path; a SHA-256 hash of this string is used to derive the stored filename.
            content (str | bytes): File contents to store; may be text or binary.
        """
        import hashlib
        path_hash = hashlib.sha256(filepath.encode()).hexdigest()
        backup_path = str(self.storage_dir / checkpoint_id / f"{path_hash}.gz")
        self.backend.save(backup_path, content, compressed=True)

    def load_file_content(self, checkpoint_id: str, filepath: str) -> str | bytes | None:
        """
        Load file content associated with a checkpoint.
        
        The provided filepath is mapped to the stored backup name using a SHA-256 hash; the matching compressed backup for the given checkpoint is loaded.
        
        Parameters:
            checkpoint_id (str): Checkpoint identifier.
            filepath (str): Original file path whose backup was saved.
        
        Returns:
            str | bytes | None: The file content (decoded text or raw bytes) if present, otherwise `None`.
        """
        import hashlib
        path_hash = hashlib.sha256(filepath.encode()).hexdigest()
        backup_path = str(self.storage_dir / checkpoint_id / f"{path_hash}.gz")
        return self.backend.load(backup_path, compressed=True)