
import os
import pytest
from unittest.mock import AsyncMock, patch
from lattice_lock.orchestrator.providers.xai import GrokAPIClient
from lattice_lock.orchestrator.types import APIResponse

@pytest.fixture
def mock_xai_env():
    with patch.dict(os.environ, {"XAI_API_KEY": "sk-grok-test"}):
        yield

@pytest.mark.asyncio
async def test_initialization(mock_xai_env):
    client = GrokAPIClient()
    assert client.api_key == "sk-grok-test"
    assert "api.x.ai" in client.base_url

@pytest.mark.asyncio
async def test_chat_completion_success(mock_xai_env):
    client = GrokAPIClient()
    mock_response = {
        "choices": [{"message": {"content": "I am Grok"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 8}
    }
    client._make_request = AsyncMock(return_value=(mock_response, 100))
    
    response = await client.chat_completion(
        model="grok-beta",
        messages=[{"role": "user", "content": "Who are you?"}]
    )
    
    assert response.content == "I am Grok"
    assert response.provider == "xai"
    assert response.model == "grok-beta"
    
    # Verify payload
    call_args = client._make_request.call_args
    headers = call_args[0][2]
    payload = call_args[0][3]
    
    assert headers["Authorization"] == "Bearer sk-grok-test"
    assert payload["model"] == "grok-beta"

@pytest.mark.asyncio
async def test_chat_completion_with_functions(mock_xai_env):
    client = GrokAPIClient()
    mock_response = {
        "choices": [{"message": {"tool_calls": [{
            "function": {
                "name": "calculate",
                "arguments": '{"expr": "2+2"}'
            }
        }]}}],
        "usage": {"prompt_tokens": 20, "completion_tokens": 10}
    }
    client._make_request = AsyncMock(return_value=(mock_response, 120))
    
    response = await client.chat_completion(
        model="grok-beta",
        messages=[{"role": "user", "content": "Calculate 2+2"}],
        functions=[{
            "name": "calculate",
            "parameters": {"type": "object", "properties": {"expr": {"type": "string"}}}
        }]
    )
    
    assert response.function_call is not None
    assert response.function_call.name == "calculate"
    assert response.function_call.arguments == {"expr": "2+2"}
    
    call_args = client._make_request.call_args
    payload = call_args[0][3]
    assert "tools" in payload
    assert payload["tools"][0]["function"]["name"] == "calculate"
