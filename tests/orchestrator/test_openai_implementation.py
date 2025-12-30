import os
from unittest.mock import AsyncMock, patch

import pytest
from lattice_lock.exceptions import ProviderUnavailableError
from lattice_lock.orchestrator.providers.openai import OpenAIAPIClient
from lattice_lock.orchestrator.types import APIResponse


@pytest.fixture
def mock_env():
    """
    Pytest fixture that temporarily sets OPENAI_API_KEY to "sk-test-key" in the environment.

    Patches os.environ so tests run with OPENAI_API_KEY="sk-test-key" and restores the original environment after the test completes.
    """
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
        yield


@pytest.mark.asyncio
async def test_initialization(mock_env):
    config = AsyncMock()
    client = OpenAIAPIClient(config=config)
    assert client.api_key == "sk-test-key"


@pytest.mark.asyncio
async def test_initialization_failure():
    with patch.dict(os.environ, {}, clear=True):
        config = AsyncMock()
        with pytest.raises(ProviderUnavailableError, match="OPENAI_API_KEY"):
            OpenAIAPIClient(config=config)


@pytest.mark.asyncio
async def test_chat_completion_success(mock_env):
    config = AsyncMock()
    client = OpenAIAPIClient(config=config)
    mock_response = {
        "choices": [{"message": {"content": "Hello world"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }
    client._make_request = AsyncMock(return_value=(mock_response, 100))

    response = await client.chat_completion(
        model="gpt-4", messages=[{"role": "user", "content": "Hi"}]
    )

    assert isinstance(response, APIResponse)
    assert response.content == "Hello world"
    assert response.model == "gpt-4"
    assert response.provider == "openai"
    assert response.latency_ms == 100
    assert response.usage["input_tokens"] == 10
    assert response.usage["output_tokens"] == 5


@pytest.mark.asyncio
async def test_chat_completion_with_functions(mock_env):
    config = AsyncMock()
    client = OpenAIAPIClient(config=config)
    mock_response = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {"function": {"name": "get_weather", "arguments": '{"location": "London"}'}}
                    ]
                }
            }
        ],
        "usage": {"prompt_tokens": 15, "completion_tokens": 8},
    }
    client._make_request = AsyncMock(return_value=(mock_response, 120))

    functions = [
        {
            "name": "get_weather",
            "description": "Get weather",
            "parameters": {"type": "object", "properties": {"location": {"type": "string"}}},
        }
    ]

    response = await client.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": "Weather in London?"}],
        functions=functions,
    )

    assert response.function_call is not None
    assert response.function_call.name == "get_weather"
    assert response.function_call.arguments == {"location": "London"}

    # Verify payload construction
    call_args = client._make_request.call_args
    payload = call_args[0][3]
    assert "tools" in payload
    assert payload["tools"][0]["function"]["name"] == "get_weather"


@pytest.mark.asyncio
async def test_chat_completion_tool_choice(mock_env):
    config = AsyncMock()
    client = OpenAIAPIClient(config=config)
    mock_response = {
        "choices": [{"message": {"content": "forced"}}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0},
    }
    client._make_request = AsyncMock(return_value=(mock_response, 50))

    await client.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": "test"}],
        functions=[{"name": "func", "parameters": {}}],
        tool_choice={"type": "function", "function": {"name": "func"}},
    )

    call_args = client._make_request.call_args
    payload = call_args[0][3]
    assert payload["tool_choice"] == {"type": "function", "function": {"name": "func"}}
