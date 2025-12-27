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
    def ensure_path(self, path: str): 
        """
        Ensure the filesystem path required for storage exists.

        If `path` appears to be a file path (has a suffix), its parent directory is created; otherwise `path` itself is created as a directory. Directories are created as needed.

        Parameters:
            path (str): File or directory path to prepare for storage.
        """
        ...
    def save(self, path: str, content: str | bytes, compressed: bool = True): 
        """
        Save content to the given filesystem path, optionally using gzip compression and ensuring the destination directory exists.

        Parameters:
        	path (str): Destination file path. If a file path is provided, its parent directory will be created if missing.
        	content (str | bytes): Data to write; text (str) will be encoded as UTF-8, bytes will be written as-is.
        	compressed (bool): If True, write the data gzip-compressed; otherwise write uncompressed.
        """
        ...
    def load(self, path: str, compressed: bool = True) -> str | bytes | None: 
        """
        Load and return file content from the backend, optionally treating the file as gzip-compressed.

        Parameters:
            path (str): Filesystem path to read.
            compressed (bool): If True, interpret the file as gzip-compressed; otherwise read raw file.

        Returns:
            str | bytes | None: Decoded UTF-8 `str` if the file is textual, raw `bytes` if binary, or `None` if the file does not exist or an I/O error occurs.
        """
        ...
    def list_files(self, pattern: str) -> list[str]: 
        """
        List filesystem paths matching the given glob pattern.

        Parameters:
            pattern (str): Glob-style pattern to match files (e.g., '*.json.gz').

        Returns:
            list[str]: Sorted list of matching file paths as strings.
        """
        ...
    def delete(self, path: str) -> bool: 
        """
        Delete the file at the given path.

        Parameters:
            path (str): Filesystem path to remove.

        Returns:
            bool: `True` if the file was removed, `False` if the path did not exist or removal failed.
        """
        ...
    def exists(self, path: str) -&gt; bool: 
        """
        Check whether a storage path exists in the backend.

        Parameters:
            path (str): The storage path (file or directory) to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        ...


<details><summary>Prompt To Fix With AI</summary>

`````markdown
This is a comment left during a code review.
Path: src/lattice_lock/rollback/storage.py
Line: 18:76

Comment:
**syntax:** Protocol method docstrings cannot be placed inline after the signature in Python. This syntax is invalid and will cause the docstrings to be ignored. They should be triple-quoted strings on the line after the method signature.

```suggestion
    def ensure_path(self, path: str): 
        """
        Ensure the filesystem path required for storage exists.

        If `path` appears to be a file path (has a suffix), its parent directory is created; otherwise `path` itself is created as a directory. Directories are created as needed.

        Parameters:
            path (str): File or directory path to prepare for storage.
        """
        ...
    def save(self, path: str, content: str | bytes, compressed: bool = True): 
        """
        Save content to the given filesystem path, optionally using gzip compression and ensuring the destination directory exists.

        Parameters:
        	path (str): Destination file path. If a file path is provided, its parent directory will be created if missing.
        	content (str | bytes): Data to write; text (str) will be encoded as UTF-8, bytes will be written as-is.
        	compressed (bool): If True, write the data gzip-compressed; otherwise write uncompressed.
        """
        ...
    def load(self, path: str, compressed: bool = True) -> str | bytes | None: 
        """
        Load and return file content from the backend, optionally treating the file as gzip-compressed.

        Parameters:
            path (str): Filesystem path to read.
            compressed (bool): If True, interpret the file as gzip-compressed; otherwise read raw file.

        Returns:
            str | bytes | None: Decoded UTF-8 `str` if the file is textual, raw `bytes` if binary, or `None` if the file does not exist or an I/O error occurs.
        """
        ...
    def list_files(self, pattern: str) -> list[str]: 
        """
        List filesystem paths matching the given glob pattern.

        Parameters:
            pattern (str): Glob-style pattern to match files (e.g., '*.json.gz').

        Returns:
            list[str]: Sorted list of matching file paths as strings.
        """
        ...
    def delete(self, path: str) -> bool: 
        """
        Delete the file at the given path.

        Parameters:
            path (str): Filesystem path to remove.

        Returns:
            bool: `True` if the file was removed, `False` if the path did not exist or removal failed.
        """
        ...
    def exists(self, path: str) -&gt; bool: 
        """
        Check whether a storage path exists in the backend.

        Parameters:
            path (str): The storage path (file or directory) to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        ...


How can I resolve this? If you propose a fix, please make it concise.


