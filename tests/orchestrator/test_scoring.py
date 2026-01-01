"""
Tests for Model Scorer.
"""

from unittest.mock import Mock

import pytest

from lattice_lock.config import AppConfig
from lattice_lock.orchestrator.scoring.model_scorer import ModelScorer
from lattice_lock.orchestrator.types import (
    ModelCapabilities,
    ModelProvider,
    TaskRequirements,
    TaskType,
)


@pytest.fixture
def mock_config():
    return Mock(spec=AppConfig)


@pytest.fixture
def sample_model():
    return ModelCapabilities(
        name="test-model",
        api_name="test-model",
        provider=ModelProvider.OPENAI,
        context_window=10000,
        input_cost=10.0,
        output_cost=30.0,
        supports_vision=True,
        supports_function_calling=True,
        reasoning_score=90,
        coding_score=90,
        speed_rating=8,
    )


def test_scorer_initialization(mock_config):
    """Test scorer loads config."""
    scorer = ModelScorer(config=mock_config)
    assert scorer.config


def test_score_basic_match(mock_config, sample_model):
    """Test scoring a compatible task."""
    scorer = ModelScorer(config=mock_config)
    req = TaskRequirements(task_type=TaskType.GENERAL, min_context=4000)

    score = scorer.score(sample_model, req)
    assert 0.0 < score <= 1.0


def test_score_context_failure(mock_config, sample_model):
    """Test scoring 0 if context too small."""
    scorer = ModelScorer(config=mock_config)
    req = TaskRequirements(task_type=TaskType.GENERAL, min_context=20000)  # Larger than model's 10k

    score = scorer.score(sample_model, req)
    assert score == 0.0


def test_score_vision_failure(mock_config, sample_model):
    """Test scoring 0 if vision required but supported."""
    scorer = ModelScorer(config=mock_config)
    req = TaskRequirements(task_type=TaskType.VISION, min_context=4000, require_vision=True)

    # Sample model supports vision -> should be > 0
    score = scorer.score(sample_model, req)
    assert score > 0.0

    # Create non-vision model
    blind_model = ModelCapabilities(
        name="blind",
        api_name="blind",
        provider=ModelProvider.OPENAI,
        context_window=10000,
        supports_vision=False,
        reasoning_score=10,
        coding_score=10,
        speed_rating=10,
        input_cost=1.0,
        output_cost=1.0,
    )
    score_blind = scorer.score(blind_model, req)
    assert score_blind == 0.0


def test_priority_impact(mock_config, sample_model):
    """Test that priority changes score."""
    scorer = ModelScorer(config=mock_config)

    # Create a slow but smart model
    smart_slow_model = ModelCapabilities(
        name="smart",
        api_name="smart",
        provider=ModelProvider.OPENAI,
        context_window=10000,
        reasoning_score=99,
        coding_score=99,
        speed_rating=1,
        input_cost=50.0,
        output_cost=50.0,
    )

    req_qual = TaskRequirements(task_type=TaskType.GENERAL, min_context=1000, priority="quality")
    req_speed = TaskRequirements(task_type=TaskType.GENERAL, min_context=1000, priority="speed")

    score_quality = scorer.score(smart_slow_model, req_qual)
    score_speed = scorer.score(smart_slow_model, req_speed)

    assert score_quality > score_speed
