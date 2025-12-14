import re
import logging
import hashlib
from typing import Optional, Dict
from functools import lru_cache

logger = logging.getLogger(__name__)

class TaskAnalyzer:
    """
    Analyzes prompts to determine task type and requirements.
    Uses a hybrid approach: Regex Heuristics -> LLM Router (Fallback).
    """
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator # Dependency injection for LLM calls
        self.patterns = {
            "CODE_GENERATION": [r"def .+\(", r"class .+\:", r"import .+", r"implement", r"function"].copy(),
            "TESTING": [r"test", r"pytest", r"assert", r"mock", r"coverage"].copy(),
            "DEBUGGING": [r"fix", r"error", r"exception", r"traceback", r"debug", r"fail", r"broken"].copy(),
            "ARCHITECTURAL_DESIGN": [r"design", r"architecture", r"document", r"plan", r"diagram"].copy(),
            "DOCUMENTATION": [r"docstring", r"readme", r"comment"].copy()
        }

    @lru_cache(maxsize=1000)
    def analyze(self, user_prompt: str) -> str:
        """
        Determines the TaskType from the prompt string.
        Results are cached to improve performance.
        """
        prompt_hash = hashlib.sha256(user_prompt.encode()).hexdigest() # Verify hash stability if needed
        logger.debug(f"Analyzing prompt (hash={prompt_hash[:8]})")

        # 1. Fast Heuristics (Stage 1)
        heuristic_result = self._run_heuristics(user_prompt)
        if heuristic_result:
            return heuristic_result

        # 2. Semantic Router (Stage 2 - LLM)
        logger.info("Heuristics uncertain (>0.8 not met). engaging Semantic Router.")
        return self._run_semantic_router(user_prompt)

    def _run_heuristics(self, prompt: str) -> Optional[str]:
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
             # Placeholder for actual LLM call via orchestrator
             # in production: response = self.orchestrator.complete(prompt=ROUTER_PROMPT.format(prompt))
             # parsing response...
             logger.info("Mocking Semantic Router response (not implemented fully).")
             return "GENERAL" 
        except Exception as e:
            logger.error(f"Semantic Router failed: {e}")
            return "GENERAL"

