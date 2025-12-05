"""
File-based storage for rollback checkpoints.
"""

import os
import gzip
import json
import glob
from typing import List, Optional
from pathlib import Path
import uuid

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
        with gzip.open(filepath, 'wt', encoding='utf-8') as f:
            f.write(json_str)
        
        return checkpoint_id

    def load_state(self, checkpoint_id: str) -> Optional[RollbackState]:
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
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                json_str = f.read()
            return RollbackState.from_json(json_str)
        except (OSError, json.JSONDecodeError):
            return None

    def list_states(self) -> List[str]:
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
                parts = filename.split('_')
                if len(parts) >= 2:
                    uuid_part = parts[1].replace('.json.gz', '')
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
