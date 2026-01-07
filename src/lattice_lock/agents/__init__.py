"""
Lattice Lock Agent System.

Provides agent implementations for the Lattice Lock Framework.

The Approver Agent is ENABLED BY DEFAULT and serves as the single authority
for all testing and quality approval workflows.
"""

from lattice_lock.agents.prompt_architect import (
    PromptArchitectAgent,
    PromptOrchestrator,
    SpecAnalyzer,
    TrackerClient,
)
from lattice_lock.agents.settings import (
    AgentSettings,
    get_coverage_target,
    get_settings,
    is_approver_enabled,
    load_settings,
    reset_settings,
)

__all__ = [
    # Prompt Architect
    "PromptArchitectAgent",
    "PromptOrchestrator",
    "SpecAnalyzer",
    "TrackerClient",
    # Settings
    "AgentSettings",
    "get_settings",
    "load_settings",
    "reset_settings",
    "is_approver_enabled",
    "get_coverage_target",
]

__version__ = "0.1.0"
