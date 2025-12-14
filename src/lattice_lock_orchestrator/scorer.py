"""
Task Analyzer v2 and Model Scorer for the Lattice Lock Orchestrator.

This module provides:
- TaskAnalyzer: Analyzes prompts using hybrid signal processing
- TaskAnalysis: Comprehensive analysis result with multi-label support
- ModelScorer: Scores models based on capabilities and requirements
"""

import hashlib
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from .types import ModelCapabilities, TaskRequirements, TaskType


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

    Version 2 improvements:
    - Multi-signal classification (keywords, regex patterns, structural heuristics)
    - Multi-label classification (prompts can have multiple task types)
    - Confidence scoring for each task type
    - Feature extraction for additional context
    - LRU caching by prompt hash for performance
    """

    DEFAULT_CACHE_SIZE = 1024

    def __init__(self, cache_size: int = DEFAULT_CACHE_SIZE):
        self._cache: OrderedDict[str, TaskAnalysis] = OrderedDict()
        self._cache_size = cache_size
        self._cache_hits = 0
        self._cache_misses = 0
        # Keyword patterns with weights
        self.keyword_patterns: dict[TaskType, list[tuple[str, float]]] = {
            TaskType.CODE_GENERATION: [
                ("write", 0.3),
                ("implement", 0.4),
                ("create", 0.3),
                ("code", 0.3),
                ("function", 0.3),
                ("class", 0.3),
                ("script", 0.3),
                ("program", 0.3),
                ("build", 0.2),
                ("generate", 0.3),
                ("develop", 0.3),
                ("make", 0.2),
            ],
            TaskType.DEBUGGING: [
                ("debug", 0.6),
                ("fix", 0.5),
                ("error", 0.5),
                ("bug", 0.6),
                ("troubleshoot", 0.5),
                ("exception", 0.5),
                ("fail", 0.4),
                ("broken", 0.4),
                ("issue", 0.3),
                ("crash", 0.5),
                ("wrong", 0.2),
                ("not working", 0.5),
                ("why is", 0.3),
                ("re-rendering", 0.3),
            ],
            TaskType.REASONING: [
                ("think", 0.3),
                ("reason", 0.4),
                ("analyze", 0.3),
                ("solve", 0.3),
                ("deduce", 0.4),
                ("why", 0.3),
                ("how", 0.3),
                ("explain", 0.4),
                ("understand", 0.4),
                ("logic", 0.4),
                ("evaluate", 0.3),
                ("consider", 0.2),
                ("approach", 0.3),
                ("best", 0.2),
            ],
            TaskType.ARCHITECTURAL_DESIGN: [
                ("design", 0.4),
                ("architect", 0.5),
                ("structure", 0.3),
                ("system", 0.3),
                ("pattern", 0.4),
                ("architecture", 0.5),
                ("scalable", 0.3),
                ("microservice", 0.4),
                ("api design", 0.4),
                ("database design", 0.4),
                ("schema", 0.3),
                ("blueprint", 0.4),
            ],
            TaskType.DOCUMENTATION: [
                ("document", 0.5),
                ("docstring", 0.5),
                ("readme", 0.5),
                ("comment", 0.3),
                ("wiki", 0.4),
                ("guide", 0.3),
                ("tutorial", 0.4),
                ("manual", 0.3),
                ("documentation", 0.5),
            ],
            TaskType.TESTING: [
                ("test", 0.4),
                ("unit test", 0.5),
                ("integration", 0.3),
                ("pytest", 0.5),
                ("mock", 0.4),
                ("coverage", 0.4),
                ("assert", 0.4),
                ("spec", 0.3),
                ("e2e", 0.4),
                ("qa", 0.3),
                ("validate", 0.3),
                ("verify", 0.3),
            ],
            TaskType.DATA_ANALYSIS: [
                ("data", 0.3),
                ("csv", 0.4),
                ("plot", 0.4),
                ("chart", 0.4),
                ("trend", 0.4),
                ("statistics", 0.4),
                ("pandas", 0.5),
                ("dataframe", 0.5),
                ("visualization", 0.4),
                ("graph", 0.3),
                ("analysis", 0.3),
                ("metric", 0.3),
            ],
            TaskType.VISION: [
                ("image", 0.5),
                ("picture", 0.5),
                ("photo", 0.5),
                ("screenshot", 0.5),
                ("visual", 0.4),
                ("diagram", 0.4),
                ("see", 0.2),
                ("look at", 0.3),
                ("analyze this image", 0.6),
                ("ocr", 0.5),
                ("recognize", 0.3),
            ],
            TaskType.GENERAL: [
                ("help", 0.2),
                ("question", 0.2),
                ("what", 0.1),
                ("tell me", 0.2),
                ("can you", 0.1),
            ],
            TaskType.SECURITY_AUDIT: [
                ("security", 0.5),
                ("vulnerability", 0.6),
                ("exploit", 0.5),
                ("injection", 0.6),
                ("xss", 0.6),
                ("csrf", 0.6),
                ("authentication", 0.3),
                ("authorization", 0.3),
                ("oauth", 0.4),
                ("penetration", 0.5),
                ("audit", 0.4),
                ("secure", 0.3),
                ("sql injection", 0.7),
                ("sanitize", 0.4),
                ("encrypt", 0.4),
            ],
            TaskType.CREATIVE_WRITING: [
                ("story", 0.5),
                ("creative", 0.4),
                ("write a story", 0.6),
                ("poem", 0.5),
                ("narrative", 0.4),
                ("fiction", 0.5),
                ("character", 0.3),
                ("plot", 0.3),
                ("dialogue", 0.4),
                ("novel", 0.4),
                ("essay", 0.3),
                ("blog post", 0.4),
            ],
        }

        # Strong regex patterns for high-confidence detection
        self.regex_patterns: dict[TaskType, list[tuple[str, float]]] = {
            TaskType.CODE_GENERATION: [
                (r"def\s+\w+\s*\(", 0.6),  # Python function definition
                (r"class\s+\w+", 0.5),  # Class definition
                (r"function\s+\w+", 0.5),  # JS function
                (r"import\s+\w+", 0.3),  # Import statements
                (r"```\w*\n", 0.4),  # Code blocks
            ],
            TaskType.DEBUGGING: [
                (r"traceback", 0.8),  # Python traceback
                (r"error:\s*", 0.6),  # Error messages
                (r"exception", 0.5),  # Exception
                (r"line\s+\d+", 0.4),  # Line numbers in errors
                (r"TypeError|ValueError|KeyError|AttributeError", 0.7),
                (r"stack\s*trace", 0.7),
            ],
            TaskType.TESTING: [
                (r"@pytest", 0.7),
                (r"def\s+test_", 0.7),
                (r"assert\s+", 0.5),
                (r"unittest", 0.6),
                (r"\.test\(\)", 0.5),
            ],
            TaskType.DATA_ANALYSIS: [
                (r"pd\.", 0.6),  # Pandas
                (r"df\[", 0.5),  # DataFrame access
                (r"\.csv", 0.5),
                (r"\.xlsx", 0.5),
                (r"matplotlib|seaborn|plotly", 0.6),
            ],
        }

    def analyze(self, prompt: str) -> TaskRequirements:
        """
        Analyzes a user prompt to extract task requirements.

        This is the backwards-compatible interface that returns TaskRequirements.
        For the full analysis, use analyze_full().

        Args:
            prompt: The user's input prompt.

        Returns:
            TaskRequirements: The analyzed requirements.
        """
        analysis = self.analyze_full(prompt)

        return TaskRequirements(
            task_type=analysis.primary_type,
            min_context=analysis.min_context_window,
            require_vision=analysis.features.get("requires_vision", False),
            require_functions=analysis.features.get("requires_function_calling", False),
            priority=analysis.features.get("priority", "balanced"),
        )

    def analyze_full(self, prompt: str) -> TaskAnalysis:
        """
        Performs full task analysis with multi-label classification.

        Uses LRU caching by prompt hash for performance optimization.

        Args:
            prompt: The user's input prompt.

        Returns:
            TaskAnalysis: Comprehensive analysis result.
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

    def _analyze_uncached(self, prompt: str) -> TaskAnalysis:
        """
        Performs the actual task analysis without caching.

        Args:
            prompt: The user's input prompt.

        Returns:
            TaskAnalysis: Comprehensive analysis result.
        """
        prompt_lower = prompt.lower()
        scores: dict[TaskType, float] = dict.fromkeys(TaskType, 0.0)
        features: dict[str, Any] = {}

        # 1. Keyword scoring
        for task_type, patterns in self.keyword_patterns.items():
            for keyword, weight in patterns:
                if keyword in prompt_lower:
                    scores[task_type] += weight

        # 2. Regex pattern scoring
        for task_type, patterns in self.regex_patterns.items():
            for pattern, weight in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
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
            # Secondary types are those with score >= 0.3 of primary (multi-label)
            primary_score = sorted_types[0][1]
            secondary_types = [
                task_type
                for task_type, score in sorted_types[1:]
                if score >= primary_score * 0.3 and score > 0.2
            ][
                :3
            ]  # Max 3 secondary types
        else:
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

        # Length-based complexity
        length = features.get("prompt_length", len(prompt))
        if length > 2000:
            complexity_score += 0.4
        elif length > 500:
            complexity_score += 0.15
        elif length > 200:
            complexity_score += 0.1

        # Multi-task complexity (multiple high-scoring task types)
        high_scoring_types = sum(1 for score in scores.values() if score > 0.4)
        if high_scoring_types > 2:
            complexity_score += 0.3
        elif high_scoring_types > 1:
            complexity_score += 0.1

        # Architectural tasks are usually complex
        if scores.get(TaskType.ARCHITECTURAL_DESIGN, 0) > 0.5:
            complexity_score += 0.35

        # Code blocks with stack traces suggest substantial debugging
        if features.get("has_code_blocks") and features.get("has_stack_trace"):
            complexity_score += 0.3
        elif features.get("has_stack_trace"):
            complexity_score += 0.15

        # Complexity keywords - weight appropriately
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

        # Simple indicators reduce complexity
        simple_words = ["simple", "basic", "hello world", "quick", "factorial"]
        if any(word in prompt_lower for word in simple_words):
            complexity_score -= 0.3

        # Testing comprehensive suites vs simple tests
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
        base_context = len(prompt) * 10  # 10x prompt length for response

        if complexity == "complex":
            base_context = max(base_context, 32000)
        elif complexity == "moderate":
            base_context = max(base_context, 8000)
        else:
            base_context = max(base_context, 4000)

        # Architectural tasks need more context
        if features.get("has_code_blocks"):
            base_context = max(base_context, 16000)

        return min(base_context, 200000)  # Cap at 200K

    def get_task_scores(self, prompt: str) -> dict[TaskType, float]:
        """
        Returns confidence scores for all task types.

        This is a convenience method for quick scoring without full analysis.

        Args:
            prompt: The user's input prompt.

        Returns:
            Dict mapping TaskType to confidence score (0.0-1.0).
        """
        analysis = self.analyze_full(prompt)
        return analysis.scores

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Returns cache statistics for monitoring and debugging.

        Returns:
            Dict with cache_size, cache_hits, cache_misses, hit_rate.
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


