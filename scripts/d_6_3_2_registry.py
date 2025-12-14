
# IMPLEMENTATION PROTOTYPE (Agent D_6_3_2)
# Task 6.3.2: Configurable Registry Implementation

import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ModelConfig:
    id: str
    provider: str
    cost: float

class RegistryLoader:
    def __init__(self, config_path: str = "lattice.yaml"):
        self.config_path = Path(config_path)
        self.models: Dict[str, ModelConfig] = {}

    def load(self):
        print(f"[REGISTRY] Loading from {self.config_path}...")
        if not self.config_path.exists():
            print("[WARN] Config file not found, using defaults.")
            self._load_defaults()
            return

        with open(self.config_path) as f:
            data = yaml.safe_load(f) or {}

        # Parse 'models' section
        for m in data.get("models", []):
            self.models[m['id']] = ModelConfig(
                id=m['id'],
                provider=m.get('provider', 'unknown'),
                cost=m.get('cost', {}).get('input', 0.0)
            )
            print(f"[REGISTRY] Loaded custom model: {m['id']}")

    def _load_defaults(self):
        self.models['gpt-4o'] = ModelConfig('gpt-4o', 'openai', 2.5)
        print("[REGISTRY] Loaded default: gpt-4o")

if __name__ == "__main__":
    loader = RegistryLoader()
    loader.load()
