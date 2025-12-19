import logging
from pathlib import Path

from lattice_lock_agents.prompt_architect.integrations.project_agent import ProjectAgentClient

logger = logging.getLogger(__name__)


def test_project_agent_client_integration():
    """Verify ProjectAgentClient functionality in the test environment."""
    logger.info("Initializing ProjectAgentClient...")
    client = ProjectAgentClient(repo_root=Path.cwd())

    # Test Scope Discovery
    logger.info("Testing get_project_scope()...")
    scope = client.get_project_scope()
    assert scope.name is not None
    logger.info(f"Scope: {scope.name}")

    # Test Phase Discovery
    logger.info("Testing get_current_phase()...")
    phase = client.get_current_phase()
    if phase:
        logger.info(f"Current Phase: {phase.name} ({phase.status})")

    # Test Pending Tasks
    logger.info("Testing get_pending_tasks()...")
    tasks = client.get_pending_tasks()
    logger.info(f"Found {len(tasks)} pending tasks")

    # Test Path Discovery
    logger.info("Testing get_specification_path()...")
    spec_path = client.get_specification_path()
    logger.info(f"Spec Path: {spec_path}")

    logger.info("Testing get_roadmap_path()...")
    roadmap_path = client.get_roadmap_path()
    logger.info(f"Roadmap Path: {roadmap_path}")
    assert roadmap_path is not None, "Should find the roadmap file"
