"""
Lattice Lock Framework

A governance-first framework for AI-assisted software development.
Provides intelligent orchestration of Large Language Models (LLMs).

Usage:
    from lattice_lock import ModelOrchestrator
    orchestrator = ModelOrchestrator()
    response = await orchestrator.route_request(prompt)
"""

from pathlib import Path

# Read version from version.txt
_version_file = Path(__file__).parent / "version.txt"
if _version_file.exists():
    __version__ = _version_file.read_text().strip()
else:
    # Fallback to parent directory version.txt
    _parent_version_file = Path(__file__).parent.parent / "version.txt"
    if _parent_version_file.exists():
        __version__ = _parent_version_file.read_text().strip()
    else:
        __version__ = "2.1.0"

# Core orchestrator exports
# Types module
from lattice_lock import types
from lattice_lock.orchestrator import (
    APIResponse,
    ModelOrchestrator,
    ModelProvider,
    ModelRegistry,
    ModelScorer,
    TaskAnalyzer,
    TaskType,
)

__all__ = [
    "__version__",
    "ModelOrchestrator",
    "TaskType",
    "ModelProvider",
    "APIResponse",
    "ModelRegistry",
    "ModelScorer",
    "TaskAnalyzer",
    "types",
]
