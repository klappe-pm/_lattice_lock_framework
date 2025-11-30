from typing import Dict, Optional, List
from .types import TaskType, TaskRequirements, ModelCapabilities

class TaskAnalyzer:
    """Analyze prompts to determine task requirements"""

    def __init__(self):
        self.task_keywords = {
            TaskType.CODE_GENERATION: ["write", "implement", "create", "code", "function", "class", "script"],
            TaskType.DEBUGGING: ["debug", "fix", "error", "bug", "troubleshoot", "exception", "fail"],
            TaskType.REASONING: ["think", "reason", "analyze", "solve", "deduce", "why", "how"],
            TaskType.ARCHITECTURAL_DESIGN: ["design", "architect", "structure", "system", "pattern"],
            TaskType.DOCUMENTATION: ["document", "docstring", "readme", "explain", "comment"],
            TaskType.TESTING: ["test", "unit", "integration", "pytest", "mock"],
            TaskType.DATA_ANALYSIS: ["data", "analyze", "csv", "plot", "chart", "trend"],
        }

    def analyze(self, prompt: str) -> TaskRequirements:
        """Analyze prompt to determine task requirements"""
        prompt_lower = prompt.lower()

        # Detect task type
        detected_type = TaskType.GENERAL
        max_matches = 0

        for task_type, keywords in self.task_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in prompt_lower)
            if matches > max_matches:
                max_matches = matches
                detected_type = task_type

        # Estimate context requirements
        prompt_length = len(prompt)
        estimated_context = max(4000, prompt_length * 10)

        # Check for specific requirements
        requires_vision = any(word in prompt_lower for word in ["image", "picture", "screenshot", "visual"])
        requires_function = any(word in prompt_lower for word in ["function", "api", "tool", "call"])
        
        # Determine priority based on keywords
        priority = "balanced"
        if "fast" in prompt_lower or "quick" in prompt_lower:
            priority = "speed"
        elif "cheap" in prompt_lower or "cost" in prompt_lower:
            priority = "cost"
        elif "best" in prompt_lower or "quality" in prompt_lower or "complex" in prompt_lower:
            priority = "quality"

        return TaskRequirements(
            task_type=detected_type,
            min_context=estimated_context,
            require_vision=requires_vision,
            require_functions=requires_function,
            priority=priority
        )

class ModelScorer:
    """Score models against task requirements"""

    def score(self, model: ModelCapabilities, requirements: TaskRequirements) -> float:
        """Score model fitness for task requirements (0.0 to 1.0)"""
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
            # Weight reasoning and coding heavily
            score += (model.reasoning_score / 100.0) * 0.3
            score += (model.coding_score / 100.0) * 0.2
        elif requirements.priority == "speed":
            # Weight speed heavily
            score += (model.speed_rating / 10.0) * 0.5
        elif requirements.priority == "cost":
            # Weight cost heavily (inverse of cost)
            # Normalize cost: assume $60 is max expensive (o1-pro)
            cost_factor = 1.0 - (model.blended_cost / 60.0)
            score += max(0, cost_factor) * 0.5
        else: # Balanced
            score += (model.reasoning_score / 100.0) * 0.2
            score += (model.coding_score / 100.0) * 0.2
            score += (model.speed_rating / 10.0) * 0.1

        # Task specific boosts
        if requirements.task_type == TaskType.CODE_GENERATION or requirements.task_type == TaskType.DEBUGGING:
            score += (model.coding_score / 100.0) * 0.2
        
        if requirements.task_type == TaskType.REASONING or requirements.task_type == TaskType.ARCHITECTURAL_DESIGN:
            score += (model.reasoning_score / 100.0) * 0.2

        return min(1.0, score)
