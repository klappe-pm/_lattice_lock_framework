"""
Tests for ModelCapabilities and related types.

Task 6.1.2 - Ensures CLI and orchestrator work correctly with model capabilities.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lattice_lock.orchestrator.registry import ModelRegistry
from lattice_lock.orchestrator.types import (
    ModelCapabilities,
    ModelProvider,
    TaskRequirements,
    TaskType,
)


class TestTaskType:
    """Tests for TaskType enum."""

    def test_vision_task_type_exists(self):
        """TaskType.VISION should exist in the enum."""
        assert hasattr(TaskType, "VISION")
        assert TaskType.VISION is not None

    def test_all_expected_task_types_exist(self):
        """All expected task types should be defined."""
        expected_types = [
            "CODE_GENERATION",
            "DEBUGGING",
            "ARCHITECTURAL_DESIGN",
            "DOCUMENTATION",
            "TESTING",
            "DATA_ANALYSIS",
            "GENERAL",
            "REASONING",
            "VISION",
        ]
        for task_type in expected_types:
            assert hasattr(TaskType, task_type), f"TaskType.{task_type} should exist"


class TestModelCapabilities:
    """Tests for ModelCapabilities dataclass."""

    @pytest.fixture
    def sample_model(self):
        """Create a sample model for testing."""
        # Calculate task scores similar to how ModelRegistry does
        coding_norm = 85.0 / 100.0
        reasoning_norm = 90.0 / 100.0
        task_scores = {
            TaskType.CODE_GENERATION: coding_norm,
            TaskType.DEBUGGING: coding_norm * 0.9 + reasoning_norm * 0.1,
            TaskType.ARCHITECTURAL_DESIGN: reasoning_norm * 0.7 + coding_norm * 0.3,
            TaskType.DOCUMENTATION: (coding_norm + reasoning_norm) / 2,
            TaskType.TESTING: coding_norm * 0.8 + reasoning_norm * 0.2,
            TaskType.DATA_ANALYSIS: reasoning_norm * 0.6 + coding_norm * 0.4,
            TaskType.GENERAL: (coding_norm + reasoning_norm) / 2,
            TaskType.REASONING: reasoning_norm,
            TaskType.VISION: 1.0,  # supports_vision=True
            TaskType.SECURITY_AUDIT: coding_norm * 0.7 + reasoning_norm * 0.3,
            TaskType.CREATIVE_WRITING: reasoning_norm * 0.8,
            TaskType.TRANSLATION: reasoning_norm * 0.9,
        }
        return ModelCapabilities(
            name="Test Model",
            api_name="test-model",
            provider=ModelProvider.OPENAI,
            context_window=128000,
            input_cost=5.0,
            output_cost=15.0,
            reasoning_score=90.0,
            coding_score=85.0,
            speed_rating=8.0,
            supports_vision=True,
            supports_function_calling=True,
            task_scores=task_scores,
        )

    @pytest.fixture
    def low_score_model(self):
        """Create a model with low scores for testing thresholds."""
        # Calculate task scores similar to how ModelRegistry does
        coding_norm = 70.0 / 100.0
        reasoning_norm = 60.0 / 100.0
        task_scores = {
            TaskType.CODE_GENERATION: coding_norm,
            TaskType.DEBUGGING: coding_norm * 0.9 + reasoning_norm * 0.1,
            TaskType.ARCHITECTURAL_DESIGN: reasoning_norm * 0.7 + coding_norm * 0.3,
            TaskType.DOCUMENTATION: (coding_norm + reasoning_norm) / 2,
            TaskType.TESTING: coding_norm * 0.8 + reasoning_norm * 0.2,
            TaskType.DATA_ANALYSIS: reasoning_norm * 0.6 + coding_norm * 0.4,
            TaskType.GENERAL: (coding_norm + reasoning_norm) / 2,
            TaskType.REASONING: reasoning_norm,
            TaskType.VISION: 0.0,  # supports_vision=False
            TaskType.SECURITY_AUDIT: coding_norm * 0.7 + reasoning_norm * 0.3,
            TaskType.CREATIVE_WRITING: reasoning_norm * 0.8,
            TaskType.TRANSLATION: reasoning_norm * 0.9,
        }
        return ModelCapabilities(
            name="Low Score Model",
            api_name="low-score-model",
            provider=ModelProvider.OLLAMA,
            context_window=4096,
            input_cost=0.0,
            output_cost=0.0,
            reasoning_score=60.0,
            coding_score=70.0,
            speed_rating=5.0,
            supports_vision=False,
            supports_function_calling=False,
            task_scores=task_scores,
        )

    def test_supports_reasoning_property_exists(self, sample_model):
        """ModelCapabilities should have supports_reasoning property."""
        assert hasattr(sample_model, "supports_reasoning")

    def test_supports_reasoning_true_for_high_score(self, sample_model):
        """supports_reasoning should be True when reasoning_score >= 85."""
        assert sample_model.supports_reasoning is True

    def test_supports_reasoning_false_for_low_score(self, low_score_model):
        """supports_reasoning should be False when reasoning_score < 85."""
        assert low_score_model.supports_reasoning is False

    def test_code_specialized_property_exists(self, sample_model):
        """ModelCapabilities should have code_specialized property."""
        assert hasattr(sample_model, "code_specialized")

    def test_code_specialized_true_for_high_score(self, sample_model):
        """code_specialized should be True when coding_score >= 85."""
        assert sample_model.code_specialized is True

    def test_code_specialized_false_for_low_score(self, low_score_model):
        """code_specialized should be False when coding_score < 85."""
        assert low_score_model.code_specialized is False

    def test_task_scores_property_exists(self, sample_model):
        """ModelCapabilities should have task_scores property."""
        assert hasattr(sample_model, "task_scores")

    def test_task_scores_returns_dict(self, sample_model):
        """task_scores should return a dictionary."""
        scores = sample_model.task_scores
        assert isinstance(scores, dict)

    def test_task_scores_contains_all_task_types(self, sample_model):
        """task_scores should contain scores for all TaskType values."""
        scores = sample_model.task_scores
        for task_type in TaskType:
            assert task_type in scores, f"task_scores should contain {task_type}"

    def test_task_scores_values_are_normalized(self, sample_model):
        """task_scores values should be between 0 and 1."""
        scores = sample_model.task_scores
        for task_type, score in scores.items():
            assert 0.0 <= score <= 1.0, f"Score for {task_type} should be 0-1, got {score}"

    def test_task_scores_vision_reflects_supports_vision(self, sample_model, low_score_model):
        """VISION task score should be 1.0 if supports_vision, else 0.0."""
        assert sample_model.task_scores[TaskType.VISION] == 1.0
        assert low_score_model.task_scores[TaskType.VISION] == 0.0

    def test_blended_cost_property(self, sample_model):
        """blended_cost should calculate correctly."""
        expected = (sample_model.input_cost * 3 + sample_model.output_cost) / 4
        assert sample_model.blended_cost == expected


class TestModelRegistry:
    """Tests for ModelRegistry and registered models."""

    @pytest.fixture
    def registry(self):
        """Create a ModelRegistry instance."""
        return ModelRegistry()

    def test_registry_has_models(self, registry):
        """Registry should have at least one model."""
        assert len(registry.models) > 0

    def test_all_models_have_required_attributes(self, registry):
        """All registered models should have the required capability attributes."""
        for model_id, model in registry.models.items():
            assert hasattr(model, "supports_reasoning"), f"{model_id} missing supports_reasoning"
            assert hasattr(model, "code_specialized"), f"{model_id} missing code_specialized"
            assert hasattr(model, "task_scores"), f"{model_id} missing task_scores"
            assert hasattr(model, "supports_vision"), f"{model_id} missing supports_vision"
            assert hasattr(
                model, "supports_function_calling"
            ), f"{model_id} missing supports_function_calling"

    def test_all_models_have_valid_task_scores(self, registry):
        """All registered models should have valid task_scores."""
        for model_id, model in registry.models.items():
            scores = model.task_scores
            assert isinstance(scores, dict), f"{model_id} task_scores should be dict"
            for task_type in TaskType:
                assert task_type in scores, f"{model_id} missing score for {task_type}"
                assert 0.0 <= scores[task_type] <= 1.0, f"{model_id} invalid score for {task_type}"

    def test_no_attribute_error_on_model_access(self, registry):
        """Accessing model capabilities should not raise AttributeError."""
        for model_id, model in registry.models.items():
            try:
                _ = model.supports_reasoning
                _ = model.code_specialized
                _ = model.task_scores
                _ = model.supports_vision
                _ = model.supports_function_calling
                _ = model.blended_cost
            except AttributeError as e:
                pytest.fail(f"AttributeError on {model_id}: {e}")


class TestTaskRequirements:
    """Tests for TaskRequirements dataclass."""

    def test_require_vision_attribute_exists(self):
        """TaskRequirements should have require_vision attribute."""
        req = TaskRequirements(task_type=TaskType.VISION)
        assert hasattr(req, "require_vision")

    def test_require_functions_attribute_exists(self):
        """TaskRequirements should have require_functions attribute."""
        req = TaskRequirements(task_type=TaskType.CODE_GENERATION)
        assert hasattr(req, "require_functions")

    def test_default_require_vision_is_false(self):
        """Default require_vision should be False."""
        req = TaskRequirements(task_type=TaskType.GENERAL)
        assert req.require_vision is False

    def test_can_set_require_vision_true(self):
        """Should be able to set require_vision to True."""
        req = TaskRequirements(task_type=TaskType.VISION, require_vision=True)
        assert req.require_vision is True
