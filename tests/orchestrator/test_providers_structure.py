import os
from unittest.mock import patch
import pytest

from lattice_lock.orchestrator.providers import (
    BaseAPIClient,
    OpenAIAPIClient,
    get_api_client,
)

def test_factory_returns_new_classes():
    """Verify factory returns instances of new classes."""
    # Mock environment to avoid missing credentials error
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = get_api_client("openai")
        assert isinstance(client, OpenAIAPIClient)
        assert isinstance(client, BaseAPIClient)
