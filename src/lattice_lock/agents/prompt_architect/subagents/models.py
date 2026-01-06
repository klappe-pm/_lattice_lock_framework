"""
Data models for the Specification Analyzer subagent.

Defines Pydantic models for structured specification analysis output.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _utc_now() -> datetime:
    """Get current UTC time in a timezone-aware manner."""
    return datetime.now(timezone.utc)


from pydantic import BaseModel, Field


class RequirementType(str, Enum):
    """Types of requirements that can be extracted from specifications."""

    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"
    INTERFACE = "interface"
    PERFORMANCE = "performance"
    SECURITY = "security"


class ConstraintType(str, Enum):
    """Types of constraints that can be extracted from specifications."""

    TECHNICAL = "technical"
    BUSINESS = "business"
    REGULATORY = "regulatory"
    RESOURCE = "resource"
    TIME = "time"
    DEPENDENCY = "dependency"


class ComponentLayer(str, Enum):
    """Architectural layers for components."""

    PRESENTATION = "presentation"
    APPLICATION = "application"
    DOMAIN = "domain"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"
    INTEGRATION = "integration"


class Requirement(BaseModel):
    """A requirement extracted from a specification document."""

    id: str = Field(..., description="Unique identifier for the requirement")
    description: str = Field(..., description="Description of the requirement")
    priority: str = Field(
        default="medium", description="Priority level (critical, high, medium, low)"
    )
    phase: str | None = Field(default=None, description="Phase this requirement belongs to")
    requirement_type: RequirementType = Field(
        default=RequirementType.FUNCTIONAL, description="Type of requirement"
    )
    source_section: str | None = Field(
        default=None, description="Source section in the specification document"
    )
    acceptance_criteria: list[str] = Field(
        default_factory=list, description="Acceptance criteria for this requirement"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="IDs of requirements this depends on"
    )

    model_config = {"extra": "allow"}


class Constraint(BaseModel):
    """A constraint extracted from a specification document."""

    id: str = Field(..., description="Unique identifier for the constraint")
    description: str = Field(..., description="Description of the constraint")
    constraint_type: ConstraintType = Field(
        default=ConstraintType.TECHNICAL, description="Type of constraint"
    )
    source_section: str | None = Field(
        default=None, description="Source section in the specification document"
    )
    impact: str | None = Field(default=None, description="Impact of this constraint on the project")
    mitigation: str | None = Field(
        default=None, description="Mitigation strategy for this constraint"
    )

    model_config = {"extra": "allow"}


class Component(BaseModel):
    """A component extracted from a specification document."""

    name: str = Field(..., description="Name of the component")
    description: str | None = Field(default=None, description="Description of the component")
    layer: ComponentLayer = Field(
        default=ComponentLayer.APPLICATION, description="Architectural layer"
    )
    interfaces: list[str] = Field(
        default_factory=list, description="Interfaces this component implements"
    )
    files: list[str] = Field(
        default_factory=list, description="Files associated with this component"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Names of components this depends on"
    )
    responsibilities: list[str] = Field(
        default_factory=list, description="Responsibilities of this component"
    )

    model_config = {"extra": "allow"}


class Phase(BaseModel):
    """A project phase extracted from a specification document."""

    name: str = Field(..., description="Name of the phase")
    description: str | None = Field(default=None, description="Description of the phase")
    scope: str | None = Field(default=None, description="Scope of the phase")
    components: list[str] = Field(
        default_factory=list, description="Components involved in this phase"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Names of phases this depends on"
    )
    deliverables: list[str] = Field(default_factory=list, description="Deliverables for this phase")
    start_date: datetime | None = Field(default=None, description="Planned start date")
    end_date: datetime | None = Field(default=None, description="Planned end date")

    model_config = {"extra": "allow"}


class SpecificationMetadata(BaseModel):
    """Metadata about the specification document."""

    title: str | None = Field(default=None, description="Title of the specification")
    version: str | None = Field(default=None, description="Version of the specification")
    author: str | None = Field(default=None, description="Author of the specification")
    last_updated: datetime | None = Field(default=None, description="Last update timestamp")
    source_file: str | None = Field(default=None, description="Path to the source file")
    file_format: str | None = Field(
        default=None, description="Format of the source file (md, yaml, json)"
    )

    model_config = {"extra": "allow"}


class SpecificationAnalysis(BaseModel):
    """Complete analysis result from a specification document."""

    phases: list[Phase] = Field(
        default_factory=list, description="Phases extracted from the specification"
    )
    components: list[Component] = Field(
        default_factory=list, description="Components extracted from the specification"
    )
    requirements: list[Requirement] = Field(
        default_factory=list, description="Requirements extracted from the specification"
    )
    constraints: list[Constraint] = Field(
        default_factory=list, description="Constraints extracted from the specification"
    )
    metadata: SpecificationMetadata = Field(
        default_factory=SpecificationMetadata,
        description="Metadata about the specification",
    )
    raw_sections: dict[str, Any] = Field(
        default_factory=dict,
        description="Raw sections extracted from the document for reference",
    )
    analysis_timestamp: datetime = Field(
        default_factory=_utc_now, description="Timestamp of the analysis"
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the analysis (0.0 to 1.0)",
    )
    llm_assisted: bool = Field(default=False, description="Whether LLM was used for extraction")
    warnings: list[str] = Field(
        default_factory=list, description="Warnings generated during analysis"
    )

    model_config = {"extra": "allow"}

    def to_dict(self) -> dict[str, Any]:
        """Convert the analysis to a dictionary for JSON serialization."""
        return self.model_dump(mode="json")

    def get_phase_by_name(self, name: str) -> Phase | None:
        """Get a phase by its name."""
        for phase in self.phases:
            if phase.name.lower() == name.lower():
                return phase
        return None

    def get_component_by_name(self, name: str) -> Component | None:
        """Get a component by its name."""
        for component in self.components:
            if component.name.lower() == name.lower():
                return component
        return None

    def get_requirements_by_phase(self, phase_name: str) -> list[Requirement]:
        """Get all requirements for a specific phase."""
        return [
            req
            for req in self.requirements
            if req.phase and req.phase.lower() == phase_name.lower()
        ]

    def get_requirements_by_type(self, requirement_type: RequirementType) -> list[Requirement]:
        """Get all requirements of a specific type."""
        return [req for req in self.requirements if req.requirement_type == requirement_type]


__all__ = [
    "RequirementType",
    "ConstraintType",
    "ComponentLayer",
    "Requirement",
    "Constraint",
    "Component",
    "Phase",
    "SpecificationMetadata",
    "SpecificationAnalysis",
]
