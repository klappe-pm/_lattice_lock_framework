import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock
from lattice_lock_orchestrator.api_clients import BaseAPIClient, APIResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockProviderClient(BaseAPIClient):
    """Mock implementation of a provider client for testing."""
    
    def __init__(self):
        super().__init__(api_key="mock_key", base_url="http://mock.url")
        self.impl_called = False
    
    async def _chat_completion_impl(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        functions: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs,
    ) -> APIResponse:
        """Mock implementation."""
        self.impl_called = True
        logger.info(f"Mock _chat_completion_impl called with model={model}")
        return APIResponse(
            content="Mock response",
            model=model,
            provider="mock",
            usage={"input_tokens": 10, "output_tokens": 20},
            latency_ms=100
        )

async def test_refactor():
    """Test that chat_completion correctly delegates to _chat_completion_impl."""
    logger.info("Starting API Client Refactor Verification...")
    
    client = MockProviderClient()
    
    # Test call
    response = await client.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.5
    )
    
    # Verify delegation
    if client.impl_called:
        logger.info("SUCCESS: BaseAPIClient.chat_completion delegated to _chat_completion_impl")
    else:
        logger.error("FAILURE: _chat_completion_impl was NOT called")
        exit(1)
        
    # Verify response
    if response.content == "Mock response":
        logger.info("SUCCESS: Response received correctly")
    else:
        logger.error(f"FAILURE: Unexpected response content: {response.content}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(test_refactor())
