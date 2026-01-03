from typing import Any

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    id: str | None = None
    description: str
    type: str = "functional"  # functional, non-functional
    priority: str = "medium"


class Component(BaseModel):
    name: str
    description: str
    dependencies: list[str] = Field(default_factory=list)


class Phase(BaseModel):
    name: str
    description: str
    components: list[str] = Field(default_factory=list)


class Constraint(BaseModel):
    description: str
    type: str = "general"


class SpecificationAnalysis(BaseModel):
    project_name: str | None = None
    phases: list[Phase] = Field(default_factory=list)
    components: list[Component] = Field(default_factory=list)
    requirements: list[Requirement] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    raw_content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationRequest(BaseModel):
    """Request for prompt generation."""

    project_name: str | None = None
    phase: str | None = None
    epic: str | None = None
    task_ids: list[str] = Field(default_factory=list)
    force_regenerate: bool = False
    dry_run: bool = False
    output_directory: str = "project_prompts"


class GenerationResult(BaseModel):
    """Result of a prompt generation run."""

    status: str  # success, failure, partial
    prompts_generated: int = 0
    prompts_updated: int = 0
    prompts_skipped: int = 0
    phases_covered: list[str] = Field(default_factory=list)
    tool_distribution: dict[str, int] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    execution_time_seconds: float | None = None
    generated_prompts: list[Any] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump()
