"""
Prompt Architect Agent Package

Contains the Prompt Architect agent and its subagents for specification analysis
and prompt generation.
"""

from lattice_lock_agents.prompt_architect.agent import (
    AgentConfig,
    GenerationResult,
    PromptArchitectAgent,
)
from lattice_lock_agents.prompt_architect.orchestrator import (
    OrchestrationConfig,
    OrchestrationState,
    PipelineStage,
    PromptOrchestrator,
    orchestrate_prompt_generation,
)
from lattice_lock_agents.prompt_architect.subagents.models import (
    Component,
    ComponentLayer,
    Constraint,
    ConstraintType,
    Phase,
    Requirement,
    RequirementType,
    SpecificationAnalysis,
)
from lattice_lock_agents.prompt_architect.subagents.spec_analyzer import SpecAnalyzer
from lattice_lock_agents.prompt_architect.tracker_client import PromptEntry, TrackerClient

__all__ = [
    # Core agent
    "PromptArchitectAgent",
    "AgentConfig",
    "GenerationResult",
    # Orchestrator
    "PromptOrchestrator",
    "OrchestrationConfig",
    "OrchestrationState",
    "PipelineStage",
    "orchestrate_prompt_generation",
    # Subagents
    "SpecAnalyzer",
    "SpecificationAnalysis",
    "Phase",
    "Component",
    "Requirement",
    "Constraint",
    "RequirementType",
    "ConstraintType",
    "ComponentLayer",
    # Tracker
    "TrackerClient",
    "PromptEntry",
]
