"""LLM-assisted quality scoring for prompts."""

import re
import os
import json
import logging
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from .utils import parse_sections

logger = logging.getLogger(__name__)


class QualityScore(BaseModel):
    """Quality score result for a prompt."""

    prompt_path: str
    overall_score: float = 0.0  # 1-10 scale
    clarity_score: float = 0.0  # 1-10 scale
    actionability_score: float = 0.0  # 1-10 scale
    completeness_score: float = 0.0  # 1-10 scale
    passes_threshold: bool = True
    needs_review: bool = False
    feedback: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QualityScorer:
    """
    LLM-assisted quality scoring for prompts.

    Provides both heuristic and LLM-based scoring with configurable thresholds.
    """

    # Default quality threshold (1-10 scale)
    DEFAULT_THRESHOLD = 6.0

    # Heuristic weights
    WEIGHTS = {
        "clarity": 0.35,
        "actionability": 0.40,
        "completeness": 0.25,
    }

    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        use_llm: bool = True,
        llm_client: Optional[Any] = None,
        model: str = "codellama:34b"
    ):
        """
        Initialize the quality scorer.

        Args:
            threshold: Minimum score to pass (1-10)
            use_llm: Whether to use LLM for scoring
            llm_client: Optional LLM client for scoring
            model: Model to use for LLM scoring
        """
        self.threshold = threshold
        self.use_llm = use_llm
        self.llm_client = llm_client
        self.model = model

    async def score(self, prompt_path: str) -> QualityScore:
        """
        Score a prompt file.

        Args:
            prompt_path: Path to the prompt file

        Returns:
            QualityScore with all scores and feedback
        """
        result = QualityScore(prompt_path=prompt_path)

        # Read file content
        if not os.path.exists(prompt_path):
            result.feedback.append(f"File not found: {prompt_path}")
            result.needs_review = True
            return result

        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            result.feedback.append(f"Failed to read file: {e}")
            result.needs_review = True
            return result

        return await self.score_content(content, prompt_path)

    async def score_content(self, content: str, prompt_id: str = "inline") -> QualityScore:
        """
        Score prompt content directly.

        Args:
            content: The prompt content
            prompt_id: Identifier for the prompt

        Returns:
            QualityScore with all scores and feedback
        """
        result = QualityScore(prompt_path=prompt_id)

        # Parse sections
        # Parse sections
        sections = parse_sections(content)

        # Score each dimension
        result.clarity_score = self._score_clarity(content, sections)
        result.actionability_score = self._score_actionability(sections)
        result.completeness_score = self._score_completeness(sections)

        # Calculate weighted overall score
        result.overall_score = (
            result.clarity_score * self.WEIGHTS["clarity"] +
            result.actionability_score * self.WEIGHTS["actionability"] +
            result.completeness_score * self.WEIGHTS["completeness"]
        )

        # LLM-assisted scoring if available
        if self.use_llm and self.llm_client:
            llm_scores = await self._get_llm_scores(content)
            if llm_scores:
                # Blend heuristic and LLM scores (60% heuristic, 40% LLM)
                result.clarity_score = 0.6 * result.clarity_score + 0.4 * llm_scores.get("clarity", result.clarity_score)
                result.actionability_score = 0.6 * result.actionability_score + 0.4 * llm_scores.get("actionability", result.actionability_score)
                result.completeness_score = 0.6 * result.completeness_score + 0.4 * llm_scores.get("completeness", result.completeness_score)

                # Recalculate overall
                result.overall_score = (
                    result.clarity_score * self.WEIGHTS["clarity"] +
                    result.actionability_score * self.WEIGHTS["actionability"] +
                    result.completeness_score * self.WEIGHTS["completeness"]
                )

                # Add LLM feedback
                if llm_scores.get("feedback"):
                    result.feedback.extend(llm_scores["feedback"])
                if llm_scores.get("suggestions"):
                    result.suggestions.extend(llm_scores["suggestions"])

        # Check threshold
        result.passes_threshold = result.overall_score >= self.threshold
        result.needs_review = result.overall_score < self.threshold

        # Generate feedback for low scores
        self._generate_feedback(result, sections)

        return result



    def _score_clarity(self, content: str, sections: Dict[str, str]) -> float:
        """Score prompt clarity (1-10)."""
        score = 5.0  # Start at neutral

        # Check title clarity
        title_match = re.search(r"^#\s+Prompt\s+\d+\.\d+\.\d+\s*-\s*(.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
            if len(title) > 10 and len(title) < 100:
                score += 1.0
            if re.search(r'\b(implement|create|add|fix|update|build)\b', title, re.I):
                score += 0.5

        # Check Goal section clarity
        goal = sections.get("Goal", "")
        if goal:
            sentences = re.split(r'(?<=[.!?])\s+', goal.strip())
            if 1 <= len(sentences) <= 3:
                score += 1.0  # Clear, focused goal
            if len(goal) > 20:
                score += 0.5

        # Check Context section clarity
        context = sections.get("Context", "")
        if context:
            # Has file references
            if re.search(r'`[^`]+`', context):
                score += 0.5
            # Reasonable length
            if 50 < len(context) < 500:
                score += 0.5
            # Mentions "existing" or "current" (shows context awareness)
            if re.search(r'\b(existing|current|has)\b', context, re.I):
                score += 0.5

        return min(max(score, 1.0), 10.0)

    def _score_actionability(self, sections: Dict[str, str]) -> float:
        """Score step actionability (1-10)."""
        score = 3.0  # Start lower

        steps = sections.get("Steps", "")
        if not steps:
            return score

        # Count numbered steps
        step_lines = re.findall(r"^\d+\.\s+.+", steps, re.MULTILINE)
        num_steps = len(step_lines)

        # Score based on step count (4-8 is ideal)
        if 4 <= num_steps <= 8:
            score += 2.0
        elif 2 <= num_steps < 4 or 8 < num_steps <= 10:
            score += 1.0

        # Check for action verbs in steps
        action_verbs = [
            r'\b(create|implement|add|update|fix|write|test|verify|run|check|ensure|validate|build)\b'
        ]
        action_count = 0
        for step in step_lines:
            for pattern in action_verbs:
                if re.search(pattern, step, re.I):
                    action_count += 1
                    break

        # Score based on action verb usage
        if num_steps > 0:
            action_ratio = action_count / num_steps
            score += action_ratio * 3.0

        # Check for specificity (file paths, function names)
        if re.search(r'`[^`]+`', steps):
            score += 1.0

        # Check for sub-steps (indicates detail)
        if re.search(r'^\s+-\s', steps, re.MULTILINE):
            score += 0.5

        return min(max(score, 1.0), 10.0)

    def _score_completeness(self, sections: Dict[str, str]) -> float:
        """Score prompt completeness (1-10)."""
        score = 0.0

        # Required sections present (each worth 1.5 points)
        required = ["Context", "Goal", "Steps", "Do NOT Touch", "Success Criteria"]
        for section in required:
            if sections.get(section):
                score += 1.5
                # Bonus for sufficient content
                if len(sections[section]) > 30:
                    score += 0.2

        # Notes section (optional but recommended)
        if sections.get("Notes"):
            score += 0.5

        # Check Success Criteria has measurable items
        success = sections.get("Success Criteria", "")
        if success:
            bullets = len(re.findall(r"^-\s", success, re.MULTILINE))
            if bullets >= 3:
                score += 0.5

        # Check Do NOT Touch has content
        do_not_touch = sections.get("Do NOT Touch", "")
        if do_not_touch:
            if len(re.findall(r"^-\s", do_not_touch, re.MULTILINE)) >= 2:
                score += 0.3

        return min(max(score, 1.0), 10.0)

    async def _get_llm_scores(self, content: str) -> Optional[Dict[str, Any]]:
        """Get LLM-assisted scores for the prompt."""
        if not self.llm_client:
            return None

        prompt = f"""Analyze this development prompt and score it on three dimensions.
Return a JSON object with these fields:
- clarity (1-10): How clear and unambiguous is the prompt?
- actionability (1-10): How actionable are the steps?
- completeness (1-10): Are all necessary details provided?
- feedback (list): List of issues found
- suggestions (list): List of improvement suggestions

Prompt to analyze:
---
{content}
---

Return ONLY the JSON object, no other text.
"""

        try:
            response = await self.llm_client.chat_completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            # Parse JSON from response
            response_text = response.content if hasattr(response, 'content') else str(response)
            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response_text)

        except Exception as e:
            logger.warning(f"LLM scoring failed: {e}")
            return None

    def _generate_feedback(self, result: QualityScore, sections: Dict[str, str]) -> None:
        """Generate actionable feedback based on scores."""
        if result.clarity_score < 6:
            result.feedback.append(
                "Low clarity score: Consider making the goal more specific and adding file references."
            )
            result.suggestions.append(
                "Add backtick-quoted file paths in Context section"
            )

        if result.actionability_score < 6:
            result.feedback.append(
                "Low actionability score: Steps may not be specific enough."
            )
            if "Steps" in sections:
                steps = sections["Steps"]
                if len(re.findall(r"^\d+\.", steps, re.MULTILINE)) < 4:
                    result.suggestions.append(
                        "Add more detailed steps (aim for 4-8 numbered steps)"
                    )
                if not re.search(r'`[^`]+`', steps):
                    result.suggestions.append(
                        "Include specific file paths or function names in steps"
                    )

        if result.completeness_score < 6:
            missing = []
            for section in ["Context", "Goal", "Steps", "Do NOT Touch", "Success Criteria"]:
                if section not in sections:
                    missing.append(section)
            if missing:
                result.feedback.append(
                    f"Missing sections: {', '.join(missing)}"
                )
                result.suggestions.append(
                    f"Add the following sections: {', '.join(missing)}"
                )

        # Add overall assessment
        if result.overall_score >= 8:
            result.feedback.append("Excellent prompt quality!")
        elif result.overall_score >= 6:
            result.feedback.append("Good prompt quality with minor improvements possible.")
        elif result.overall_score >= 4:
            result.feedback.append("Prompt needs improvement before use.")
        else:
            result.feedback.append("Prompt requires significant revision.")
