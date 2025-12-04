"""
Lattice-Lock Orchestrator

Intelligent model routing across 63 AI models from 8 providers.
"""

from pathlib import Path

from .core import ModelOrchestrator
from .types import TaskType, ModelProvider, APIResponse
from .registry import ModelRegistry
from .scorer import ModelScorer, TaskAnalyzer


def _get_version() -> str:
    """Read version from version.txt file.

    Looks for version.txt in the project root (three levels up from this file).
    Falls back to a default version if the file cannot be found.
    """
    version_file = Path(__file__).parent.parent.parent / "version.txt"
    try:
        return version_file.read_text().strip()
    except FileNotFoundError:
        return "0.0.0"


__version__ = _get_version()

__all__ = [
    "ModelOrchestrator",
    "TaskType",
    "ModelProvider",
    "APIResponse",
    "ModelRegistry",
    "ModelScorer",
    "TaskAnalyzer",
]
