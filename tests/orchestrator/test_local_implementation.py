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
    config = AsyncMock()
    client = LocalModelClient(config=config)
    assert client.base_url == "http://test-local:8000"


@pytest.mark.asyncio
async def test_initialization_default():
    with patch.dict(os.environ, {}, clear=True):
        config = AsyncMock()
        client = LocalModelClient(config=config)
        assert client.base_url == "http://localhost:11434/v1"


@pytest.mark.asyncio
async def test_chat_completion_openai_format(mock_local_env):
    config = AsyncMock()
    client = LocalModelClient(config=config)
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
    config = AsyncMock()
    client = LocalModelClient(config=config)
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
    config = AsyncMock()
    client = LocalModelClient(config=config)

    # Mock _make_request to raise exception first, then return valid response
    client._make_request = AsyncMock(side_effect=[
        Exception("API Error"),
        ({"response": "Ollama fallback"}, 45)
    ])

    # Mock session for fallback call - wait, if _make_request handles it, we don't need to mock session?
    # In my local.py view, _make_request is used for fallback too.
    # But local.py uses client.session.post in the fallback block?
    # Let me check local.py content again.
    # Line 123 calls self._make_request
    # So assuming _make_request is used, I just need to update side_effect.
    # The previous test setup mocked client.session.post which suggests old implementation.
    # My "restored" or current local.py uses _make_request.
    # So I remove the session mock stuff.
    
    # But wait, original test had:
    # client.session = MagicMock()
    # ...
    # client.session.post.return_value = mock_session_post
    # client.config.ollama_base_url = "http://localhost:11434"
    
    # If the implementation uses _make_request, I don't need mocking session.post.
    # I verified local.py uses _make_request at line 123.
    
    client.config.ollama_base_url = "http://localhost:11434"

    response = await client.chat_completion(
        model="llama2", messages=[{"role": "user", "content": "Hi"}]
    )

    assert response.content == "Ollama fallback"
    assert response.provider == "local"

    # Verify fallback endpoint called via _make_request
    # The first call failed (API Error)
    # The second call succeeded ("Ollama fallback")
    # We check the arguments of _make_request
    assert client._make_request.call_count == 2
    
    # Check the second call arguments (the fallback)
    call_args = client._make_request.call_args_list[1]
    url = call_args[0][1]
    assert "api/generate" in url


@pytest.mark.asyncio
async def test_ollama_fallback_fails_with_functions(mock_local_env):
    config = AsyncMock()
    client = LocalModelClient(config=config)
    client._make_request = AsyncMock(side_effect=Exception("API Error"))

    with pytest.raises(Exception, match="API Error"):
        await client.chat_completion(
            model="llama2",
            messages=[{"role": "user", "content": "Hi"}],
            functions=[{"name": "func", "parameters": {}}],
        )
