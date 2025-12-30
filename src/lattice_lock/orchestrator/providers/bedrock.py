"""
AWS Bedrock Provider
"""

import asyncio
import json
import logging
import os
import time
from typing import Any

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError
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
    """Helper class for Bedrock logic"""

    def __init__(self, region: str, access_key: str | None, secret_key: str | None):
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key

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

    async def generate(self, model: str, body: str) -> dict:
        if not hasattr(self, "_client"):
            await asyncio.to_thread(self._init_client)

        def _invoke():
            return self._client.invoke_model(
                body=body,
                modelId=model,
                accept="application/json",
                contentType="application/json",
            )

        return await asyncio.to_thread(_invoke)


class BedrockAPIClient(BaseAPIClient):
    """
    Amazon Bedrock API client.
    """

    def __init__(self, config: AppConfig, region: str = "us-east-1", **kwargs):
        # Bedrock uses AWS credentials
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.access_key = kwargs.get("aws_access_key_id") or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = kwargs.get("aws_secret_access_key") or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.anthropic_version = kwargs.get("api_version", "bedrock-2023-05-31")
        self._bedrock_client = None

        super().__init__(config)

    def _validate_config(self) -> None:
        if not _BOTO3_AVAILABLE:
            raise ProviderUnavailableError("bedrock", "boto3 library not installed")
        if not self.access_key or not self.secret_key:
            raise ProviderUnavailableError(
                "bedrock", "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY required"
            )

    async def health_check(self) -> bool:
        # Check if we can initialize client
        try:
            self._bedrock_client = BedrockClient(self.region, self.access_key, self.secret_key)
            # Could try to list foundation models if we had 'bedrock' (control plane) client,
            # but we only have 'bedrock-runtime'. Runtime doesn't have simple ping.
            return True
        except Exception as e:
            raise ProviderUnavailableError("bedrock", str(e))

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        functions: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs,
    ) -> APIResponse:

        if not self._bedrock_client:
            self._bedrock_client = BedrockClient(self.region, self.access_key, self.secret_key)

        start_time = time.time()

        # Simple body construction for Claude (most common Bedrock model for this project)
        # Note: This assumes Claude models. For modularity, we might need model-specific formatters later.

        # Clean messages
        clean_messages = []
        for msg in messages:
            clean_messages.append({"role": msg["role"], "content": str(msg["content"])})

        body = json.dumps(
            {
                "anthropic_version": self.anthropic_version,
                "max_tokens": max_tokens or 4096,
                "messages": clean_messages,
                "temperature": temperature,
            }
        )

        try:
            response = await self._bedrock_client.generate(model, body)
            latency = (time.time() - start_time) * 1000

            response_body = json.loads(response.get("body").read())

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
