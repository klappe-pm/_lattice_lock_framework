import pytest
from unittest.mock import AsyncMock, MagicMock
from lattice_lock.orchestrator.scorer import TaskAnalyzer, SemanticRouter
from lattice_lock.orchestrator.types import TaskType, APIResponse

@pytest.mark.asyncio
async def test_semantic_router_calls_client():
    mock_client = AsyncMock()
    mock_client.chat_completion.return_value = APIResponse(
        content="DEBUGGING",
        model="gpt-4o-mini",
        provider="openai",
        usage={},
        latency_ms=100
    )
    
    router = SemanticRouter(client=mock_client)
    result = await router.route("There is a bug in my code")
    
    assert result == TaskType.DEBUGGING
    mock_client.chat_completion.assert_awaited_once()

@pytest.mark.asyncio
async def test_semantic_router_fallback_to_general():
    mock_client = AsyncMock()
    mock_client.chat_completion.return_value = APIResponse(
        content="I am not sure",
        model="gpt-4o-mini",
        provider="openai",
        usage={},
        latency_ms=100
    )
    
    router = SemanticRouter(client=mock_client)
    result = await router.route("Random prompt")
    
    assert result == TaskType.GENERAL

@pytest.mark.asyncio
async def test_task_analyzer_engages_semantic_router():
    mock_client = AsyncMock()
    mock_client.chat_completion.return_value = APIResponse(
        content="CODE_GENERATION",
        model="gpt-4o-mini",
        provider="openai",
        usage={},
        latency_ms=100
    )
    
    analyzer = TaskAnalyzer(router_client=mock_client)
    
    # Needs a prompt that doesn't trigger heuristics easily but is long enough (>10 chars)
    # and max_heuristic_score < 0.5
    prompt = "please help me with something subtle"
    
    # We expect analyze_async to call the semantic router
    requirements = await analyzer.analyze_async(prompt)
    
    assert requirements.task_type == TaskType.CODE_GENERATION
    mock_client.chat_completion.assert_awaited_once()
