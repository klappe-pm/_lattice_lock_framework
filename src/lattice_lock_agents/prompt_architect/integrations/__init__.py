"""
Integrations module for the Prompt Architect Agent.

Provides integration clients for interacting with other agents
and external systems.
"""

from lattice_lock_agents.prompt_architect.integrations.project_agent import (
    ProjectAgentClient,
    ProjectScope,
    ProjectPhase,
    PendingTask,
)

# Registry of available integration clients
INTEGRATION_REGISTRY = {
    "project_agent": ProjectAgentClient,
}


def get_integration_client(integration_name: str, **kwargs):
    """
    Get an integration client by name.

    Args:
        integration_name: Name of the integration (e.g., "project_agent").
        **kwargs: Additional arguments to pass to the client constructor.

    Returns:
        Integration client instance.

    Raises:
        ValueError: If the integration is not found.
    """
    client_class = INTEGRATION_REGISTRY.get(integration_name)
    if client_class is None:
        available = ", ".join(INTEGRATION_REGISTRY.keys())
        raise ValueError(
            f"Unknown integration: {integration_name}. Available: {available}"
        )
    return client_class(**kwargs)


def list_integrations():
    """
    List all available integrations.

    Returns:
        List of integration names.
    """
    return list(INTEGRATION_REGISTRY.keys())


__all__ = [
    "ProjectAgentClient",
    "ProjectScope",
    "ProjectPhase",
    "PendingTask",
    "get_integration_client",
    "list_integrations",
    "INTEGRATION_REGISTRY",
]
