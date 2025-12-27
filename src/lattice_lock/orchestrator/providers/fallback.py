import asyncio
import logging
from collections.abc import Callable
from typing import Any

from lattice_lock.exceptions import ProviderUnavailableError

from ..types import APIResponse

logger = logging.getLogger(__name__)


class FallbackManager:
    """Manages execution resilience across multiple model providers."""

    def __init__(self, max_retries: int = 1):
        self.max_retries = max_retries

    async def execute_with_fallback(
        self, func: Callable[..., Any], candidates: list[Any], *args, **kwargs
    ) -> APIResponse:
        """
        Attempt execution of `func` against each candidate in order and return the first successful APIResponse.

        Args:
            func: Callable that accepts a candidate as its first argument followed by any additional args/kwargs.
            candidates: Ordered list of candidate objects (for example model instances or clients) to try.
            *args: Positional arguments forwarded to `func` after the candidate.
            **kwargs: Keyword arguments forwarded to `func` after the candidate.

        Returns:
            APIResponse: The response returned by the first successful `func` invocation.

        Raises:
            ProviderUnavailableError: If every candidate (including allowed retries per candidate) fails; the exception includes the last observed error.
        """
        last_error = None

        for i, candidate in enumerate(candidates):
            logger.info(f"Attempting execution with candidate {i+1}/{len(candidates)}: {candidate}")

            # Simple retry logic for the current candidate
            for attempt in range(self.max_retries + 1):
                try:
                    # Handle both sync and async functions naturally if we can,
                    # but pure async is preferred. For now we assume the func might be awaitable.
                    if asyncio.iscoroutinefunction(func):
                        return await func(candidate, *args, **kwargs)
                    else:
                        # If strict async is required, we could wrap this in to_thread
                        # But typically the func passed here will be an async client method
                        return func(candidate, *args, **kwargs)

                except Exception as e:
                    logger.warning(
                        f"Candidate {candidate} failed (attempt {attempt+1}/{self.max_retries+1}): {e}"
                    )
                    last_error = e
                    if attempt < self.max_retries:
                        await asyncio.sleep(0.5 * (2**attempt))  # Exponential backoff

            logger.warning(f"Falling back from candidate {candidate} due to persistent failure.")

        logger.error("All candidates exhausted. raising ProviderUnavailableError.")
        raise ProviderUnavailableError(
            "all_providers", f"All providers failed. Last error: {last_error}"
        )
