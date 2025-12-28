"""
Task Analysis Type Definitions.
"""
from dataclasses import dataclass, field
from typing import Any

from ..types import TaskType


@dataclass
class TaskAnalysis:
    """
    Comprehensive task analysis result with multi-label support.

    Attributes:
        primary_type: The most likely task type
        secondary_types: Additional relevant task types sorted by confidence
        scores: Raw confidence scores for each task type (0.0-1.0)
        features: Extracted features from the prompt
        complexity: Estimated complexity ("simple", "moderate", "complex")
        min_context_window: Minimum recommended context window
    """

    primary_type: TaskType
    secondary_types: list[TaskType] = field(default_factory=list)
    scores: dict[TaskType, float] = field(default_factory=dict)
    features: dict[str, Any] = field(default_factory=dict)
    complexity: str = "moderate"
    min_context_window: int = 4000
