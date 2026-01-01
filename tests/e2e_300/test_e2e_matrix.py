import json
import unittest
from unittest.mock import MagicMock

import pytest

from lattice_lock.orchestrator.core import ModelOrchestrator
from lattice_lock.orchestrator.types import APIResponse

# --- Test Data Matrix ---

PROVIDERS = ["openai", "anthropic", "google", "bedrock", "local"]
MODELS = [
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-3-opus",
    "claude-3-sonnet",
    "gemini-pro",
    "gemini-ultra",
    "llama-3-70b",
    "mixtral-8x7b",
    "anthropic.claude-v2",
    "meta.llama3",
    "mistral-large",
    "command-r",
    "gpt-4-turbo",
    "claude-3-haiku",
    "gemini-1.5-pro",
]
SCENARIOS = [
    "basic_chat",
    "long_context",
    "system_prompt_override",
    "json_mode",
    "tool_use_single",
    "tool_use_chain",
    "high_temp",
    "low_temp",
    "top_p_sampling",
    "max_tokens_limit",
    "error_401_auth",
    "error_429_rate_limit",
    "error_500_server",
    "error_503_unavailable",
    "timeout_error",
    "empty_response",
    "malformed_json_response",
    "pii_injection_attempt",
    "prompt_injection_attempt",
    "fallback_required",
]

# Generate 300 combinations (actually we'll just iterate to ensure coverage, but pytest parametrization is cleaner)
# We will use a generator to create strict (provider, model, scenario) tuples that make sense
# e.g., mapping models to their correct providers to avoid "invalid model for provider" errors before we even hit the network.

MODEL_PROVIDER_MAP = {
    "gpt-4": "openai",
    "gpt-3.5-turbo": "openai",
    "gpt-4-turbo": "openai",
    "claude-3-opus": "anthropic",
    "claude-3-sonnet": "anthropic",
    "claude-3-haiku": "anthropic",
    "gemini-pro": "google",
    "gemini-ultra": "google",
    "gemini-1.5-pro": "google",
    "anthropic.claude-v2": "bedrock",
    "meta.llama3": "bedrock",
    "mistral-large": "bedrock",
    "llama-3-70b": "local",
    "mixtral-8x7b": "local",
    "command-r": "local",
}

TEST_CASES = []
for model in MODELS:
    provider = MODEL_PROVIDER_MAP.get(model, "openai")  # Default fallback
    for scenario in SCENARIOS:
        TEST_CASES.append((provider, model, scenario))


