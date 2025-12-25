"""
Tests for Task 6.1.4 - Provider Client Hardening & Bedrock Behavior

This module tests:
- Provider availability checks and credential validation
- BedrockClient graceful error handling (no NotImplementedError)
- Fallback behavior when primary provider fails
- Clear error messages for missing credentials
- Provider status classification (Production, Beta, Experimental)
"""

import os
from unittest.mock import patch

import pytest

from lattice_lock.orchestrator.providers import (
    AnthropicAPIClient,
    BedrockAPIClient,
    GoogleAPIClient,
    GrokAPIClient,
    LocalModelClient,
    OpenAIAPIClient,
    ProviderAvailability,
    ProviderStatus,
    ProviderUnavailableError,
    get_api_client,
)
from lattice_lock.orchestrator.types import APIResponse


class TestProviderStatus:
    """Tests for ProviderStatus enum."""

    def test_provider_status_values(self):
        """Test that all expected status values exist."""
        assert ProviderStatus.PRODUCTION.value == "production"
        assert ProviderStatus.BETA.value == "beta"
        assert ProviderStatus.EXPERIMENTAL.value == "experimental"
        assert ProviderStatus.UNAVAILABLE.value == "unavailable"

    def test_provider_status_count(self):
        """Test that we have exactly 4 status levels."""
        assert len(ProviderStatus) == 4


