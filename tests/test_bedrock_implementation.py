import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Skip bedrock tests if boto3 is not installed
boto3 = pytest.importorskip("boto3", reason="boto3 not installed")

from lattice_lock.orchestrator.providers.bedrock import BedrockClient
from lattice_lock.orchestrator.providers.fallback import FallbackManager, ProviderUnavailableError
from lattice_lock.orchestrator.registry import ModelRegistry
from lattice_lock.orchestrator.types import ModelProvider


@pytest.fixture
def mock_boto():
    with patch("boto3.client") as mock:
        yield mock


@pytest.fixture
def client(mock_boto):
    with patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "test", "AWS_SECRET_ACCESS_KEY": "test"}):
        yield BedrockClient()


class TestBedrockClient:
    def test_init_sets_region(self):
        with patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "test", "AWS_SECRET_ACCESS_KEY": "test"}):
            client = BedrockClient(region_name="us-west-2")
            assert client.region_name == "us-west-2"

    @pytest.mark.asyncio
    async def test_generate_calls_bedrock(self, client, mock_boto):
        mock_bedrock = MagicMock()
        mock_boto.return_value = mock_bedrock
        mock_response = {
            "body": MagicMock(
                read=lambda: b'{"content":[{"type":"text", "text":"Hello"}], "usage":{"input_tokens":10, "output_tokens":5}}'
            )
        }
        mock_bedrock.invoke_model.return_value = mock_response

        response = await client.generate(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            messages=[{"role": "user", "content": "Hi"}],
        )

        assert response is not None
        assert not response.error
        mock_bedrock.invoke_model.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_handles_error(self, client, mock_boto):
        mock_bedrock = MagicMock()
        mock_boto.return_value = mock_bedrock
        mock_bedrock.invoke_model.side_effect = Exception("Bedrock error")

        response = await client.generate(model="test", messages=[])
        assert response.error
        assert "Bedrock error" in response.error


class TestFallbackManager:
    @pytest.mark.asyncio
    async def test_execute_primary_succeeds(self):
        manager = FallbackManager()
        
        # Use simple tracking list
        calls = []
        async def mock_coro(model):
             calls.append(model)
             return "Success"
        
        result = await manager.execute_with_fallback(mock_coro, ["primary", "backup"])
        assert result == "Success"
        assert calls == ["primary"]

    @pytest.mark.asyncio
    async def test_execute_fallback_succeeds(self):
        manager = FallbackManager()
        
        calls = []
        async def fail_then_succeed(model):
            calls.append(model)
            if model == "primary":
                raise Exception("Fail")
            return "Success"
            
        result = await manager.execute_with_fallback(fail_then_succeed, ["primary", "backup"])
        assert result == "Success"
        # Primary fails twice (initial + 1 retry default), then backup succeeds
        assert len(calls) == 3
        assert calls == ["primary", "primary", "backup"]

    @pytest.mark.asyncio
    async def test_all_fail_raises_exception(self):
        # Set max_retries higher than number of models to ensure we exhaust models first
        manager = FallbackManager(max_retries=1) 
        
        async def fail(model):
             raise Exception("Fail")
             
        with pytest.raises(ProviderUnavailableError):
            await manager.execute_with_fallback(fail, ["primary", "backup"])


class TestRegistryHardening:
    def test_validate_credentials(self):
        registry = ModelRegistry()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True):
            assert registry.validate_credentials(ModelProvider.OPENAI)

        with patch.dict(os.environ, {}, clear=True):
            assert not registry.validate_credentials(ModelProvider.OPENAI)