class FileBackend:
    """Local filesystem implementation of StorageBackend (synchronous)."""
    
    def ensure_path(self, path: str):
        """
        Ensure the filesystem path exists by creating necessary directories.
        
        Parameters:
        	path (str): Target filesystem path. If the path has a suffix it is treated as a file and this creates its parent directories; otherwise the path is treated as a directory and the directory itself is created.
        """
        p = Path(path)
        if p.suffix:  # It's a file
            p.parent.mkdir(parents=True, exist_ok=True)
        else:
            p.mkdir(parents=True, exist_ok=True)

    def save(self, path: str, content: str | bytes, compressed: bool = True):
        """
        Write content to the given filesystem path, ensuring parent directories exist and optionally gzip-compressing the output.
        
        Parameters:
            path (str): Filesystem path to write to.
            content (str | bytes): Data to write; text is encoded as UTF-8.
            compressed (bool): If True, store the data in gzip-compressed form; otherwise write raw data.
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
        Load file content from the local filesystem, optionally treating the file as gzip-compressed.
        
        Parameters:
            path (str): Filesystem path to the file to load.
            compressed (bool): If True, read the file as gzip-compressed data; otherwise read it directly.
        
        Returns:
            str | bytes | None: `str` decoded as UTF-8 when the file is valid UTF-8, `bytes` when decoding fails or the file is binary, or `None` if the path does not exist or an I/O error occurs.
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
        List filesystem paths that match a glob pattern.
        
        Parameters:
        	pattern (str): Glob-style pattern to match file paths (as used by the system glob module).
        """
        return glob.glob(pattern)

    def delete(self, path: str) -> bool:
        """
        Delete the file at the given filesystem path if it exists.
        
        Returns:
            bool: `True` if a file was removed, `False` if no file existed at the path.
        """
        if Path(path).exists():
            os.remove(path)
            return True
        return False

    def exists(self, path: str) -> bool:
        """
        Check whether a filesystem path exists.
        
        Parameters:
            path (str): Path to a file or directory.
        
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
        Initialize the checkpoint storage with a base directory and storage backend.
        
        Parameters:
            storage_dir (str): Base directory where checkpoint files and per-checkpoint backups are stored.
            backend (StorageBackend | None): Storage backend implementation to use for filesystem operations;
                when omitted a local FileBackend is created and used.
        
        Side effects:
            Ensures the base storage directory exists on disk.
        """
        self.storage_dir = Path(storage_dir)
        self.backend = backend or FileBackend()
        # Ensure base directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_state(self, state: RollbackState) -> str:
        """
        Store the given RollbackState as a gzip-compressed JSON checkpoint file.
        
        The state is serialized to JSON and written under the storage directory using a filename of the form "{timestamp}_{checkpoint_id}.json.gz".
        
        Parameters:
            state (RollbackState): The rollback state to persist.
        
        Returns:
            checkpoint_id (str): The generated UUID4 identifier for the saved checkpoint.
        """
        checkpoint_id = str(uuid.uuid4())
        filename = f"{state.timestamp}_{checkpoint_id}.json.gz"
        filepath = str(self.storage_dir / filename)

        json_str = state.to_json()
        self.backend.save(filepath, json_str, compressed=True)
        return checkpoint_id

    def load_state(self, checkpoint_id: str) -> RollbackState | None:
        """
        Load the RollbackState corresponding to the given checkpoint identifier.
        
        Returns:
            The deserialized `RollbackState` if a matching compressed checkpoint file is found and contains valid JSON; `None` if no matching file exists or the file cannot be parsed.
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
        Return checkpoint IDs available in storage, ordered newest first.
        
        Returns:
            list[str]: Checkpoint IDs extracted from matching "*.json.gz" filenames, ordered from newest to oldest.
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
        Delete the stored checkpoint file identified by checkpoint_id.
        
        Parameters:
            checkpoint_id (str): Checkpoint identifier used in stored filenames (the UUID portion).
        
        Returns:
            bool: True if a matching checkpoint file was found and deleted, False otherwise.
        """
        pattern = str(self.storage_dir / f"*_{checkpoint_id}.json.gz")
        files = self.backend.list_files(pattern)

        if not files:
            return False

        return self.backend.delete(files[0])

    def prune_states(self, keep_n: int):
        """
        Remove older checkpoints so only the most recent `keep_n` remain.
        
        If `keep_n` is less than zero, the function does nothing. If the current number
        of checkpoints is less than or equal to `keep_n`, no checkpoints are removed.
        Otherwise, checkpoints older than the newest `keep_n` are deleted.
        
        Parameters:
            keep_n (int): Number of most recent checkpoints to retain.
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
        Store file content in the checkpoint's backup area using a deterministic filename.
        
        The content is saved under the checkpoint's directory using a SHA-256 hash of `filepath` as the filename (with a ".gz" suffix) and is written with gzip compression via the configured backend.
        
        Parameters:
            checkpoint_id (str): Identifier of the checkpoint to associate the file with.
            filepath (str): Original file path used to derive the storage key (hashed).
            content (str | bytes): File content to store; may be text or binary.
        """
        import hashlib
        path_hash = hashlib.sha256(filepath.encode()).hexdigest()
        backup_path = str(self.storage_dir / checkpoint_id / f"{path_hash}.gz")
        self.backend.save(backup_path, content, compressed=True)

    def load_file_content(self, checkpoint_id: str, filepath: str) -> str | bytes | None:
        """
        Retrieve the backed-up content of a file stored under a checkpoint.
        
        Parameters:
        	checkpoint_id (str): Identifier of the checkpoint containing the backup.
        	filepath (str): Original file path; its SHA-256 digest is used to locate the stored backup.
        
        Returns:
        	content (str | bytes | None): The stored file content as a UTF-8 decoded string for text files or raw bytes for binary files; `None` if no backup exists.
        """
        import hashlib
        path_hash = hashlib.sha256(filepath.encode()).hexdigest()
        backup_path = str(self.storage_dir / checkpoint_id / f"{path_hash}.gz")
        return self.backend.load(backup_path, compressed=True)