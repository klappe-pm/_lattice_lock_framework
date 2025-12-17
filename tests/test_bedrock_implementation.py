import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Skip bedrock tests if boto3 is not installed
boto3 = pytest.importorskip("boto3", reason="boto3 not installed")

from lattice_lock_orchestrator.providers.bedrock import BedrockClient
from lattice_lock_orchestrator.providers.fallback import FallbackManager, ProviderUnavailableError
from lattice_lock_orchestrator.registry import ModelRegistry
from lattice_lock_orchestrator.types import ModelProvider


class TestBedrockClient(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("boto3.client")
        self.mock_boto = self.patcher.start()
        # Ensure client is enabled for testing
        with patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "test", "AWS_SECRET_ACCESS_KEY": "test"}):
            self.client = BedrockClient()

    def tearDown(self):
        self.patcher.stop()

    def test_init_sets_region(self):
        client = BedrockClient(region_name="us-west-2")
        self.assertEqual(client.region_name, "us-west-2")

    def test_generate_calls_bedrock(self):
        client = self.client
        mock_bedrock = MagicMock()
        self.mock_boto.return_value = mock_bedrock
        mock_response = {
            "body": MagicMock(
                read=lambda: b'{"content":[{"type":"text", "text":"Hello"}], "usage":{"input_tokens":10, "output_tokens":5}}'
            )
        }
        mock_bedrock.invoke_model.return_value = mock_response

        response = client.generate(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            messages=[{"role": "user", "content": "Hi"}],
        )

        self.assertIsNotNone(response)
        self.assertFalse(response.error)
        mock_bedrock.invoke_model.assert_called_once()

    def test_generate_handles_error(self):
        client = self.client
        mock_bedrock = MagicMock()
        self.mock_boto.return_value = mock_bedrock
        mock_bedrock.invoke_model.side_effect = Exception("Bedrock error")

        response = client.generate(model="test", messages=[])
        self.assertTrue(response.error)
        self.assertIn("Bedrock error", response.error)


class TestFallbackManager(unittest.TestCase):
    def test_execute_primary_succeeds(self):
        manager = FallbackManager()
        mock_func = MagicMock(return_value="Success")
        result = manager.execute_with_fallback(mock_func, ["primary", "backup"])
        self.assertEqual(result, "Success")
        mock_func.assert_called_once_with("primary")

    def test_execute_fallback_succeeds(self):
        manager = FallbackManager()
        mock_func = MagicMock(side_effect=[Exception("Fail"), "Success"])
        result = manager.execute_with_fallback(mock_func, ["primary", "backup"])
        self.assertEqual(result, "Success")
        self.assertEqual(mock_func.call_count, 2)

    def test_all_fail_raises_exception(self):
        manager = FallbackManager(max_retries=0)
        mock_func = MagicMock(side_effect=Exception("Fail"))
        with self.assertRaises(ProviderUnavailableError):
            manager.execute_with_fallback(mock_func, ["primary", "backup"])


class TestRegistryHardening(unittest.TestCase):
    def test_validate_credentials(self):
        registry = ModelRegistry()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True):
            self.assertTrue(registry.validate_credentials(ModelProvider.OPENAI))

        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(registry.validate_credentials(ModelProvider.OPENAI))


if __name__ == "__main__":
    unittest.main()
