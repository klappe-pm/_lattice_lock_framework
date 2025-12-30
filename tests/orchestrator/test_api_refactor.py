from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from lattice_lock.orchestrator.exceptions import AuthenticationError, RateLimitError, ServerError
from lattice_lock.orchestrator.providers import (
    BaseAPIClient,
    GrokAPIClient,
    ProviderAvailability,
    ProviderStatus,
)


@pytest.mark.asyncio
async def test_base_api_client_exceptions():
    """Test that BaseAPIClient raises correct exceptions"""
    from lattice_lock.config import AppConfig

    mock_config = MagicMock(spec=AppConfig)

    # BaseAPIClient is abstract, so we create a concrete dummy
    class DummyClient(BaseAPIClient):
        def _validate_config(self):
            pass

        async def health_check(self):
            return True

        async def chat_completion(self, model, messages, **kwargs):
            pass

    client = DummyClient(mock_config)

    # Mock aiohttp session and response
    mock_response = MagicMock()
    mock_response.status = 401
    mock_response.json = AsyncMock(return_value={"error": {"message": "Unauthorized"}})
    mock_response.text = AsyncMock(return_value='{"error": {"message": "Unauthorized"}}')

    # Create async context manager mock for request()
    class MockRequestContextManager:
        def __init__(self, response):
            self.response = response

        async def __aenter__(self):
            return self.response

        async def __aexit__(self, *args):
            pass

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.request = MagicMock(return_value=MockRequestContextManager(mock_response))

    client._session = mock_session

    # Now raises AuthenticationError for 401/403
    with pytest.raises(AuthenticationError) as exc:
        await client._make_request("GET", "test", {}, {})
    assert "Unauthorized" in str(exc.value)

    # Test 429
    mock_response.status = 429
    mock_response.json = AsyncMock(return_value={"error": {"message": "Rate limit exceeded"}})
    with pytest.raises(RateLimitError):
        await client._make_request("GET", "test", {}, {})

    # Test 500
    mock_response.status = 500
    mock_response.json = AsyncMock(return_value={"error": {"message": "Server error"}})
    with pytest.raises(ServerError):
        await client._make_request("GET", "test", {}, {})


@pytest.mark.asyncio
async def test_grok_client_structure():
    """Verify GrokAPIClient uses the new template method"""
    from lattice_lock.config import AppConfig

    mock_config = MagicMock(spec=AppConfig)

    with patch.dict("os.environ", {"XAI_API_KEY": "fake-key"}):
        client = GrokAPIClient(mock_config)
        assert isinstance(client, BaseAPIClient)
        # Check that it has the required abstract methods implemented
        assert hasattr(client, "health_check")
        assert hasattr(client, "chat_completion")


@pytest.mark.asyncio
async def test_availability_check():
    """Test ProviderAvailability singleton"""
    # Reset for test
    ProviderAvailability.reset()

    with patch.dict("os.environ", {"XAI_API_KEY": "test-key"}):
        # is_available checks if credentials are present
        assert ProviderAvailability.is_available("xai")

    # Test unavailable
    with patch.dict("os.environ", {}, clear=True):
        ProviderAvailability.reset()
        # When credentials are missing, is_available returns False
        assert not ProviderAvailability.is_available("xai")
        # get_status returns UNKNOWN when not explicitly set (not tracking unavailable)
        status = ProviderAvailability.get_status("xai")
        assert status == ProviderStatus.UNKNOWN