class ModelScorer:
    """
    Scores models based on their capabilities and task requirements.

    Updated to support TaskAnalysis for multi-label scoring.
    """

    def score(self, model: ModelCapabilities, requirements: TaskRequirements) -> float:
        """
        Calculates a fitness score for a model given the task requirements.

        Args:
            model: The model to score.
            requirements: The requirements of the task.

        Returns:
            float: A score between 0.0 and 1.0, where higher is better.
        """
        score = 0.0

        # Hard requirements (disqualifying if not met)
        if requirements.min_context > model.context_window:
            return 0.0
        if requirements.require_vision and not model.supports_vision:
            return 0.0
        if requirements.require_functions and not model.supports_function_calling:
            return 0.0

        # Base score starts at 0.5
        score = 0.5

        # Adjust based on priority
        if requirements.priority == "quality":
            score += (model.reasoning_score / 100.0) * 0.3
            score += (model.coding_score / 100.0) * 0.2
        elif requirements.priority == "speed":
            score += (model.speed_rating / 10.0) * 0.5
        elif requirements.priority == "cost":
            cost_factor = 1.0 - (model.blended_cost / 60.0)
            score += max(0, cost_factor) * 0.5
        else:  # Balanced
            score += (model.reasoning_score / 100.0) * 0.2
            score += (model.coding_score / 100.0) * 0.2
            score += (model.speed_rating / 10.0) * 0.1

        # Task specific boosts
        if requirements.task_type in (TaskType.CODE_GENERATION, TaskType.DEBUGGING):
            score += (model.coding_score / 100.0) * 0.2

        if requirements.task_type in (TaskType.REASONING, TaskType.ARCHITECTURAL_DESIGN):
            score += (model.reasoning_score / 100.0) * 0.2

        return min(1.0, score)

    def score_with_analysis(self, model: ModelCapabilities, analysis: TaskAnalysis) -> float:
        """
        Scores a model using full TaskAnalysis for multi-label support.

        This considers both primary and secondary task types for better matching.

        Args:
            model: The model to score.
            analysis: Full task analysis result.

        Returns:
            float: A score between 0.0 and 1.0.
        """
        # Hard requirements check
        if analysis.min_context_window > model.context_window:
            return 0.0
        if analysis.features.get("requires_vision") and not model.supports_vision:
            return 0.0
        if (
            analysis.features.get("requires_function_calling")
            and not model.supports_function_calling
        ):
            return 0.0

        score = 0.5

        # Get model's task scores
        model_task_scores = model.task_scores

        # Weight primary task type heavily
        primary_match = model_task_scores.get(analysis.primary_type, 0.5)
        score += primary_match * 0.3

        # Weight secondary task types
        for secondary_type in analysis.secondary_types[:2]:
            secondary_match = model_task_scores.get(secondary_type, 0.5)
            score += secondary_match * 0.1

        # Priority adjustments
        priority = analysis.features.get("priority", "balanced")
        if priority == "quality":
            score += (model.reasoning_score / 100.0) * 0.1
        elif priority == "speed":
            score += (model.speed_rating / 10.0) * 0.2
        elif priority == "cost":
            cost_factor = 1.0 - (model.blended_cost / 60.0)
            score += max(0, cost_factor) * 0.2

        # Complexity adjustment - complex tasks favor high-capability models
        if analysis.complexity == "complex":
            score += (model.reasoning_score / 100.0) * 0.1

        return min(1.0, score)