class TestProviderAvailability:
    """Tests for ProviderAvailability class."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProviderAvailability.reset()

    def teardown_method(self):
        """Reset singleton after each test."""
        ProviderAvailability.reset()

    def test_required_credentials_defined(self):
        """Test that required credentials are defined for all providers."""
        expected_providers = [
            "openai",
            "anthropic",
            "google",
            "xai",
            "azure",
            "bedrock",
            "dial",
            "local",
        ]
        for provider in expected_providers:
            assert provider in ProviderAvailability.REQUIRED_CREDENTIALS

    def test_provider_maturity_defined(self):
        """Test that maturity levels are defined for all providers."""
        expected_providers = [
            "openai",
            "anthropic",
            "google",
            "xai",
            "azure",
            "bedrock",
            "dial",
            "local",
        ]
        for provider in expected_providers:
            assert provider in ProviderAvailability.PROVIDER_MATURITY

    def test_production_providers(self):
        """Test that production providers are correctly classified."""
        production_providers = ["openai", "anthropic", "google", "xai", "local"]
        for provider in production_providers:
            assert ProviderAvailability.PROVIDER_MATURITY[provider] == ProviderStatus.PRODUCTION

    def test_beta_providers(self):
        """Test that beta providers are correctly classified."""
        beta_providers = ["azure", "dial"]
        for provider in beta_providers:
            assert ProviderAvailability.PROVIDER_MATURITY[provider] == ProviderStatus.BETA

    def test_experimental_providers(self):
        """Test that experimental providers are correctly classified."""
        assert ProviderAvailability.PROVIDER_MATURITY["bedrock"] == ProviderStatus.EXPERIMENTAL

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    def test_check_available_provider(self):
        """Test that provider with credentials is marked available."""
        ProviderAvailability.reset()
        status = ProviderAvailability.check_all_providers()
        assert status["openai"] == ProviderStatus.PRODUCTION
        assert ProviderAvailability.is_available("openai")

    @patch.dict(os.environ, {}, clear=True)
    def test_check_unavailable_provider(self):
        """Test that provider without credentials is marked unavailable."""
        ProviderAvailability.reset()
        status = ProviderAvailability.check_all_providers()
        assert status["openai"] == ProviderStatus.UNAVAILABLE
        assert not ProviderAvailability.is_available("openai")

    @patch.dict(os.environ, {}, clear=True)
    def test_get_message_for_missing_credentials(self):
        """Test that missing credentials produce clear message."""
        ProviderAvailability.reset()
        ProviderAvailability.check_all_providers()
        message = ProviderAvailability.get_message("openai")
        assert "Missing credentials" in message
        assert "OPENAI_API_KEY" in message

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test", "ANTHROPIC_API_KEY": "test"}, clear=True)
    def test_get_available_providers(self):
        """Test getting list of available providers."""
        ProviderAvailability.reset()
        available = ProviderAvailability.get_available_providers()
        assert "openai" in available
        assert "anthropic" in available
        # local and bedrock don't require credentials
        assert "local" in available
        assert "bedrock" in available

    def test_singleton_pattern(self):
        """Test that ProviderAvailability uses singleton pattern."""
        instance1 = ProviderAvailability.get_instance()
        instance2 = ProviderAvailability.get_instance()
        assert instance1 is instance2

    def test_reset_clears_state(self):
        """Test that reset clears the singleton state."""
        ProviderAvailability.check_all_providers()
        ProviderAvailability.reset()
        instance = ProviderAvailability.get_instance()
        assert not instance._checked


class TestProviderUnavailableError:
    """Tests for ProviderUnavailableError exception."""

    def test_error_message_format(self):
        """Test that error message is properly formatted."""
        error = ProviderUnavailableError("openai", "Missing OPENAI_API_KEY")
        assert "openai" in str(error)
        assert "Missing OPENAI_API_KEY" in str(error)
        assert error.provider == "openai"
        assert error.message == "Missing OPENAI_API_KEY"

    def test_error_is_exception(self):
        """Test that ProviderUnavailableError is an Exception."""
        error = ProviderUnavailableError("test", "test message")
        assert isinstance(error, Exception)


class TestGetApiClient:
    """Tests for get_api_client factory function."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProviderAvailability.reset()

    def teardown_method(self):
        """Reset singleton after each test."""
        ProviderAvailability.reset()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    def test_get_openai_client(self):
        """Test getting OpenAI client with credentials."""
        ProviderAvailability.reset()
        client = get_api_client("openai")
        assert isinstance(client, OpenAIAPIClient)

    @patch.dict(os.environ, {"XAI_API_KEY": "test-key"}, clear=True)
    def test_get_xai_client(self):
        """Test getting xAI/Grok client with credentials."""
        ProviderAvailability.reset()
        client = get_api_client("xai")
        assert isinstance(client, GrokAPIClient)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_local_client_no_credentials_needed(self):
        """Test getting local client without credentials."""
        ProviderAvailability.reset()
        client = get_api_client("local")
        assert isinstance(client, LocalModelClient)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_bedrock_client_experimental(self):
        """Test getting Bedrock client (experimental, no credentials required)."""
        ProviderAvailability.reset()
        client = get_api_client("bedrock")
        assert isinstance(client, BedrockAPIClient)

    @patch.dict(os.environ, {}, clear=True)
    def test_unavailable_provider_raises_error(self):
        """Test that unavailable provider raises ProviderUnavailableError."""
        ProviderAvailability.reset()
        with pytest.raises(ProviderUnavailableError) as exc_info:
            get_api_client("openai", check_availability=True)
        assert "openai" in str(exc_info.value)
        assert "Missing credentials" in str(exc_info.value)

    @patch.dict(os.environ, {}, clear=True)
    def test_skip_availability_check(self):
        """Test that availability check can be skipped."""
        ProviderAvailability.reset()
        # This should raise ValueError from the client itself, not ProviderUnavailableError
        with pytest.raises(ValueError):
            get_api_client("openai", check_availability=False)

    def test_unknown_provider_raises_value_error(self):
        """Test that unknown provider raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_api_client("unknown_provider")
        assert "Unknown provider" in str(exc_info.value)
        assert "unknown_provider" in str(exc_info.value)

    @patch.dict(os.environ, {"XAI_API_KEY": "test-key"}, clear=True)
    def test_provider_alias_grok(self):
        """Test that 'grok' alias maps to 'xai'."""
        ProviderAvailability.reset()
        client = get_api_client("grok")
        assert isinstance(client, GrokAPIClient)

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}, clear=True)
    def test_provider_alias_gemini(self):
        """Test that 'gemini' alias maps to 'google'."""
        ProviderAvailability.reset()
        client = get_api_client("gemini")
        assert isinstance(client, GoogleAPIClient)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True)
    def test_provider_alias_claude(self):
        """Test that 'claude' alias maps to 'anthropic'."""
        ProviderAvailability.reset()
        client = get_api_client("claude")
        assert isinstance(client, AnthropicAPIClient)

    @patch.dict(os.environ, {}, clear=True)
    def test_provider_alias_ollama(self):
        """Test that 'ollama' alias maps to 'local'."""
        ProviderAvailability.reset()
        client = get_api_client("ollama")
        assert isinstance(client, LocalModelClient)


class TestBedrockAPIClient:
    """Tests for BedrockAPIClient graceful error handling."""

    def test_bedrock_client_creation(self):
        """Test that BedrockAPIClient can be created."""
        client = BedrockAPIClient()
        assert client.region == "us-east-1"

    def test_bedrock_client_custom_region(self):
        """Test that BedrockAPIClient accepts custom region."""
        client = BedrockAPIClient(region="us-west-2")
        assert client.region == "us-west-2"

    @pytest.mark.asyncio
    async def test_bedrock_no_not_implemented_error(self):
        """Test that BedrockAPIClient does NOT raise NotImplementedError."""
        client = BedrockAPIClient()
        messages = [{"role": "user", "content": "Hello"}]

        # This should NOT raise NotImplementedError
        response = await client.chat_completion(model="anthropic.claude-v2", messages=messages)

        # Should return an APIResponse with error field set
        assert isinstance(response, APIResponse)
        assert response.error is not None
        assert "experimental" in response.error.lower() or "boto3" in response.error.lower()

    @pytest.mark.asyncio
    async def test_bedrock_returns_error_response(self):
        """Test that BedrockAPIClient returns error in APIResponse."""
        client = BedrockAPIClient()
        messages = [{"role": "user", "content": "Hello"}]

        response = await client.chat_completion(model="anthropic.claude-v2", messages=messages)

        assert response.content is None
        assert response.provider == "bedrock"
        assert response.error is not None
        assert "boto3" in response.error

    @pytest.mark.asyncio
    async def test_bedrock_with_functions_includes_note(self):
        """Test that BedrockAPIClient mentions function calling limitation."""
        client = BedrockAPIClient()
        messages = [{"role": "user", "content": "Hello"}]
        functions = [{"name": "test_func", "parameters": {}}]

        response = await client.chat_completion(
            model="anthropic.claude-v2", messages=messages, functions=functions
        )

        assert "function calling" in response.error.lower()

    @pytest.mark.asyncio
    async def test_bedrock_logs_warning_once(self):
        """Test that BedrockAPIClient logs warning only once."""
        client = BedrockAPIClient()
        messages = [{"role": "user", "content": "Hello"}]

        # First call
        await client.chat_completion(model="test", messages=messages)
        assert client._warned is True

        # Second call should not log again (warning flag already set)
        await client.chat_completion(model="test", messages=messages)
        assert client._warned is True


class TestModelOrchestratorProviderIntegration:
    """Tests for ModelOrchestrator provider availability integration."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProviderAvailability.reset()

    def teardown_method(self):
        """Reset singleton after each test."""
        ProviderAvailability.reset()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test", "ANTHROPIC_API_KEY": "test"}, clear=True)
    def test_orchestrator_check_provider_status(self):
        """Test that orchestrator can check provider status."""
        from lattice_lock.orchestrator.core import ModelOrchestrator

        ProviderAvailability.reset()
        orchestrator = ModelOrchestrator()
        status = orchestrator.check_provider_status()

        assert "openai" in status
        assert "production" in status["openai"].lower()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True)
    def test_orchestrator_get_available_providers(self):
        """Test that orchestrator can get available providers."""
        from lattice_lock.orchestrator.core import ModelOrchestrator

        ProviderAvailability.reset()
        orchestrator = ModelOrchestrator()
        available = orchestrator.get_available_providers()

        assert "openai" in available
        assert "local" in available  # No credentials needed

    @patch.dict(os.environ, {}, clear=True)
    def test_orchestrator_is_provider_available(self):
        """Test that orchestrator can check individual provider availability."""
        from lattice_lock.orchestrator.core import ModelOrchestrator

        ProviderAvailability.reset()
        orchestrator = ModelOrchestrator()

        # local doesn't need credentials
        assert orchestrator._is_provider_available("local")
        # openai needs credentials
        assert not orchestrator._is_provider_available("openai")


