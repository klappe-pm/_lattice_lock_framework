from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Requirement(BaseModel):
    id: Optional[str] = None
    description: str
    type: str = "functional"  # functional, non-functional
    priority: str = "medium"

class Component(BaseModel):
    name: str
    description: str
    dependencies: List[str] = Field(default_factory=list)

class Phase(BaseModel):
    name: str
    description: str
    components: List[str] = Field(default_factory=list)

class Constraint(BaseModel):
    description: str
    type: str = "general"

class SpecificationAnalysis(BaseModel):
    project_name: Optional[str] = None
    phases: List[Phase] = Field(default_factory=list)
    components: List[Component] = Field(default_factory=list)
    requirements: List[Requirement] = Field(default_factory=list)
    constraints: List[Constraint] = Field(default_factory=list)
    raw_content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
