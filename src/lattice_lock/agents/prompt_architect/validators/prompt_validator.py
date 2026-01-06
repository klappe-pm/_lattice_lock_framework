"""Prompt validator for ensuring generated prompts meet quality standards."""

import logging
import os
import re
from typing import Any

from pydantic import BaseModel, Field

from .utils import parse_sections

logger = logging.getLogger(__name__)


class SectionValidation(BaseModel):
    """Validation result for a single section."""

    section_name: str
    is_valid: bool
    is_present: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    content_length: int = 0


class ValidationResult(BaseModel):
    """Complete validation result for a prompt."""

    prompt_path: str
    is_valid: bool
    sections: dict[str, SectionValidation] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_error(self, error: str) -> None:
        """Add a global error."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a global warning."""
        self.warnings.append(warning)


class PromptValidator:
    """Validates prompt files against the agent specification format."""

    # Required sections and their validation rules
    REQUIRED_SECTIONS = {
        "Context": {
            "min_length": 50,
            "required_patterns": [],
            "description": "Must reference relevant files/specs",
        },
        "Goal": {
            "min_length": 20,
            "required_patterns": [],
            "description": "Must be single, clear objective",
        },
        "Steps": {
            "min_length": 50,
            "required_patterns": [r"^\d+\.", r"^-\s"],  # Numbered or bulleted list
            "description": "Must be 4-8 specific, actionable items",
        },
        "Do NOT Touch": {
            "min_length": 10,
            "required_patterns": [r"^-\s"],  # Bulleted list
            "description": "Must list files owned by other tools",
        },
        "Success Criteria": {
            "min_length": 20,
            "required_patterns": [r"^-\s"],  # Bulleted list
            "description": "Must be measurable",
        },
    }

    OPTIONAL_SECTIONS = {"Notes": {"min_length": 10, "description": "Optional but recommended"}}

    # Header patterns
    HEADER_PATTERN = re.compile(r"^#\s+Prompt\s+(\d+\.\d+\.\d+)\s*-\s*(.+)$", re.MULTILINE)
    METADATA_PATTERNS = {
        "tool": re.compile(r"^\*\*Tool:\*\*\s*(.+)$", re.MULTILINE),
        "epic": re.compile(r"^\*\*Epic:\*\*\s*(.+)$", re.MULTILINE),
        "phase": re.compile(r"^\*\*Phase:\*\*\s*(.+)$", re.MULTILINE),
    }

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, treat warnings as errors
        """
        self.strict_mode = strict_mode

    def validate(self, prompt_path: str) -> ValidationResult:
        """
        Validate a prompt file.

        Args:
            prompt_path: Path to the prompt file

        Returns:
            ValidationResult with all validation details
        """
        result = ValidationResult(prompt_path=prompt_path, is_valid=True)

        # Check file exists
        if not os.path.exists(prompt_path):
            result.add_error(f"Prompt file not found: {prompt_path}")
            return result

        # Read file content
        try:
            with open(prompt_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"Failed to read prompt file: {e}")
            return result

        # Validate structure
        self._validate_header(content, result)
        self._validate_metadata(content, result)
        self._validate_sections(content, result)

        # Check for overall validity
        if result.errors or self.strict_mode and result.warnings:
            result.is_valid = False

        return result

    def validate_content(self, content: str, prompt_id: str = "inline") -> ValidationResult:
        """
        Validate prompt content directly (useful for pre-write validation).

        Args:
            content: The prompt content to validate
            prompt_id: Identifier for the prompt

        Returns:
            ValidationResult with all validation details
        """
        result = ValidationResult(prompt_path=prompt_id, is_valid=True)

        self._validate_header(content, result)
        self._validate_metadata(content, result)
        self._validate_sections(content, result)

        if result.errors or self.strict_mode and result.warnings:
            result.is_valid = False

        return result

    def _validate_header(self, content: str, result: ValidationResult) -> None:
        """Validate the prompt header format."""
        match = self.HEADER_PATTERN.search(content)
        if not match:
            result.add_error(
                "Missing or invalid prompt header. Expected format: '# Prompt X.Y.Z - Title'"
            )
        else:
            result.metadata["prompt_id"] = match.group(1)
            result.metadata["title"] = match.group(2).strip()

    def _validate_metadata(self, content: str, result: ValidationResult) -> None:
        """Validate the metadata section (Tool, Epic, Phase)."""
        for key, pattern in self.METADATA_PATTERNS.items():
            match = pattern.search(content)
            if not match:
                result.add_error(f"Missing metadata: **{key.capitalize()}:**")
            else:
                result.metadata[key] = match.group(1).strip()

    def _validate_sections(self, content: str, result: ValidationResult) -> None:
        """Validate all required and optional sections."""
        # Parse sections from content
        # Parse sections from content
        sections = parse_sections(content)

        # Validate required sections
        for section_name, rules in self.REQUIRED_SECTIONS.items():
            section_content = sections.get(section_name, "")
            validation = self._validate_section(section_name, section_content, rules, required=True)
            result.sections[section_name] = validation

            if not validation.is_valid:
                for error in validation.errors:
                    result.add_error(error)
            for warning in validation.warnings:
                result.add_warning(warning)

        # Validate optional sections
        for section_name, rules in self.OPTIONAL_SECTIONS.items():
            section_content = sections.get(section_name, "")
            validation = self._validate_section(
                section_name, section_content, rules, required=False
            )
            result.sections[section_name] = validation

            for warning in validation.warnings:
                result.add_warning(warning)

    def _validate_section(
        self, name: str, content: str, rules: dict[str, Any], required: bool
    ) -> SectionValidation:
        """Validate a single section against its rules."""
        validation = SectionValidation(
            section_name=name, is_valid=True, is_present=bool(content), content_length=len(content)
        )

        # Check presence
        if not content:
            if required:
                validation.is_valid = False
                validation.errors.append(f"Missing required section: ## {name}")
            else:
                validation.warnings.append(f"Optional section not present: ## {name}")
            return validation

        # Check minimum length
        min_length = rules.get("min_length", 0)
        if len(content) < min_length:
            validation.warnings.append(
                f"Section '{name}' is shorter than recommended ({len(content)} < {min_length} chars)"
            )

        # Check required patterns
        required_patterns = rules.get("required_patterns", [])
        if required_patterns:
            has_pattern = any(
                re.search(pattern, content, re.MULTILINE) for pattern in required_patterns
            )
            if not has_pattern:
                validation.warnings.append(
                    f"Section '{name}' may not follow expected format. {rules.get('description', '')}"
                )

        # Section-specific validation
        if name == "Steps":
            self._validate_steps_section(content, validation)
        elif name == "Goal":
            self._validate_goal_section(content, validation)
        elif name == "Context":
            self._validate_context_section(content, validation)
        elif name == "Success Criteria":
            self._validate_success_criteria_section(content, validation)

        return validation

    def _validate_steps_section(self, content: str, validation: SectionValidation) -> None:
        """Validate the Steps section has 4-8 items."""
        # Count numbered steps
        steps = re.findall(r"^\d+\.", content, re.MULTILINE)
        num_steps = len(steps)

        if num_steps < 4:
            validation.warnings.append(
                f"Steps section has only {num_steps} items. Recommended: 4-8 steps."
            )
        elif num_steps > 8:
            validation.warnings.append(
                f"Steps section has {num_steps} items. Consider breaking into smaller tasks (recommended: 4-8)."
            )

    def _validate_goal_section(self, content: str, validation: SectionValidation) -> None:
        """Validate the Goal section is a single, clear objective."""
        # Check for multiple sentences that might indicate multiple goals
        sentences = re.split(r"(?<=[.!?])\s+", content.strip())
        if len(sentences) > 3:
            validation.warnings.append(
                "Goal section may contain multiple objectives. Consider focusing on a single goal."
            )

    def _validate_context_section(self, content: str, validation: SectionValidation) -> None:
        """Validate the Context section references files or specs."""
        # Check for file references (backticks with paths)
        file_refs = re.findall(r"`[^`]+\.(py|md|yaml|json|txt|toml)`", content)
        dir_refs = re.findall(r"`[^`]+/`", content)

        if not file_refs and not dir_refs:
            validation.warnings.append(
                "Context section should reference specific files or directories (use backticks)."
            )

    def _validate_success_criteria_section(
        self, content: str, validation: SectionValidation
    ) -> None:
        """Validate the Success Criteria section contains measurable items."""
        # Check for bullet points
        bullets = re.findall(r"^-\s", content, re.MULTILINE)
        if len(bullets) < 2:
            validation.warnings.append("Success Criteria should list multiple measurable outcomes.")

        # Check for action words that indicate measurable criteria
        action_patterns = [
            r"\bworks?\b",
            r"\bpass(es)?\b",
            r"\breturns?\b",
            r"\bshows?\b",
            r"\bcreates?\b",
            r"\bvalidates?\b",
            r"\bcatches?\b",
            r"\bprovides?\b",
        ]
        has_action = any(re.search(pattern, content, re.IGNORECASE) for pattern in action_patterns)
        if not has_action:
            validation.warnings.append(
                "Success Criteria should use action verbs for measurability."
            )
