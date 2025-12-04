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

from lattice_lock_orchestrator import (
    ModelOrchestrator,
    TaskType,
    ModelProvider,
    APIResponse,
    ModelRegistry,
    ModelScorer,
    TaskAnalyzer,
)
from lattice_lock_orchestrator.types import TaskRequirements, ModelCapabilities

__version__ = "1.0.0"

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
]
