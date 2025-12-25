import os
from unittest.mock import patch
import pytest

from lattice_lock.orchestrator.providers import (
    BaseAPIClient,
    GrokAPIClient,
    OpenAIAPIClient,
    XAIAPIClient,
    get_api_client,
)

def test_new_imports_work():
    """Verify that we can import from the new package."""
    assert get_api_client is not None
    assert OpenAIAPIClient is not None
    assert BaseAPIClient is not None

def test_grok_alias():
    """Verify GrokAPIClient alias works."""
    assert GrokAPIClient is XAIAPIClient

def test_factory_returns_new_classes():
    """Verify factory returns instances of new classes."""
    # Mock environment to avoid missing credentials error
    # We also mock availability check if needed, but OpenAI availability usually just checks for key
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = get_api_client("openai", check_availability=False)
        assert isinstance(client, OpenAIAPIClient)
        assert isinstance(client, BaseAPIClient)

