"""
Rollback state definition and serialization.
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import time

@dataclass
class RollbackState:
    """Represents a snapshot of the system state for rollback."""
    timestamp: float
    files: Dict[str, str]  # path -> hash
    config: Dict[str, Any]
    schema_version: str
    description: str = ""

    def to_json(self) -> str:
        """Serialize state to JSON string."""
        return json.dumps(asdict(self), sort_keys=True)

    @classmethod
    def from_json(cls, json_str: str) -> 'RollbackState':
        """Deserialize state from JSON string."""
        data = json.loads(json_str)
        return cls(**data)

    def diff(self, other: 'RollbackState') -> Dict[str, Any]:
        """
        Compare this state with another state.
        Returns a dictionary describing the differences.
        """
        diff_result = {
            "files_changed": [],
            "files_added": [],
            "files_removed": [],
            "config_changed": False,
            "schema_version_changed": False
        }

        # Compare files
        all_files = set(self.files.keys()) | set(other.files.keys())
        for file_path in all_files:
            hash_self = self.files.get(file_path)
            hash_other = other.files.get(file_path)

            if hash_self and not hash_other:
                diff_result["files_removed"].append(file_path) # Removed in 'other' (current) compared to 'self' (old)?
                # Usually diff is new - old. Let's assume self is NEW, other is OLD.
                # Wait, usually we diff current state against a checkpoint.
                # Let's define diff as: changes to get from OTHER to SELF.
                # So if file is in SELF but not OTHER, it was added.
            elif hash_self and not hash_other:
                 # This logic is getting confusing. Let's be explicit.
                 pass

        # Let's restart the logic for clarity.
        # Diff: What changed from OTHER -> SELF

        # Files
        for file_path, file_hash in self.files.items():
            if file_path not in other.files:
                diff_result["files_added"].append(file_path)
            elif other.files[file_path] != file_hash:
                diff_result["files_changed"].append(file_path)

        for file_path in other.files:
            if file_path not in self.files:
                diff_result["files_removed"].append(file_path)

        # Config
        if self.config != other.config:
            diff_result["config_changed"] = True

        # Schema Version
        if self.schema_version != other.schema_version:
            diff_result["schema_version_changed"] = True

        return diff_result
