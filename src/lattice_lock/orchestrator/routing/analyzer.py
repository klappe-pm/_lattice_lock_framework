import hashlib
import logging
import re
from collections import OrderedDict

logger = logging.getLogger(__name__)

ROUTER_PROMPT = """
Analyze the following user prompt and classify it into one of these TaskTypes:
CODE_GENERATION, TESTING, DEBUGGING, ARCHITECTURAL_DESIGN, DOCUMENTATION, GENERAL

Return ONLY the name of the TaskType.

Prompt: {}
"""


def _hash_prompt(prompt: str) -> str:
    """Create a SHA-256 hash of the prompt for cache key."""
    return hashlib.sha256(prompt.encode()).hexdigest()


class TaskAnalyzer:
    """
    Analyzes prompts to determine task type and requirements.
    Uses a hybrid approach: Regex Heuristics -> LLM Router (Fallback).
    """

    DEFAULT_CACHE_SIZE = 1000

    def __init__(self, orchestrator=None, cache_size: int = DEFAULT_CACHE_SIZE):
        self.orchestrator = orchestrator  # Dependency injection for LLM calls
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._cache_size = cache_size
        self.patterns = {
            "CODE_GENERATION": [
                r"def .+\(",
                r"class .+\:",
                r"import .+",
                r"implement",
                r"function",
            ].copy(),
            "TESTING": [r"test", r"pytest", r"assert", r"mock", r"coverage"].copy(),
            "DEBUGGING": [
                r"fix",
                r"error",
                r"exception",
                r"traceback",
                r"debug",
                r"fail",
                r"broken",
            ].copy(),
            "ARCHITECTURAL_DESIGN": [
                r"design",
                r"architecture",
                r"document",
                r"plan",
                r"diagram",
            ].copy(),
            "DOCUMENTATION": [r"docstring", r"readme", r"comment"].copy(),
        }

    def analyze(self, user_prompt: str) -> str:
        """
        Determines the TaskType from the prompt string.
        Results are cached using a manual LRU cache to avoid memory leaks.
        """
        prompt_hash = _hash_prompt(user_prompt)
        logger.debug(f"Analyzing prompt (hash={prompt_hash[:8]})")

        # Check cache first
        if prompt_hash in self._cache:
            self._cache.move_to_end(prompt_hash)
            return self._cache[prompt_hash]

        # 1. Fast Heuristics (Stage 1)
        heuristic_result = self._run_heuristics(user_prompt)
        if heuristic_result:
            result = heuristic_result
        else:
            # 2. Semantic Router (Stage 2 - LLM)
            logger.info("Heuristics uncertain (>0.8 not met). engaging Semantic Router.")
            result = self._run_semantic_router(user_prompt)

        # Store in cache with LRU eviction
        self._cache[prompt_hash] = result
        self._cache.move_to_end(prompt_hash)
        while len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)

        return result

    def _run_heuristics(self, prompt: str) -> str | None:
        """Run regex-based heuristics."""
        # Check against patterns
        # Simple implementation: First match wins. v2 could use weighting.
        for task_type, regexes in self.patterns.items():
            for pattern in regexes:
                if re.search(pattern, prompt, re.IGNORECASE):
                    # In a real v2, we'd calculate a confidence score here.
                    # For now, regex match is treated as high confidence for simplicity,
                    # or we can be stricter and require multiple keywords.
                    # Let's assume regex match is sufficient for Stage 1 verified types.
                    logger.info(f"Task classified as {task_type} via regex heuristic.")
                    return task_type
        return None

    def _run_semantic_router(self, prompt: str) -> str:
        """Run LLM-based classification."""
        if not self.orchestrator:
            logger.warning("No orchestrator available for Semantic Router. Defaulting to GENERAL.")
            return "GENERAL"

        try:
            # Actual LLM call via orchestrator
            # Note: We assume the orchestrator has a sync-compatible way to call models
            # or we try to use the client directly if possible.
            # For this legacy implementation, we'll try to use a simple 'complete' call if it exists.
            if hasattr(self.orchestrator, "complete"):
                response = self.orchestrator.complete(prompt=ROUTER_PROMPT.format(prompt))
                result = response.strip().upper()
                if result in self.patterns or result == "GENERAL":
                    logger.info(f"Semantic Router classified task as {result}")
                    return result

            logger.info(
                "Semantic Router response uncertain or not implemented on orchestrator. Defaulting to GENERAL."
            )
            return "GENERAL"
        except Exception as e:
            logger.error(f"Semantic Router failed: {e}")
            return "GENERAL"
