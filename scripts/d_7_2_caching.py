
# IMPLEMENTATION PROTOTYPE (Agent D_7_2)
# Task 7.2: Core Caching Layer

import hashlib
import pickle
import time
from pathlib import Path
from typing import Any, Optional

CACHE_DIR = Path(".lattice/cache")

class CacheLayer:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode()).hexdigest()
        return CACHE_DIR / f"{hashed}.cache"

    def get(self, key: str) -> Optional[Any]:
        path = self._get_path(key)
        if not path.exists():
            return None

        try:
            with open(path, "rb") as f:
                data = pickle.load(f)

            if time.time() - data['ts'] > self.ttl:
                print(f"[CACHE] Expired: {key}")
                path.unlink()
                return None

            print(f"[CACHE] Hit: {key}")
            return data['val']
        except Exception:
            return None

    def set(self, key: str, value: Any):
        path = self._get_path(key)
        with open(path, "wb") as f:
            pickle.dump({"ts": time.time(), "val": value}, f)
        print(f"[CACHE] Set: {key}")

if __name__ == "__main__":
    cache = CacheLayer(ttl_seconds=5)
    cache.set("test_prompt", "Response from LLM")
    print(cache.get("test_prompt"))
    print(cache.get("missing"))
