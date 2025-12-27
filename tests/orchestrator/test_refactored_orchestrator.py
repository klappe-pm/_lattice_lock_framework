from unittest.mock import AsyncMock, patch

import pytest
from lattice_lock.orchestrator.core import ModelOrchestrator
from lattice_lock.orchestrator.types import (
    APIResponse,
    ModelCapabilities,
    ModelProvider,
    TaskRequirements,
    TaskType,
    TokenUsage,
)


@pytest.fixture
def mock_registry():
    with patch("lattice_lock.orchestrator.core.ModelRegistry") as MockRegistry:
        registry = MockRegistry.return_value

        # Setup specific models for retrieval
        def get_model_side_effect(model_id):
            if model_id == "primary-model":
                return ModelCapabilities(
                    name="Primary",
                    api_name="primary-model",
                    provider=ModelProvider.OPENAI,
                    context_window=8000,
                    input_cost=10.0,
                    output_cost=30.0,
                    reasoning_score=90.0,
                    coding_score=90.0,
                    speed_rating=8.0,
                )
            if model_id == "fallback-model":
                return ModelCapabilities(
                    name="Fallback",
                    api_name="fallback-model",
                    provider=ModelProvider.ANTHROPIC,
                    context_window=100000,
                    input_cost=10.0,
                    output_cost=30.0,
                    reasoning_score=95.0,
                    coding_score=85.0,
                    speed_rating=7.0,
                )
            return None

        registry.get_model.side_effect = get_model_side_effect
        yield registry


@pytest.fixture
def mock_client_pool():
    with patch("lattice_lock.orchestrator.core.ClientPool") as MockClientPool:
        pool = MockClientPool.return_value
        yield pool


@pytest.fixture
def mock_executor():
    with patch("lattice_lock.orchestrator.core.ConversationExecutor") as MockExecutor:
        executor = MockExecutor.return_value
        yield executor


@pytest.fixture
def mock_selector():
    with patch("lattice_lock.orchestrator.core.ModelSelector") as MockSelector:
        selector = MockSelector.return_value
        yield selector


@pytest.fixture
def mock_analyzer():
    with patch("lattice_lock.orchestrator.core.TaskAnalyzer") as MockAnalyzer:
        analyzer = MockAnalyzer.return_value
        yield analyzer


@pytest.mark.asyncio
async def test_orchestrator_initialization(
    mock_registry, mock_client_pool, mock_executor, mock_selector, mock_analyzer
):
    """Verify orchestrator initializes all components correctly."""
    orchestrator = ModelOrchestrator()
    assert orchestrator.registry
    assert orchestrator.client_pool
    assert orchestrator.executor
    assert orchestrator.selector


@pytest.mark.asyncio
async def test_route_request_success(
    mock_registry, mock_client_pool, mock_executor, mock_selector, mock_analyzer
):
    """Verify route_request flow calls selector, client pool and executor."""
    orchestrator = ModelOrchestrator()

    # Setup mocks
    mock_reqs = TaskRequirements(task_type=TaskType.GENERAL)
    mock_analyzer.analyze_async = AsyncMock(return_value=mock_reqs)
    mock_selector.select_best_model.return_value = "primary-model"

    mock_client = AsyncMock()
    mock_client_pool.get_client.return_value = mock_client

    expected_response = APIResponse(
        content="Success",
        model="primary-model",
        provider="openai",
        usage=TokenUsage(10, 10, 20, 0.05),
        latency_ms=100,
    )
    mock_executor.execute = AsyncMock(return_value=expected_response)

    # Execute
    response = await orchestrator.route_request("Test prompt")

    # Verify interaction
    mock_analyzer.analyze_async.assert_called_once_with("Test prompt")
    mock_selector.select_best_model.assert_called_once_with(mock_reqs)
    mock_registry.get_model.assert_called_with("primary-model")
    mock_client_pool.get_client.assert_called_with("openai")
    mock_executor.execute.assert_called_once()
    assert response == expected_response


@pytest.mark.asyncio
async def test_route_request_fallback(
    mock_registry, mock_client_pool, mock_executor, mock_selector, mock_analyzer
):
    """Verify fallback logic when primary fails."""
    orchestrator = ModelOrchestrator()

    # Setup mocks
    mock_reqs = TaskRequirements(task_type=TaskType.GENERAL)
    mock_analyzer.analyze_async = AsyncMock(return_value=mock_reqs)
    mock_selector.select_best_model.return_value = "primary-model"
    mock_selector.get_fallback_chain.return_value = ["fallback-model"]  # Chain includes fallback

    # Primary client raises error
    mock_executor.execute = AsyncMock(
        side_effect=[
            ValueError("Primary Failed"),  # First call (primary)
            APIResponse(  # Second call (fallback)
                content="Fallback Success",
                model="fallback-model",
                provider="anthropic",
                usage=TokenUsage(10, 10, 20, 0.05),
                latency_ms=100,
            ),
        ]
    )

    # Execute
    response = await orchestrator.route_request("Test prompt")

    # Verify interaction
    assert response.content == "Fallback Success"
    assert mock_executor.execute.call_count == 2

    # Check fallback chain requested
    mock_selector.get_fallback_chain.assert_called_once()
