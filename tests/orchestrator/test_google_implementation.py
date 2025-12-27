import os
import pytest
from unittest.mock import AsyncMock, patch
from lattice_lock.orchestrator.providers.google import GoogleAPIClient
from lattice_lock.orchestrator.types import APIResponse

@pytest.fixture
def mock_google_env():
    """
    Set the GOOGLE_API_KEY environment variable to "sk-google-test" for the duration of a test.
    
    This pytest fixture patches os.environ so code executed within the test sees the test API key value.
    """
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "sk-google-test"}):
        yield

@pytest.mark.asyncio
async def test_initialization(mock_google_env):
    client = GoogleAPIClient()
    assert client.api_key == "sk-google-test"
    assert "generativelanguage.googleapis.com" in client.base_url

@pytest.mark.asyncio
async def test_chat_completion_success(mock_google_env):
    client = GoogleAPIClient()
    mock_response = {
        "candidates": [{
            "content": {
                "parts": [{"text": "Hello Gemini"}]
            }
        }],
        "usageMetadata": {
            "promptTokenCount": 5,
            "candidatesTokenCount": 2
        }
    }
    client._make_request = AsyncMock(return_value=(mock_response, 90))
    
    response = await client.chat_completion(
        model="gemini-pro",
        messages=[{"role": "user", "content": "Hi"}]
    )
    
    assert response.content == "Hello Gemini"
    assert response.provider == "google"
    assert response.usage["input_tokens"] == 5
    assert response.usage["output_tokens"] == 2
    
    # Verify payload
    call_args = client._make_request.call_args
    endpoint = call_args[0][1]
    payload = call_args[0][3]
    
    assert "key=sk-google-test" in endpoint
    assert payload["contents"][0]["parts"][0]["text"] == "Hi"
    assert payload["contents"][0]["role"] == "user"

@pytest.mark.asyncio
async def test_function_calling(mock_google_env):
    client = GoogleAPIClient()
    mock_response = {
        "candidates": [{
            "content": {
                "parts": [{
                    "functionCall": {
                        "name": "search",
                        "args": {"query": "python"}
                    }
                }]
            }
        }]
    }
    client._make_request = AsyncMock(return_value=(mock_response, 110))
    
    response = await client.chat_completion(
        model="gemini-pro",
        messages=[{"role": "user", "content": "Search python"}],
        functions=[{
            "name": "search",
            "description": "Search web",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}
        }]
    )
    
    assert response.function_call is not None
    assert response.function_call.name == "search"
    assert response.function_call.arguments == {"query": "python"}
    
    # Verify tools payload
    call_args = client._make_request.call_args
    payload = call_args[0][3]
    assert "tools" in payload
    assert payload["tools"][0]["functionDeclarations"][0]["name"] == "search"