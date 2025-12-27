
import os
import pytest
from unittest.mock import AsyncMock, patch
from lattice_lock.orchestrator.providers.anthropic import AnthropicAPIClient
from lattice_lock.orchestrator.types import APIResponse

@pytest.fixture
def mock_anthropic_env():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test"}):
        yield

@pytest.fixture
def mock_dial_env():
    with patch.dict(os.environ, {"DIAL_API_KEY": "sk-dial-test"}):
        yield

@pytest.mark.asyncio
async def test_initialization_direct(mock_anthropic_env):
    client = AnthropicAPIClient()
    assert client.api_key == "sk-ant-test"
    assert "api.anthropic.com" in client.base_url
    assert not client.use_dial

@pytest.mark.asyncio
async def test_initialization_dial(mock_dial_env):
    client = AnthropicAPIClient(use_dial=True)
    assert client.api_key == "sk-dial-test"
    assert "dial.api.endpoint" in client.base_url
    assert client.use_dial

@pytest.mark.asyncio
async def test_direct_completion_success(mock_anthropic_env):
    client = AnthropicAPIClient()
    mock_response = {
        "content": [{"text": "Hello Claude", "type": "text"}],
        "usage": {"input_tokens": 10, "output_tokens": 5}
    }
    client._make_request = AsyncMock(return_value=(mock_response, 120))
    
    response = await client.chat_completion(
        model="claude-3",
        messages=[
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"}
        ]
    )
    
    assert response.content == "Hello Claude"
    assert response.provider == "anthropic"
    assert response.usage["input_tokens"] == 10
    
    # Verify system message extraction
    call_args = client._make_request.call_args
    headers = call_args[0][2]
    payload = call_args[0][3]
    
    assert headers["x-api-key"] == "sk-ant-test"
    assert payload["system"] == "You are helpful"
    assert len(payload["messages"]) == 1
    assert payload["messages"][0]["role"] == "user"

@pytest.mark.asyncio
async def test_direct_tool_use(mock_anthropic_env):
    client = AnthropicAPIClient()
    mock_response = {
        "content": [{
            "type": "tool_use",
            "name": "get_weather",
            "input": {"location": "Paris"}
        }],
        "usage": {"input_tokens": 20, "output_tokens": 10}
    }
    client._make_request = AsyncMock(return_value=(mock_response, 150))
    
    response = await client.chat_completion(
        model="claude-3",
        messages=[{"role": "user", "content": "Weather?"}],
        functions=[{"name": "get_weather", "parameters": {}}]
    )
    
    assert response.function_call is not None
    assert response.function_call.name == "get_weather"
    assert response.function_call.arguments == {"location": "Paris"}

@pytest.mark.asyncio
async def test_dial_completion(mock_dial_env):
    client = AnthropicAPIClient(use_dial=True)
    mock_response = {
        "choices": [{"message": {"content": "Hello DIAL"}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 5}
    }
    client._make_request = AsyncMock(return_value=(mock_response, 80))
    
    response = await client.chat_completion(
        model="gpt-4-dial",
        messages=[{"role": "user", "content": "Hi"}]
    )
    
    assert response.content == "Hello DIAL"
    assert response.provider == "dial"
    
    # Verify OpenAI format payload
    call_args = client._make_request.call_args
    payload = call_args[0][3]
    assert "messages" in payload
    assert "model" in payload
