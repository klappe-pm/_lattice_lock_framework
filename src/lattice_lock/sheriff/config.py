import os
from dataclasses import dataclass, field
from typing import Any

from enum import Enum

import yaml


class ViolationSeverity(Enum):
    """Severity levels for Sheriff violations."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SheriffConfig:
    forbidden_imports: list[str] = field(default_factory=list)
    enforce_type_hints: bool = True
    target_version: str = "current"
    custom_rules: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str = "lattice.yaml") -> "SheriffConfig":
        if not os.path.exists(path):
            return cls()

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}

            config_data = data.get("config", {})

            return cls(
                forbidden_imports=config_data.get("forbidden_imports", []),
                enforce_type_hints=config_data.get("enforce_type_hints", True),
                target_version=config_data.get("target_version", "current"),
                custom_rules=config_data.get("custom_rules", {}),
            )
        except Exception:
            # Fallback to defaults on error
            return cls()
