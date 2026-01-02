"""
Lattice-Lock Framework

A governance-first framework for AI-assisted software development.
Provides intelligent model orchestration across 63 AI models from 8 providers.

Usage:
    from lattice_lock import ModelOrchestrator
    from lattice_lock.types import TaskType, TaskRequirements

    orchestrator = ModelOrchestrator()
    response = await orchestrator.route_request(prompt="...", task_type=TaskType.CODE_GENERATION)
"""

import logging
import os

# Configure logging based on LATTICE_LOG_LEVEL
log_level = os.getenv("LATTICE_LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level, logging.INFO)

# Set library logger level and null handler to avoid "No handler found" warnings
logger = logging.getLogger("lattice_lock")
logger.setLevel(numeric_level)
logger.addHandler(logging.NullHandler())


from pathlib import Path

from lattice_lock.compile import CompilationResult, compile_lattice
from lattice_lock.orchestrator import (
    APIResponse,
    ModelOrchestrator,
    ModelProvider,
    ModelRegistry,
    ModelScorer,
    TaskAnalyzer,
    TaskType,
)
from lattice_lock.orchestrator.types import ModelCapabilities, TaskRequirements
from lattice_lock.sheriff import SheriffResult, Violation, ViolationSeverity, run_sheriff


def _get_version() -> str:
    """Read version from version.txt file.

    Looks for version.txt in the same directory as this file.
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
    "TaskRequirements",
    "ModelProvider",
    "APIResponse",
    "ModelCapabilities",
    "ModelRegistry",
    "ModelScorer",
    "TaskAnalyzer",
    "compile_lattice",
    "CompilationResult",
    "run_sheriff",
    "SheriffResult",
    "Violation",
    "ViolationSeverity",
]
