import os
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import Response

from lattice_lock.orchestrator.registry import ModelRegistry
from lattice_lock.orchestrator.types import ModelCapabilities, ModelProvider


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Set dummy API keys for all providers so framework validation passes."""
    original_environ = os.environ.copy()
    os.environ.update(
        {
            "OPENAI_API_KEY": "sk-dummy-key",
            "ANTHROPIC_API_KEY": "sk-ant-dummy-key",
            "GOOGLE_API_KEY": "dummy-google-key",
            "AWS_ACCESS_KEY_ID": "dummy-aws-id",
            "AWS_SECRET_ACCESS_KEY": "dummy-aws-secret",
            "XAI_API_KEY": "dummy-xai-key",
            "AZURE_OPENAI_API_KEY": "dummy-azure-key",
            "AZURE_OPENAI_ENDPOINT": "https://dummy.openai.azure.com",
        }
    )
    yield
    os.environ.clear()
    os.environ.update(original_environ)


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient to control HTTP responses."""
    mock_client = MagicMock()

    # Setup async context manager for the client itself
    async def __aenter__():
        return mock_client

    async def __aexit__(*args, **kwargs):
        pass

    mock_client.__aenter__ = __aenter__
    mock_client.__aexit__ = __aexit__

    # aclose method IS a coroutine
    mock_client.aclose = AsyncMock()
    mock_client.is_closed = False

    # request method is async in our usage (await client.request())
    # So it should be an AsyncMock that returns the response
    mock_client.request = AsyncMock()

    # We patch httpx.AsyncClient globally for the duration of the test
    with unittest.mock.patch("httpx.AsyncClient", return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_response_factory():
    """Fixture that returns a helper to create mock responses."""

    def _create_mock_response(status=200, json_data=None, text_data=""):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = status

        def json_method():
            if json_data is not None:
                return json_data
            return {}

        mock_response.json = json_method
        mock_response.text = text_data

        # httpx response is NOT a context manager in request() usage, only in stream()
        # But we mocked request() to return response directly.

        return mock_response

    return _create_mock_response


@pytest.fixture(autouse=True)
def mock_model_registry():
    """Patch ModelRegistry to return dummy capabilities for any model."""

    def get_provider_from_id(model_id: str) -> ModelProvider:
        if "gpt" in model_id or "o1-" in model_id:
            return ModelProvider.OPENAI
        if "claude" in model_id:
            if "bedrock" in model_id or "anthropic.claude" in model_id:
                return ModelProvider.BEDROCK
            return ModelProvider.ANTHROPIC
        if "gemini" in model_id:
            return ModelProvider.GOOGLE
        if "llama" in model_id or "mixtral" in model_id or "command" in model_id:
            if "bedrock" in model_id or "meta." in model_id:
                return ModelProvider.BEDROCK
            return ModelProvider.OLLAMA  # Local map to ollama usually
        if "mistral" in model_id:
            return ModelProvider.BEDROCK
        return ModelProvider.OPENAI

    original_get = ModelRegistry.get_model

    def side_effect(self, model_id: str):
        # Try original first
        try:
            res = original_get(self, model_id)
            if res:
                return res
        except Exception:
            pass

        provider = get_provider_from_id(model_id)
        # Construct valid ModelCapabilities
        return ModelCapabilities(
            name=model_id,
            api_name=model_id,
            provider=provider,
            context_window=100000,
            input_cost=0.01,
            output_cost=0.03,
            reasoning_score=80.0,
            coding_score=80.0,
            speed_rating=8.0,
            supports_function_calling=True,
            supports_json_mode=True,
        )

    with unittest.mock.patch(
        "lattice_lock.orchestrator.registry.ModelRegistry.get_model",
        side_effect=side_effect,
        autospec=True,
    ):
        yield


@pytest.fixture(autouse=True)
def mock_boto3_module():
    """Mock boto3 module if not installed to allow tests to pass."""
    import sys

    if "boto3" not in sys.modules:
        mock_boto3 = MagicMock()
        mock_boto3.client = MagicMock()
        mock_boto3.Session = MagicMock()
        sys.modules["boto3"] = mock_boto3

        # Also ensure botocore.exceptions is available as it is imported by bedrock provider
        if "botocore" not in sys.modules:
            mock_botocore = MagicMock()
            mock_exceptions = MagicMock()
            mock_exceptions.ClientError = Exception
            mock_botocore.exceptions = mock_exceptions
            sys.modules["botocore"] = mock_botocore
            sys.modules["botocore.exceptions"] = mock_exceptions

        # Force reload of bedrock provider if it was already imported
        # This ensures it picks up the mocked boto3 and sets _BOTO3_AVAILABLE = True
        if "lattice_lock.orchestrator.providers.bedrock" in sys.modules:
            import importlib

            importlib.reload(sys.modules["lattice_lock.orchestrator.providers.bedrock"])

        yield

        # Cleanup
        del sys.modules["boto3"]
        if "botocore" in sys.modules and isinstance(sys.modules["botocore"], MagicMock):
            del sys.modules["botocore"]
            del sys.modules["botocore.exceptions"]
    else:
        yield
