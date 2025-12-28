"""
Task Analyzer v2 for the Lattice Lock Orchestrator.

This module provides:
- TaskAnalyzer: Analyzes prompts using hybrid signal processing
- TaskAnalysis: Comprehensive analysis result with multi-label support
"""

import hashlib
import logging
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..types import TaskRequirements, TaskType
from .semantic_router import SemanticRouter

logger = logging.getLogger(__name__)


def _hash_prompt(prompt: str) -> str:
    """Create a SHA-256 hash of the prompt for cache key."""
    return hashlib.sha256(prompt.encode()).hexdigest()


@dataclass
class TaskAnalysis:
    """
    Comprehensive task analysis result with multi-label support.

    Attributes:
        primary_type: The most likely task type
        secondary_types: Additional relevant task types sorted by confidence
        scores: Raw confidence scores for each task type (0.0-1.0)
        features: Extracted features from the prompt
        complexity: Estimated complexity ("simple", "moderate", "complex")
        min_context_window: Minimum recommended context window
    """

    primary_type: TaskType
    secondary_types: list[TaskType] = field(default_factory=list)
    scores: dict[TaskType, float] = field(default_factory=dict)
    features: dict[str, Any] = field(default_factory=dict)
    complexity: str = "moderate"
    min_context_window: int = 4000


