import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lattice_lock.orchestrator.providers.local import LocalModelClient


@pytest.fixture
def mock_local_env():
    """
    Temporarily sets the CUSTOM_API_URL environment variable for the duration of a test.

    Used as a pytest fixture; yields control while CUSTOM_API_URL is set to "http://test-local:8000" and restores the original environment afterwards.
    """
    with patch.dict(os.environ, {"CUSTOM_API_URL": "http://test-local:8000"}):
        yield


@pytest.mark.asyncio
async def test_initialization(mock_local_env):
    client = LocalModelClient()
    assert client.base_url == "http://test-local:8000"
    assert client.api_key == ""


@pytest.mark.asyncio
async def test_initialization_default():
    with patch.dict(os.environ, {}, clear=True):
        client = LocalModelClient()
        assert client.base_url == "http://localhost:11434/v1"


@pytest.mark.asyncio
async def test_chat_completion_openai_format(mock_local_env):
    client = LocalModelClient()
    mock_response = {
        "choices": [{"message": {"content": "Local Hello"}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 5},
    }
    client._make_request = AsyncMock(return_value=(mock_response, 50))

    response = await client.chat_completion(
        model="llama2", messages=[{"role": "user", "content": "Hi"}]
    )

    assert response.content == "Local Hello"
    assert response.provider == "local"
    assert response.latency_ms == 50


@pytest.mark.asyncio
async def test_function_calling_passthrough(mock_local_env):
    client = LocalModelClient()
    mock_response = {
        "choices": [
            {"message": {"tool_calls": [{"function": {"name": "func", "arguments": "{}"}}]}}
        ]
    }
    client._make_request = AsyncMock(return_value=(mock_response, 60))

    response = await client.chat_completion(
        model="llama2",
        messages=[{"role": "user", "content": "Call func"}],
        functions=[{"name": "func", "parameters": {}}],
    )

    assert response.function_call is not None
    assert response.function_call.name == "func"


@pytest.mark.asyncio
async def test_ollama_fallback(mock_local_env):
    client = LocalModelClient()

    # Mock _make_request to raise exception simulating failure
    client._make_request = AsyncMock(side_effect=Exception("API Error"))

    # Mock session for fallback call
    client.session = MagicMock()
    mock_session_post = MagicMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {"response": "Ollama fallback"}
    mock_session_post.__aenter__.return_value = mock_response
    client.session.post.return_value = mock_session_post

    response = await client.chat_completion(
        model="llama2", messages=[{"role": "user", "content": "Hi"}]
    )

    assert response.content == "Ollama fallback"
    assert response.provider == "local"

    # Verify fallback endpoint called
    args = client.session.post.call_args
    assert "api/generate" in args[0][0]


@pytest.mark.asyncio
async def test_ollama_fallback_fails_with_functions(mock_local_env):
    client = LocalModelClient()
    client._make_request = AsyncMock(side_effect=Exception("API Error"))

    with pytest.raises(Exception, match="API Error"):
        await client.chat_completion(
            model="llama2",
            messages=[{"role": "user", "content": "Hi"}],
            functions=[{"name": "func", "parameters": {}}],
        )
