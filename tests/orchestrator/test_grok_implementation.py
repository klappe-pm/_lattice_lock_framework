import os
from unittest.mock import AsyncMock, patch

import pytest

from lattice_lock.orchestrator.providers.xai import GrokAPIClient


@pytest.fixture
def mock_xai_env():
    """
    Pytest fixture that temporarily sets the XAI_API_KEY environment variable to "sk-grok-test" for the duration of a test.

    The original environment is restored after the fixture finishes.
    """
    with patch.dict(os.environ, {"XAI_API_KEY": "sk-grok-test"}):
        yield


@pytest.mark.asyncio
async def test_initialization(mock_xai_env):
    client = GrokAPIClient()
    assert client.api_key == "sk-grok-test"
    assert "api.x.ai" in client.base_url


@pytest.mark.asyncio
async def test_chat_completion_success(mock_xai_env):
    """
    Verifies that GrokAPIClient.chat_completion correctly parses a simple assistant message and includes the expected authorization header and model in the outgoing request payload.

    Sets up a client with a mocked _make_request that returns a single assistant message and usage, calls chat_completion with model "grok-beta", and asserts that the returned response has content "I am Grok", provider "xai", and model "grok-beta". Also inspects the mocked request arguments to assert the Authorization header is "Bearer sk-grok-test" and the payload's "model" field is "grok-beta".
    """
    client = GrokAPIClient()
    mock_response = {
        "choices": [{"message": {"content": "I am Grok"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 8},
    }
    client._make_request = AsyncMock(return_value=(mock_response, 100))

    response = await client.chat_completion(
        model="grok-beta", messages=[{"role": "user", "content": "Who are you?"}]
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
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {"function": {"name": "calculate", "arguments": '{"expr": "2+2"}'}}
                    ]
                }
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 10},
    }
    client._make_request = AsyncMock(return_value=(mock_response, 120))

    response = await client.chat_completion(
        model="grok-beta",
        messages=[{"role": "user", "content": "Calculate 2+2"}],
        functions=[
            {
                "name": "calculate",
                "parameters": {"type": "object", "properties": {"expr": {"type": "string"}}},
            }
        ],
    )

    assert response.function_call is not None
    assert response.function_call.name == "calculate"
    assert response.function_call.arguments == {"expr": "2+2"}

    call_args = client._make_request.call_args
    payload = call_args[0][3]
    assert "tools" in payload
    assert payload["tools"][0]["function"]["name"] == "calculate"