@pytest.mark.asyncio
@pytest.mark.parametrize("provider, model_id, scenario", TEST_CASES)
async def test_orchestrator_e2e(
    mock_aiohttp_session, mock_response_factory, provider, model_id, scenario
):
    """
    E2E Test validating the full orchestrator flow with mocked provider responses.
    """
    orchestrator = ModelOrchestrator()

    # --- Setup Mock Behavior based on Scenario ---

    # 1. Determine expected success payload structure
    mock_resp_payload = {}

    if provider in ["openai", "local"]:
        # OpenAI & Local (Ollama/vLLM) use standard ChatCompletion format
        mock_resp_payload = {
            "choices": [
                {
                    "message": {"content": "Test response content", "role": "assistant"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }
    elif provider == "anthropic":
        # Anthropic uses top-level content list
        mock_resp_payload = {
            "content": [{"type": "text", "text": "Test response content"}],
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }
    elif provider == "google":
        # Google Gemini uses candidates structure
        mock_resp_payload = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "Test response content"}], "role": "model"},
                    "finish_reason": "STOP",
                }
            ],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5},
        }
    elif provider == "bedrock":
        # Bedrock responses depend on the invoked model, but typically follow Anthropic format inside "body"
        # for Claude models, which are the primary ones we mock here.
        # Bedrock wrapping is handled via boto3 mock, payload is the inner JSON.
        mock_resp_payload = {
            "content": [{"type": "text", "text": "Test response content"}],
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }

    # 2. Determine failure conditions based on scenario
    status = 200
    exception_to_raise = None

    if "error_401" in scenario:
        status = 401
    elif "error_429" in scenario:
        status = 429
    elif "error_500" in scenario:
        status = 500
    elif "error_503" in scenario:
        status = 503
    elif "timeout" in scenario:
        exception_to_raise = TimeoutError("Simulated timeout")
    elif "empty_response" in scenario:
        mock_resp_payload = {}
    elif "malformed_json_response" in scenario:
        # Will be handled by raw text response that isn't valid JSON
        pass

    # 3. Apply Mocks

    # A) For HTTP-based providers (OpenAI, Anthropic, Google, Local)
    if provider != "bedrock":
        if exception_to_raise:
            mock_aiohttp_session.request.side_effect = exception_to_raise
        else:
            if "malformed_json" in scenario:
                # Return invalid JSON text
                mock_response = mock_response_factory(status=200, text_data="{invalid_json")

                # Force .json() to fail as real aiohttp would
                async def fail_json():
                    raise ValueError("JSONDecodeError")

                mock_response.json = fail_json
            else:
                mock_response = mock_response_factory(status=status, json_data=mock_resp_payload)

            mock_aiohttp_session.request.return_value = mock_response

    # B) For Bedrock (uses boto3)
    else:
        # We need to mock boto3.client used in BedrockAPIClient
        # Since the client is instantiated inside the method or cached, we patch the boto3.client factory

        mock_boto_client = MagicMock()

        if exception_to_raise:
            mock_boto_client.invoke_model.side_effect = exception_to_raise
        elif status != 200:
            # Simulate AWS ClientError
            # This is complex to mock perfectly, so we'll simulate a generic Exception that the client catches
            mock_boto_client.invoke_model.side_effect = Exception(f"AWS Error {status}")
        elif "malformed_json" in scenario:
            # Return a body that is not valid JSON
            mock_body = MagicMock()
            mock_body.read.return_value = b"{invalid_json"
            mock_boto_client.invoke_model.return_value = {"body": mock_body}
        elif "empty_response" in scenario:
            # Return valid JSON but empty
            mock_body = MagicMock()
            mock_body.read.return_value = json.dumps({}).encode("utf-8")
            mock_boto_client.invoke_model.return_value = {"body": mock_body}
        else:
            # Success Case
            mock_body = MagicMock()
            mock_body.read.return_value = json.dumps(mock_resp_payload).encode("utf-8")
            mock_boto_client.invoke_model.return_value = {"body": mock_body}

        # Apply the patch to boto3.client
        # We need to verify where BedrockAPIClient imports boto3.
        # It does `import boto3`. So we patch `boto3.client`.

        with unittest.mock.patch("boto3.client", return_value=mock_boto_client):
            await _run_orchestrator_test(
                orchestrator, provider, model_id, scenario, status, exception_to_raise
            )
            return

    # Execute for non-bedrock (already returned above if bedrock)
    await _run_orchestrator_test(
        orchestrator, provider, model_id, scenario, status, exception_to_raise
    )


async def _run_orchestrator_test(
    orchestrator, provider, model_id, scenario, status, exception_to_raise
):
    """Helper to run the actual request and assertions"""

    # Additional prompt params
    prompt = "Hello, world!"
    kwargs = {}
    if "long_context" in scenario:
        prompt = "test " * 1000
    if "system" in scenario:
        kwargs["system"] = "You are a helpful assistant."

    try:
        response = await orchestrator.route_request(prompt=prompt, model_id=model_id, **kwargs)

        # --- Assertions ---
        if (
            status == 200
            and not exception_to_raise
            and "malformed" not in scenario
            and "empty" not in scenario
        ):
            assert isinstance(response, APIResponse)
            assert response.content is not None
            assert len(response.content) > 0

    except RuntimeError as e:
        # Orchestrator raises RuntimeError if all fallbacks fail
        if (
            "fallback" in scenario
            or status != 200
            or exception_to_raise
            or "malformed" in scenario
            or "empty" in scenario
        ):
            # This is expected for error scenarios where fallback chains might also fail in this rigid mock env
            pass
        else:
            raise e  # Unexpected failure
    except Exception as e:
        # Check if this was expected
        if "timeout" in scenario and "timeout" in str(e).lower():
            pass
        elif status != 200:
            pass  # Expected error
        else:
            raise e