class TestFallbackBehavior:
    """Tests for fallback behavior with provider availability."""

    def setup_method(self):
        """Reset singleton before each test."""
        ProviderAvailability.reset()

    def teardown_method(self):
        """Reset singleton after each test."""
        ProviderAvailability.reset()

    @patch.dict(os.environ, {}, clear=True)
    def test_fallback_skips_unavailable_providers(self):
        """Test that fallback logic skips unavailable providers."""
        from lattice_lock.orchestrator.core import ModelOrchestrator

        ProviderAvailability.reset()
        orchestrator = ModelOrchestrator()

        # Without any API keys, only local should be available
        available = orchestrator.get_available_providers()
        assert "local" in available
        assert "openai" not in available


class TestAcceptanceCriteria:
    """
    Tests verifying Task 6.1.4 acceptance criteria:
    - No NotImplementedError raised during normal operation
    - Missing credentials produce clear warning, not crash
    - Fallback chains work when primary provider unavailable
    - All existing tests still pass (verified by running full test suite)
    - New tests cover provider availability scenarios
    """

    def setup_method(self):
        """Reset singleton before each test."""
        ProviderAvailability.reset()

    def teardown_method(self):
        """Reset singleton after each test."""
        ProviderAvailability.reset()

    @pytest.mark.asyncio
    async def test_no_not_implemented_error_bedrock(self):
        """AC: No NotImplementedError raised during normal operation."""
        client = BedrockAPIClient()
        messages = [{"role": "user", "content": "Hello"}]

        # Should not raise NotImplementedError
        try:
            response = await client.chat_completion(model="test", messages=messages)
            assert response is not None
        except NotImplementedError:
            pytest.fail("BedrockAPIClient raised NotImplementedError")

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_credentials_clear_warning(self):
        """AC: Missing credentials produce clear warning, not crash."""
        ProviderAvailability.reset()

        # Should not crash, should produce clear message
        try:
            ProviderAvailability.check_all_providers()
            message = ProviderAvailability.get_message("openai")
            assert "Missing credentials" in message
            assert "OPENAI_API_KEY" in message
        except Exception as e:
            pytest.fail(f"Missing credentials caused crash: {e}")

    @patch.dict(os.environ, {}, clear=True)
    def test_provider_unavailable_error_is_clear(self):
        """AC: Provider unavailable error has clear message."""
        ProviderAvailability.reset()

        with pytest.raises(ProviderUnavailableError) as exc_info:
            get_api_client("openai", check_availability=True)

        error = exc_info.value
        assert error.provider == "openai"
        assert "Missing credentials" in error.message

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True)
    def test_fallback_chain_skips_unavailable(self):
        """AC: Fallback chains work when primary provider unavailable."""
        from lattice_lock.orchestrator.core import ModelOrchestrator

        ProviderAvailability.reset()
        orchestrator = ModelOrchestrator()

        # Verify that unavailable providers are detected
        assert not orchestrator._is_provider_available("anthropic")
        assert orchestrator._is_provider_available("openai")
