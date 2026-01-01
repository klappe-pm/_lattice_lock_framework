from unittest.mock import MagicMock, mock_open, patch

import pytest

from lattice_lock.orchestrator.chain import ChainOrchestrator, Pipeline, PipelineStep
from lattice_lock.orchestrator.types import APIResponse, TokenUsage


@pytest.fixture
def mock_orchestrator():
    return MagicMock()


@pytest.fixture
def chain_orch(mock_orchestrator):
    return ChainOrchestrator(orchestrator=mock_orchestrator)


@pytest.mark.asyncio
async def test_run_pipeline_basic(chain_orch, mock_orchestrator):
    pipeline = Pipeline(
        "Test",
        [
            PipelineStep("Step 1", "Hello {{name}}", output_key="out1"),
            PipelineStep("Step 2", "Got {{out1}}", output_key="out2"),
        ],
    )

    # We need to return coro/awaitable for route_request as it's awaited
    async def mock_resp1(*args, **kwargs):
        return APIResponse(
            content="Response 1",
            model="m1",
            provider="p1",
            usage=TokenUsage(0, 0, 0, 0.1),
            latency_ms=10,
        )

    async def mock_resp2(*args, **kwargs):
        return APIResponse(
            content="Response 2",
            model="m2",
            provider="p2",
            usage=TokenUsage(0, 0, 0, 0.2),
            latency_ms=10,
        )

    mock_orchestrator.route_request.side_effect = [mock_resp1(), mock_resp2()]

    result = await chain_orch.run_pipeline(pipeline, {"name": "World"})

    assert result["final_context"]["out1"] == "Response 1"
    assert result["final_context"]["out2"] == "Response 2"
    assert result["step_results"]["Step 1"]["content"] == "Response 1"
    assert mock_orchestrator.route_request.call_count == 2

    # Verify template rendering
    args, kwargs = mock_orchestrator.route_request.call_args_list[0]
    assert kwargs["prompt"] == "Hello World"

    args, kwargs = mock_orchestrator.route_request.call_args_list[1]
    assert kwargs["prompt"] == "Got Response 1"


def test_from_yaml(chain_orch):
    yaml_content = """
name: "Test Pipeline"
steps:
  - name: "S1"
    prompt: "P1"
  - name: "S2"
    prompt: "P2"
    model_id: "m2"
    output_key: "ok2"
"""
    with patch("builtins.open", mock_open(read_data=yaml_content)):
        pipeline = chain_orch.from_yaml("fake.yaml")

    assert pipeline.name == "Test Pipeline"
    assert len(pipeline.steps) == 2
    assert pipeline.steps[0].name == "S1"
    assert pipeline.steps[1].model_id == "m2"
    assert pipeline.steps[1].output_key == "ok2"
