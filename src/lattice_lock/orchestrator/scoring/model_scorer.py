"""
Model Scorer for the Lattice Lock Orchestrator.

This module provides:
- ModelScorer: Scores models based on capabilities and requirements
"""

import logging
from pathlib import Path

import yaml

from lattice_lock.config import AppConfig

from ..analysis.types import TaskAnalysis
from ..types import ModelCapabilities, TaskRequirements

logger = logging.getLogger(__name__)


class ModelScorer:
    """
    Scores models based on their capabilities and task requirements.
    """

    def __init__(self, config: AppConfig | None = None, config_path: str | None = None):
        """
        Initialize ModelScorer.

        Args:
            config: AppConfig instance
            config_path: Optional path to scorer config file
        """
        self.app_config = config

        if config_path is None:
            # Look for scorer_config.yaml in the parent directory (orchestrator)
            # or in current directory if refactored location differs.
            # Assuming file is in relevant path.
            # Original code looked in parent.parent
            config_path = str(Path(__file__).parent.parent / "scorer_config.yaml")

        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        """Load scoring weights from YAML config."""
        try:
            # Use safe open
            if Path(self.config_path).exists():
                with open(self.config_path) as f:
                    self.config = yaml.safe_load(f)
            else:
                raise FileNotFoundError(f"{self.config_path} not found")

        except Exception as e:
            logger.warning(
                f"Failed to load scorer config from {self.config_path}: {e}. Using hardcoded fallbacks."
            )
            self.config = {
                "priority_weights": {
                    "quality": {"reasoning": 0.3, "coding": 0.2, "base": 0.5},
                    "speed": {"speed": 0.5, "base": 0.5},
                    "cost": {"cost": 0.5, "base": 0.5},
                    "balanced": {"reasoning": 0.2, "coding": 0.2, "speed": 0.1, "base": 0.5},
                },
                "analysis_weights": {
                    "base": 0.5,
                    "primary_task": 0.3,
                    "secondary_task": 0.1,
                    "complexity_boost": 0.1,
                },
                "task_boosts": {
                    "CODE_GENERATION": {"coding": 0.2},
                    "DEBUGGING": {"coding": 0.2},
                    "REASONING": {"reasoning": 0.2},
                    "ARCHITECTURAL_DESIGN": {"reasoning": 0.2},
                },
                "max_blended_cost": 60.0,
            }

    def score(self, model: ModelCapabilities, requirements: TaskRequirements) -> float:
        """
        Calculates a fitness score for a model given the task requirements.
        """
        if requirements.min_context > model.context_window:
            return 0.0
        if requirements.require_vision and not model.supports_vision:
            return 0.0
        if requirements.require_functions and not model.supports_function_calling:
            return 0.0

        weights = self.config["priority_weights"].get(
            requirements.priority, self.config["priority_weights"]["balanced"]
        )
        score = weights.get("base", 0.5)

        if requirements.priority == "quality":
            score += (model.reasoning_score / 100.0) * weights.get("reasoning", 0.3)
            score += (model.coding_score / 100.0) * weights.get("coding", 0.2)
        elif requirements.priority == "speed":
            score += (model.speed_rating / 10.0) * weights.get("speed", 0.5)
        elif requirements.priority == "cost":
            cost_factor = 1.0 - (model.blended_cost / self.config.get("max_blended_cost", 60.0))
            score += max(0, cost_factor) * weights.get("cost", 0.5)
        else:  # Balanced
            score += (model.reasoning_score / 100.0) * weights.get("reasoning", 0.2)
            score += (model.coding_score / 100.0) * weights.get("coding", 0.2)
            score += (model.speed_rating / 10.0) * weights.get("speed", 0.1)

        # Task specific boosts
        boosts = self.config["task_boosts"].get(requirements.task_type.name, {})
        if "coding" in boosts:
            score += (model.coding_score / 100.0) * boosts["coding"]
        if "reasoning" in boosts:
            score += (model.reasoning_score / 100.0) * boosts["reasoning"]

        return min(1.0, score)

    def score_with_analysis(self, model: ModelCapabilities, analysis: TaskAnalysis) -> float:
        """
        Scores a model using full TaskAnalysis for multi-label support.
        """
        if analysis.min_context_window > model.context_window:
            return 0.0
        if analysis.features.get("requires_vision") and not model.supports_vision:
            return 0.0
        if (
            analysis.features.get("requires_function_calling")
            and not model.supports_function_calling
        ):
            return 0.0

        aw = self.config["analysis_weights"]
        score = aw.get("base", 0.5)

        model_task_scores = model.task_scores
        primary_match = model_task_scores.get(analysis.primary_type, 0.5)
        score += primary_match * aw.get("primary_task", 0.3)

        for secondary_type in analysis.secondary_types[:2]:
            secondary_match = model_task_scores.get(secondary_type, 0.5)
            score += secondary_match * aw.get("secondary_task", 0.1)

        priority = analysis.features.get("priority", "balanced")
        _weights = self.config["priority_weights"].get(
            priority, self.config["priority_weights"]["balanced"]
        )  # noqa: F841 - loaded for future use

        if priority == "quality":
            score += (model.reasoning_score / 100.0) * 0.1
        elif priority == "speed":
            score += (model.speed_rating / 10.0) * 0.2
        elif priority == "cost":
            cost_factor = 1.0 - (model.blended_cost / self.config.get("max_blended_cost", 60.0))
            score += max(0, cost_factor) * 0.2

        if analysis.complexity == "complex":
            score += (model.reasoning_score / 100.0) * aw.get("complexity_boost", 0.1)

        return min(1.0, score)