class TaskAnalyzer:
    """
    Analyzes prompts to determine task requirements using hybrid signal processing.
    """

    DEFAULT_CACHE_SIZE = 1024

    def __init__(
        self,
        cache_size: int = DEFAULT_CACHE_SIZE,
        router_client: Any = None,
        patterns_path: Path | None = None,
    ):
        self._cache: OrderedDict[str, TaskAnalysis] = OrderedDict()
        self._cache_size = cache_size
        self._cache_hits = 0
        self._cache_misses = 0
        self._router = SemanticRouter(router_client) if router_client else None

        if patterns_path is None:
            patterns_path = Path(__file__).parent / "patterns.yaml"
        self._patterns_path = patterns_path
        self._keyword_patterns, self._regex_patterns = self._load_and_compile(patterns_path)

    def _load_and_compile(self, path: Path) -> tuple[dict, dict]:
        """Load patterns from YAML and compile regexes."""
        keyword_patterns = {}
        regex_patterns = {}

        try:
            import yaml

            if path.exists():
                with open(path) as f:
                    data = yaml.safe_load(f)

                # Load keywords
                raw_keywords = data.get("keyword_patterns", {})
                for task_name, patterns in raw_keywords.items():
                    try:
                        task_type = TaskType[task_name]
                        keyword_patterns[task_type] = [(p[0], p[1]) for p in patterns]
                    except KeyError:
                        logger.warning(f"Unknown TaskType in patterns.yaml: {task_name}")

                # Load and compile regexes
                raw_regexes = data.get("regex_patterns", {})
                for task_name, patterns in raw_regexes.items():
                    try:
                        task_type = TaskType[task_name]
                        regex_patterns[task_type] = []
                        for pattern_str, weight in patterns:
                            try:
                                compiled = re.compile(pattern_str, re.IGNORECASE)
                                regex_patterns[task_type].append((compiled, weight))
                            except re.error as e:
                                logger.error(f"Invalid regex pattern '{pattern_str}': {e}")
                    except KeyError:
                        logger.warning(f"Unknown TaskType in patterns.yaml: {task_name}")

        except ImportError:
            logger.warning("PyYAML not installed. TaskAnalyzer functionality will be limited.")
        except Exception as e:
            logger.error(f"Failed to load patterns from {path}: {e}")

        return keyword_patterns, regex_patterns

    def analyze(self, prompt: str) -> TaskRequirements:
        """
        Analyzes a user prompt to extract task requirements (Synchronous).
        Note: This does not engage the semantic router as it requires async.
        """
        analysis = self.analyze_full(prompt)

        return TaskRequirements(
            task_type=analysis.primary_type,
            min_context=analysis.min_context_window,
            require_vision=analysis.features.get("requires_vision", False),
            require_functions=analysis.features.get("requires_function_calling", False),
            priority=analysis.features.get("priority", "balanced"),
        )

    async def analyze_async(self, prompt: str) -> TaskRequirements:
        """
        Analyzes a user prompt to extract task requirements (Asynchronous).
        Can engage the semantic router if heuristics are uncertain.
        """
        analysis = await self.analyze_full_async(prompt)

        return TaskRequirements(
            task_type=analysis.primary_type,
            min_context=analysis.min_context_window,
            require_vision=analysis.features.get("requires_vision", False),
            require_functions=analysis.features.get("requires_function_calling", False),
            priority=analysis.features.get("priority", "balanced"),
        )

    def analyze_full(self, prompt: str) -> TaskAnalysis:
        """
        Performs full task analysis with multi-label classification (Synchronous).
        """
        prompt_hash = _hash_prompt(prompt)

        if prompt_hash in self._cache:
            self._cache_hits += 1
            self._cache.move_to_end(prompt_hash)
            return self._cache[prompt_hash]

        self._cache_misses += 1
        analysis = self._analyze_uncached(prompt)

        self._cache[prompt_hash] = analysis
        self._cache.move_to_end(prompt_hash)

        while len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)

        return analysis

    async def analyze_full_async(self, prompt: str) -> TaskAnalysis:
        """
        Performs full task analysis with multi-label classification (Asynchronous).
        """
        prompt_hash = _hash_prompt(prompt)

        if prompt_hash in self._cache:
            self._cache_hits += 1
            self._cache.move_to_end(prompt_hash)
            return self._cache[prompt_hash]

        self._cache_misses += 1
        analysis = await self._analyze_uncached_async(prompt)

        self._cache[prompt_hash] = analysis
        self._cache.move_to_end(prompt_hash)

        while len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)

        return analysis

    async def _analyze_uncached_async(self, prompt: str) -> TaskAnalysis:
        """
        Performs the actual task analysis without caching (Asynchronous).
        """
        # Run standard heuristics (re-purposing the sync logic)
        analysis = self._analyze_uncached(prompt)

        # Stage 2: Semantic Router if heuristics are uncertain
        max_heuristic_score = max(analysis.scores.values()) if analysis.scores.values() else 0.0
        if max_heuristic_score < 0.5 and len(prompt) > 10 and self._router:
            logger.info(
                f"Heuristics uncertain (score={max_heuristic_score:.2f}). Engaging Semantic Router."
            )
            semantic_type = await self._router.route(prompt)
            if semantic_type != TaskType.GENERAL:
                # Boost the semantic result
                analysis.scores[semantic_type] = 0.9
                analysis.primary_type = semantic_type
                logger.info(f"Semantic Router classified task as: {semantic_type.name}")

        return analysis

    def _analyze_uncached(self, prompt: str) -> TaskAnalysis:
        """
        Performs the actual task analysis without caching.
        """
        prompt_lower = prompt.lower()
        scores: dict[TaskType, float] = dict.fromkeys(TaskType, 0.0)
        features: dict[str, Any] = {}

        # 1. Keyword scoring
        for task_type, patterns in self._keyword_patterns.items():
            for keyword, weight in patterns:
                if keyword in prompt_lower:
                    scores[task_type] += weight

        # 2. Regex pattern scoring
        for task_type, patterns in self._regex_patterns.items():
            for compiled_regex, weight in patterns:
                if compiled_regex.search(prompt):
                    scores[task_type] += weight

        # 3. Structural heuristics
        features["has_code_blocks"] = bool(re.search(r"```", prompt))
        features["has_stack_trace"] = bool(re.search(r"traceback|at line \d+", prompt_lower))
        features["is_question"] = prompt.strip().endswith("?") or prompt_lower.startswith(
            ("how", "why", "what", "can")
        )
        features["prompt_length"] = len(prompt)
        features["has_error_message"] = bool(re.search(r"error|exception|fail", prompt_lower))

        # Apply heuristic boosts
        if features["has_code_blocks"]:
            scores[TaskType.CODE_GENERATION] += 0.3
            scores[TaskType.DEBUGGING] += 0.1

        if features["has_stack_trace"]:
            scores[TaskType.DEBUGGING] += 0.8

        if features["has_error_message"]:
            scores[TaskType.DEBUGGING] += 0.2

        if features["is_question"]:
            scores[TaskType.REASONING] += 0.1

        # 4. Detect special requirements
        features["requires_vision"] = any(
            word in prompt_lower
            for word in ["image", "picture", "screenshot", "photo", "visual", "diagram"]
        )
        features["requires_function_calling"] = any(
            word in prompt_lower
            for word in ["function call", "api call", "tool use", "external api"]
        )

        if features["requires_vision"]:
            scores[TaskType.VISION] += 0.8

        # Stage 2: Semantic Router if heuristics are uncertain
        # No async semantic call in sync method; return heuristic result as is.

        # 5. Determine priority
        if "fast" in prompt_lower or "quick" in prompt_lower or "urgent" in prompt_lower:
            features["priority"] = "speed"
        elif "cheap" in prompt_lower or "low cost" in prompt_lower or "budget" in prompt_lower:
            features["priority"] = "cost"
        elif (
            "best" in prompt_lower
            or "quality" in prompt_lower
            or "complex" in prompt_lower
            or "accurate" in prompt_lower
        ):
            features["priority"] = "quality"
        else:
            features["priority"] = "balanced"

        # 6. Normalize scores to 0-1 range
        max_score = max(scores.values()) if scores.values() else 1.0
        if max_score > 0:
            normalized_scores = {k: min(1.0, v / max(max_score, 1.0)) for k, v in scores.items()}
        else:
            normalized_scores = scores

        # 7. Determine primary and secondary types
        sorted_types = sorted(
            [(task_type, score) for task_type, score in normalized_scores.items() if score > 0],
            key=lambda x: x[1],
            reverse=True,
        )

        if sorted_types:
            primary_type = sorted_types[0][0]
            primary_score = sorted_types[0][1]
            secondary_types = [
                task_type
                for task_type, score in sorted_types[1:]
                if score >= primary_score * 0.3 and score > 0.2
            ][:3]
        else:
            # Fallback for no matches
            primary_type = TaskType.GENERAL
            secondary_types = []

        # 8. Estimate complexity
        complexity = self._estimate_complexity(prompt, features, normalized_scores)

        # 9. Estimate context window needs
        min_context = self._estimate_context_window(prompt, features, complexity)

        return TaskAnalysis(
            primary_type=primary_type,
            secondary_types=secondary_types,
            scores=normalized_scores,
            features=features,
            complexity=complexity,
            min_context_window=min_context,
        )

    def _estimate_complexity(
        self, prompt: str, features: dict[str, Any], scores: dict[TaskType, float]
    ) -> str:
        """Estimates task complexity based on various signals."""
        complexity_score = 0.0
        prompt_lower = prompt.lower()

        length = features.get("prompt_length", len(prompt))
        if length > 2000:
            complexity_score += 0.4
        elif length > 500:
            complexity_score += 0.15
        elif length > 200:
            complexity_score += 0.1

        high_scoring_types = sum(1 for score in scores.values() if score > 0.4)
        if high_scoring_types > 2:
            complexity_score += 0.3
        elif high_scoring_types > 1:
            complexity_score += 0.1

        if scores.get(TaskType.ARCHITECTURAL_DESIGN, 0) > 0.5:
            complexity_score += 0.35

        if features.get("has_code_blocks") and features.get("has_stack_trace"):
            complexity_score += 0.3
        elif features.get("has_stack_trace"):
            complexity_score += 0.15

        complex_words = [
            "comprehensive",
            "enterprise",
            "distributed",
            "high availability",
            "fault tolerant",
            "memory leak",
        ]
        moderate_words = ["complete", "crud", "full"]

        if any(word in prompt_lower for word in complex_words):
            complexity_score += 0.4
        elif any(word in prompt_lower for word in ["complex"]):
            complexity_score += 0.25
        elif any(word in prompt_lower for word in moderate_words):
            complexity_score += 0.1

        simple_words = ["simple", "basic", "hello world", "quick", "factorial"]
        if any(word in prompt_lower for word in simple_words):
            complexity_score -= 0.3

        if "comprehensive" in prompt_lower and scores.get(TaskType.TESTING, 0) > 0.3:
            complexity_score += 0.3
        elif "integration" in prompt_lower and scores.get(TaskType.TESTING, 0) > 0.3:
            complexity_score += 0.1

        if complexity_score >= 0.5:
            return "complex"
        elif complexity_score >= 0.15:
            return "moderate"
        else:
            return "simple"

    def _estimate_context_window(
        self, prompt: str, features: dict[str, Any], complexity: str
    ) -> int:
        """Estimates minimum context window needed."""
        base_context = len(prompt) * 10

        if complexity == "complex":
            base_context = max(base_context, 32000)
        elif complexity == "moderate":
            base_context = max(base_context, 8000)
        else:
            base_context = max(base_context, 4000)

        if features.get("has_code_blocks"):
            base_context = max(base_context, 16000)

        return min(base_context, 200000)

    def get_task_scores(self, prompt: str) -> dict[TaskType, float]:
        """
        Returns confidence scores for all task types.
        """
        analysis = self.analyze_full(prompt)
        return analysis.scores

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Returns cache statistics for monitoring and debugging.
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0.0
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self._cache_size,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": hit_rate,
        }

    def clear_cache(self) -> None:
        """Clears the analysis cache."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
