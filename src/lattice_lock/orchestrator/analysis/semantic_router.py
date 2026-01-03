"""
Semantic Router for the Lattice Lock Orchestrator.

This module provides:
- SemanticRouter: Second-stage router that uses LLM-based intent classification
"""

import logging

from ..types import TaskType

logger = logging.getLogger(__name__)


class SemanticRouter:
    """
    Second-stage router that uses LLM-based intent classification.
    """

    ROUTER_PROMPT = """
    Analyze the following user prompt and classify it into one of the TaskTypes:
    {types}

    Return ONLY the name of the TaskType that best matches the intent.
    If no type matches well, return GENERAL.

    Prompt: {prompt}
    """

    def __init__(self, client=None):
        self.client = client

    async def route(self, prompt: str) -> TaskType:
        """Routes a prompt to a TaskType using an LLM."""
        if not self.client:
            return TaskType.GENERAL

        types_str = ", ".join([t.name for t in TaskType])
        full_prompt = self.ROUTER_PROMPT.format(types=types_str, prompt=prompt)

        try:
            # Use a fast, cheap model for routing if possible
            response = await self.client.chat_completion(
                model="gpt-4o-mini",  # Fallback default
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=10,
                temperature=0.0,
            )

            result = response.content.strip()
            for t in TaskType:
                if t.name in result:
                    return t
            return TaskType.GENERAL
        except Exception as e:
            logger.warning(f"Semantic routing failed: {e}")
            return TaskType.GENERAL
