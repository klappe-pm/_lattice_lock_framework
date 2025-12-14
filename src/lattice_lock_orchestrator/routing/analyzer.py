import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TaskAnalyzer:
    """
    Analyzes prompts to determine task type and requirements.
    Uses a hybrid approach: Regex Heuristics -> LLM Router (Fallback).
    """
    def __init__(self):
        self.patterns = {
            "CODE_GENERATION": [r"def .+\(", r"class .+\:", r"import .+"].copy(),
            "TESTING": [r"test", r"pytest", r"assert", r"mock"].copy(),
            "DEBUGGING": [r"fix", r"error", r"exception", r"traceback", r"debug"].copy()
        }

    def analyze(self, user_prompt: str) -> str:
        """Determines the TaskType from the prompt string."""
        logger.debug(f"Analyzing prompt (len={len(user_prompt)})")

        # 1. Fast Heuristics
        for task_type, regexes in self.patterns.items():
            for pattern in regexes:
                if re.search(pattern, user_prompt, re.IGNORECASE):
                    logger.info(f"Task classified as {task_type} via regex heuristic.")
                    return task_type

        # 2. Fallback
        logger.info("Heuristics uncertain. Defaulting to GENERAL (LLM router not active).")
        return "GENERAL"
