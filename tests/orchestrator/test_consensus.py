from unittest.mock import MagicMock

import pytest

from lattice_lock.orchestrator.consensus import ConsensusOrchestrator
from lattice_lock.orchestrator.types import APIResponse, TaskType, TokenUsage


@pytest.fixture
def mock_orchestrator():
    return MagicMock()


@pytest.fixture
def consensus_orch(mock_orchestrator):
    return ConsensusOrchestrator(orchestrator=mock_orchestrator)


@pytest.mark.asyncio
async def test_run_consensus_basic(consensus_orch, mock_orchestrator):
    prompt = "What is 2+2?"

    # Mock analyzer
    mock_req = MagicMock()
    mock_req.task_type = TaskType.GENERAL

    async def mock_analyze(*args, **kwargs):
        return mock_req

    mock_orchestrator.analyzer.analyze_async.side_effect = mock_analyze

    # Mock registry and scorer
    mock_orchestrator.registry.models = {"m1": MagicMock(), "m2": MagicMock()}
    mock_orchestrator.scorer.score.return_value = 0.9
    mock_orchestrator.selector.select_best_model.return_value = "synth"

    # Mock route_request
    async def mock_route(*args, **kwargs):
        model_id = kwargs.get("model_id") or "synth"
        return APIResponse(
            content=f"Response from {model_id}",
            model=model_id,
            provider="openai",
            usage=TokenUsage(0, 0, 0, 0.1),
            latency_ms=10,
        )

    mock_orchestrator.route_request.side_effect = mock_route

    result = await consensus_orch.run_consensus(prompt, num_models=2)

    assert "synthesis" in result
    assert result["synthesizer_model"] == "synth"
    assert len(result["individual_responses"]) == 2
    assert result["total_cost"] == pytest.approx(0.3)  # 0.1 * 3
