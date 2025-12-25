"""
AWS Bedrock Provider
"""
import asyncio
import json
import logging
import os
import time

from lattice_lock.orchestrator.types import APIResponse

from .base import BaseAPIClient

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError  # noqa: F401

    _BOTO3_AVAILABLE = True
except ImportError:
    boto3 = None
    ClientError = None  # type: ignore[misc, assignment]
    _BOTO3_AVAILABLE = False


class BedrockClient:
    """
    AWS Bedrock Client Provider.
    """

    def __init__(self, region_name: str | None = None):
        self.region = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.region_name = self.region  # Alias for compatibility
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        # Check Boto3 availability first
        if not _BOTO3_AVAILABLE:
            logger.warning("boto3 not found. Bedrock client disabled.")
            self.enabled = False
            return

        # Then check credentials
        self.enabled = bool(self.access_key and self.secret_key)

        if self.enabled:
            logger.info(f"Bedrock Client initialized in {self.region}")
        else:
            logger.warning("Bedrock credentials missing. Client disabled.")

    def _init_client(self):
        """Helper to initialize client in thread-safe way if needed"""
        if not hasattr(self, "_client"):
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
        return self._client

    async def generate(
        self, model: str, messages: list[dict[str, str]], max_tokens: int = 4096, **kwargs
    ) -> APIResponse:
        """Generate response from Bedrock model."""
        if not self.enabled:
            return APIResponse(
                content=None,
                model=model,
                provider="bedrock",
                error="Bedrock client not initialized (missing AWS credentials?)",
            )

        start_time = time.time()

        try:
            # Simple body construction for Claude (most common Bedrock model for this project)
            # In a full implementation, this would handle different schemas for different models
            body = json.dumps(
                {
                    "anthropic_version": kwargs.get("anthropic_version", "bedrock-2023-05-31"),
                    "max_tokens": max_tokens,
                    "messages": messages,
                }
            )

            # Initialize client if needed (technically this part might blocking briefly on first run)
            # We can defer it to loop if strictly needed, but client creation is usually fast enough
            # unless it does heavy auth calls.
            if not hasattr(self, "_client"):
                await asyncio.to_thread(self._init_client)

            logger.info(f"Generating with Bedrock model: {model}")

            # Run blocking boto3 call in thread
            def _invoke():
                return self._client.invoke_model(
                    body=body,
                    modelId=model,
                    accept="application/json",
                    contentType="application/json",
                )

            response = await asyncio.to_thread(_invoke)

            latency = (time.time() - start_time) * 1000

            response_body = json.loads(response.get("body").read())

            # Extract content (assuming Claude structure)
            content_text = ""
            if "content" in response_body:
                for block in response_body["content"]:
                    if block["type"] == "text":
                        content_text += block["text"]

            usage = response_body.get("usage", {})

            return APIResponse(
                content=content_text,
                model=model,
                provider="bedrock",
                usage={
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                },
                latency_ms=latency,
            )

        except Exception as e:
            logger.error(f"Bedrock generation failed: {e}")
            return APIResponse(
                content=None,
                model=model,
                provider="bedrock",
                error=str(e),
                usage={},
                latency_ms=0.0,
            )


class BedrockAPIClient(BaseAPIClient):
    """
    Amazon Bedrock API client.

    Status: EXPERIMENTAL

    This client wraps the BedrockClient.
    Bedrock requires AWS credentials and optionally boto3.

    To use Bedrock models:
    1. Install boto3: pip install boto3
    2. Configure AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
    """

    def __init__(self, region: str = "us-east-1", **kwargs):
        # Bedrock uses AWS credentials, not API keys
        super().__init__("", f"https://bedrock-runtime.{region}.amazonaws.com")
        self.region = region
        self.anthropic_version = kwargs.get("api_version", "bedrock-2023-05-31")
        self._warned = False

        self._bedrock_client = BedrockClient(region_name=region)

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
        """
        Send chat completion request to Amazon Bedrock.

        Note: This is an experimental client.
        """
        if not self._warned:
            logger.warning(
                "BedrockAPIClient is EXPERIMENTAL. "
                "Bedrock requires AWS Signature V4 authentication via boto3."
            )
            self._warned = True

        # Check if Bedrock client is enabled
        if not self._bedrock_client.enabled:
            error_msg = "Bedrock provider is not configured (boto3 not installed or missing AWS credentials)."
            if functions:
                error_msg += " Additionally, Bedrock function calling requires model-specific tool definitions."
            return APIResponse(
                content=None,
                model=model,
                provider="bedrock",
                usage={"input_tokens": 0, "output_tokens": 0},
                latency_ms=0,
                raw_response={"error": error_msg},
                error=error_msg,
            )

        # Delegate to the actual Bedrock client (async call)
        try:
            response = await self._bedrock_client.generate(
                model=model,
                messages=messages,
                max_tokens=max_tokens or 4096,
                anthropic_version=self.anthropic_version,
            )
            return response
        except Exception as e:
            logger.error(f"Bedrock generation failed: {e}")
            return APIResponse(
                content=None,
                model=model,
                provider="bedrock",
                usage={"input_tokens": 0, "output_tokens": 0},
                latency_ms=0,
                error=str(e),
            )
