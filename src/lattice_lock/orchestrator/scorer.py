"""
DEPRECATED: Import from lattice_lock.orchestrator.analysis and lattice_lock.orchestrator.scoring instead.
"""
import warnings

# Re-export classes from new locations
from .analysis import TaskAnalyzer, TaskAnalysis, SemanticRouter
from .scoring import ModelScorer

warnings.warn(
    "Importing from scorer.py is deprecated. Use lattice_lock.orchestrator.analysis or lattice_lock.orchestrator.scoring instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "TaskAnalyzer",
    "TaskAnalysis",
    "SemanticRouter",
    "ModelScorer",
]
