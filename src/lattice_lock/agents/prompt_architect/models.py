"""
Data models for the Prompt Architect Agent.

Defines the structures for prompt templates, contexts, and generation results.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ToolType(Enum):
    """Supported tool types for prompt generation."""

    DEVIN = "devin"
    GEMINI_CLI = "gemini_cli"
    CODEX_CLI = "codex_cli"
    CLAUDE_CLI = "claude_cli"
    CLAUDE_APP = "claude_app"
    CLAUDE_WEBSITE = "claude_website"


class PromptStatus(Enum):
    """Status of a generated prompt."""

    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class TaskPriority(Enum):
    """Priority levels for tasks."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FileOwnership:
    """Defines file ownership for a tool to prevent conflicts."""

    tool: ToolType
    paths: list[str]
    patterns: list[str] = field(default_factory=list)
    description: str = ""

    def owns_path(self, path: str) -> bool:
        """Check if this ownership covers a given path."""
        if path in self.paths:
            return True
        for pattern in self.patterns:
            if pattern.endswith("*"):
                if path.startswith(pattern[:-1]):
                    return True
            elif pattern in path:
                return True
        return False


@dataclass
class ToolCapability:
    """Describes the capabilities of a tool."""

    tool: ToolType
    name: str
    description: str
    strengths: list[str]
    limitations: list[str]
    file_ownership: list[FileOwnership] = field(default_factory=list)
    max_context_tokens: int = 100000
    supports_code_execution: bool = True
    supports_file_editing: bool = True
    supports_web_browsing: bool = False

    def can_handle_task(self, task_type: str, file_paths: list[str]) -> bool:
        """Check if this tool can handle a given task."""
        for ownership in self.file_ownership:
            for path in file_paths:
                if ownership.owns_path(path):
                    return True
        return False


@dataclass
class TaskAssignment:
    """Assignment of a task to a specific tool."""

    task_id: str
    task_name: str
    description: str
    tool: ToolType
    file_paths: list[str]
    dependencies: list[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_tokens: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class PromptContext:
    """Context information for prompt generation."""

    project_name: str
    phase_name: str
    epic_name: str
    task_id: str
    task_name: str
    description: str
    requirements: list[str]
    acceptance_criteria: list[str]
    dependencies: list[str] = field(default_factory=list)
    file_paths: list[str] = field(default_factory=list)
    do_not_touch: list[str] = field(default_factory=list)
    additional_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptTemplate:
    """Template for generating prompts."""

    name: str
    tool: ToolType
    sections: list[str]
    required_fields: list[str]
    optional_fields: list[str] = field(default_factory=list)
    template_content: str = ""

    def validate_context(self, context: PromptContext) -> list[str]:
        """Validate that context has all required fields."""
        errors = []
        for field_name in self.required_fields:
            if not hasattr(context, field_name):
                errors.append(f"Missing required field: {field_name}")
            elif getattr(context, field_name) is None:
                errors.append(f"Required field is None: {field_name}")
        return errors


@dataclass
class PromptOutput:
    """Generated prompt output."""

    prompt_id: str
    task_id: str
    tool: ToolType
    title: str
    content: str
    file_path: str
    status: PromptStatus = PromptStatus.DRAFT
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)


@dataclass
class GenerationRequest:
    """Request to generate prompts."""

    project_name: str
    phase: str | None = None
    epic: str | None = None
    task_ids: list[str] = field(default_factory=list)
    force_regenerate: bool = False
    dry_run: bool = False
    output_directory: str = "project_prompts"


@dataclass
class GenerationResult:
    """Result of prompt generation."""

    success: bool
    prompts_generated: int
    prompts_updated: int
    prompts_skipped: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    generated_prompts: list[PromptOutput] = field(default_factory=list)
    total_estimated_cost: float = 0.0
    execution_time_seconds: float = 0.0

    def add_prompt(self, prompt: PromptOutput) -> None:
        """Add a generated prompt to the result."""
        self.generated_prompts.append(prompt)
        self.prompts_generated += 1

    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)


@dataclass
class PhaseSpec:
    """Specification for a project phase."""

    phase_id: str
    name: str
    description: str
    epics: list["EpicSpec"]
    start_date: datetime | None = None
    end_date: datetime | None = None


@dataclass
class EpicSpec:
    """Specification for an epic within a phase."""

    epic_id: str
    name: str
    description: str
    tasks: list["TaskSpec"]
    dependencies: list[str] = field(default_factory=list)


@dataclass
class TaskSpec:
    """Specification for a task within an epic."""

    task_id: str
    name: str
    description: str
    requirements: list[str]
    acceptance_criteria: list[str]
    file_paths: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    estimated_hours: float = 0.0
    assigned_tool: ToolType | None = None


__all__ = [
    "ToolType",
    "PromptStatus",
    "TaskPriority",
    "FileOwnership",
    "ToolCapability",
    "TaskAssignment",
    "PromptContext",
    "PromptTemplate",
    "PromptOutput",
    "GenerationRequest",
    "GenerationResult",
    "PhaseSpec",
    "EpicSpec",
    "TaskSpec",
]
