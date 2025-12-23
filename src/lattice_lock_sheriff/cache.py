import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from .config import SheriffConfig

logger = logging.getLogger("lattice_lock.sheriff.cache")


class SheriffCache:
    def __init__(self, cache_dir: Path = Path(".sheriff_cache"), config_hash: str = ""):
        self.cache_dir = cache_dir
        self.config_hash = config_hash
        self.cache_file = self.cache_dir / f"sheriff_cache_{config_hash}.json"
        self._cache: dict[
            Path, dict[str, Any]
        ] = {}  # {file_path: {file_hash: str, violations: List[dict]}}
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_hash(self, file_path: Path) -> str:
        """Generates a SHA256 hash of the file's content."""
        if not file_path.is_file():
            return ""  # Or raise an error
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def load(self) -> None:
        """Loads the cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self._cache = {Path(k): v for k, v in data.items()}
            except (OSError, json.JSONDecodeError) as e:
                # Log error and start with empty cache
                logger.warning(f"Failed to load sheriff cache from {self.cache_file}: {e}")
                self._cache = {}
        else:
            self._cache = {}

    def save(self) -> None:
        """Saves the cache to disk."""
        try:
            # Convert Path keys to strings for JSON serialization
            serializable_cache = {str(k): v for k, v in self._cache.items()}
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(serializable_cache, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save sheriff cache to {self.cache_file}: {e}")

    def clear(self) -> None:
        """Clears the current cache and removes the cache file."""
        self._cache = {}
        if self.cache_file.exists():
            try:
                self.cache_file.unlink()
            except OSError as e:
                logger.error(f"Failed to delete cache file {self.cache_file}: {e}")

    def get_cached_violations(self, file_path: Path) -> list[dict[str, Any]] | None:
        """
        Retrieves cached violations for a file if its hash matches.
        Returns a list of dictionaries, not Violation objects.
        """
        file_hash = self._get_file_hash(file_path)
        cached_data = self._cache.get(file_path)
        if cached_data and cached_data.get("file_hash") == file_hash:
            return cached_data.get("violations")
        return None

    def set_violations(self, file_path: Path, violations_data: list[dict[str, Any]]) -> None:
        """
        Caches violations for a file.
        Expects violations_data as a list of dictionaries (Violation.__dict__).
        """
        file_hash = self._get_file_hash(file_path)
        self._cache[file_path] = {"file_hash": file_hash, "violations": violations_data}


def get_config_hash(config: SheriffConfig) -> str:
    """Generates a SHA256 hash of the SheriffConfig object."""
    # Convert config to a consistent dictionary representation, then hash
    config_dict = {
        "forbidden_imports": sorted(config.forbidden_imports),  # Ensure consistent order
        "enforce_type_hints": config.enforce_type_hints,
        "target_version": config.target_version,
        "custom_rules": config.custom_rules,  # Assuming custom_rules is JSON-serializable
    }
    config_json = json.dumps(config_dict, sort_keys=True)
    return hashlib.sha256(config_json.encode("utf-8")).hexdigest()
