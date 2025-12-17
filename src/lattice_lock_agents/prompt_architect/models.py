from typing import Any, Optional

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    id: Optional[str] = None
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
    project_name: Optional[str] = None
    phases: list[Phase] = Field(default_factory=list)
    components: list[Component] = Field(default_factory=list)
    requirements: list[Requirement] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    raw_content: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
