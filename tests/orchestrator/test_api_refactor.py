from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lattice_lock.orchestrator.exceptions import (
    AuthenticationError,
    RateLimitError,
    ServerError,
)
from lattice_lock.orchestrator.providers import (
    BaseAPIClient,
    GrokAPIClient,
    ProviderAvailability,
    ProviderStatus,
)


@pytest.mark.asyncio
async def test_base_api_client_exceptions():
    """Test that BaseAPIClient raises correct exceptions"""
    client = BaseAPIClient("fake-key", "http://fake-url")

    # Mock aiohttp session
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.text.return_value = '{"error": {"message": "Unauthorized"}}'
    mock_response.json.return_value = {"error": {"message": "Unauthorized"}}

    mock_session = MagicMock()
    # request() is not a coroutine, it returns an async context manager
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_response
    mock_session.request.return_value = mock_ctx

    client.session = mock_session

    with pytest.raises(AuthenticationError) as exc:
        await client._make_request("GET", "test", {}, {})
    assert "Unauthorized" in str(exc.value)

    # Test 429
    mock_response.status = 429
    mock_response.text.return_value = "Rate limit exceeded"
    with pytest.raises(RateLimitError):
        await client._make_request("GET", "test", {}, {})

    # Test 500
    mock_response.status = 500
    mock_response.text.return_value = "Server error"
    with pytest.raises(ServerError):
        await client._make_request("GET", "test", {}, {})


@pytest.mark.asyncio
async def test_grok_client_structure():
    """Verify GrokAPIClient uses the new template method"""
    with patch.dict("os.environ", {"XAI_API_KEY": "fake-key"}):
        client = GrokAPIClient()
        assert isinstance(client, BaseAPIClient)
        # Check that it has the implementing method
        assert hasattr(client, "_chat_completion_impl")


@pytest.mark.asyncio
async def test_availability_check():
    """Test ProviderAvailability singleton"""
    # Reset for test
    ProviderAvailability.reset()

    with patch.dict("os.environ", {"XAI_API_KEY": "test-key"}):
        status = ProviderAvailability.get_status("xai")
        assert status == ProviderStatus.PRODUCTION
        assert ProviderAvailability.is_available("xai")

    # Test unavailable
    with patch.dict("os.environ", {}, clear=True):
        ProviderAvailability.reset()
        status = ProviderAvailability.get_status("xai")
        # If env var is missing, usage depends on if it was already cached or not
        # but reset() should clear it.
        # Note: Depending on how the class is implemented, we expect UNAVAILABLE or EXPERIMENTAL
        # Based on code: "missing credentials" -> UNAVAILABLE
        assert status == ProviderStatus.UNAVAILABLE
