"""
Integration tests for Prompt Architect and Project Agent integration.

Tests the ProjectAgentClient and its integration with the Prompt Architect
orchestration pipeline.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lattice_lock.agents.prompt_architect.integrations.project_agent import (
    InteractionLog,
    PendingTask,
    ProjectAgentClient,
    ProjectPhase,
    ProjectScope,
)


class TestProjectAgentClient:
    """Tests for the ProjectAgentClient class."""

    def test_client_initialization(self):
        """Test that the client initializes correctly."""
        client = ProjectAgentClient()
        assert client is not None
        assert client.repo_root is not None

    def test_client_with_custom_paths(self):
        """Test client initialization with custom paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = ProjectAgentClient(
                repo_root=Path(tmpdir),
                agent_definitions_path=f"{tmpdir}/agent_definitions",
                agent_memory_path=f"{tmpdir}/agent_memory",
            )
            assert client.repo_root == Path(tmpdir)

    def test_get_project_scope(self):
        """Test getting project scope."""
        client = ProjectAgentClient()
        scope = client.get_project_scope()

        assert isinstance(scope, ProjectScope)
        assert scope.name is not None
        assert len(scope.name) > 0

    def test_get_current_phase(self):
        """Test getting current phase."""
        client = ProjectAgentClient()
        phase = client.get_current_phase()

        # May return None if no phases found
        if phase is not None:
            assert isinstance(phase, ProjectPhase)
            assert phase.id is not None

    def test_get_pending_tasks(self):
        """Test getting pending tasks."""
        client = ProjectAgentClient()
        tasks = client.get_pending_tasks()

        assert isinstance(tasks, list)
        for task in tasks:
            assert isinstance(task, PendingTask)

    def test_get_pending_tasks_with_phase_filter(self):
        """Test getting pending tasks with phase filter."""
        client = ProjectAgentClient()
        tasks = client.get_pending_tasks(phase="5")

        assert isinstance(tasks, list)
        for task in tasks:
            assert task.phase == "5"

    def test_get_pending_tasks_with_tool_filter(self):
        """Test getting pending tasks with tool filter."""
        client = ProjectAgentClient()
        tasks = client.get_pending_tasks(tool="Devin AI")

        assert isinstance(tasks, list)
        for task in tasks:
            assert task.tool == "Devin AI"

    def test_get_specification_path(self):
        """Test getting specification path."""
        client = ProjectAgentClient()
        spec_path = client.get_specification_path()

        # May return None if not found
        if spec_path is not None:
            assert Path(spec_path).exists()

    def test_get_roadmap_path(self):
        """Test getting roadmap path."""
        client = ProjectAgentClient()
        roadmap_path = client.get_roadmap_path()

        # May return None if not found
        if roadmap_path is not None:
            assert Path(roadmap_path).exists()


class TestInteractionLogging:
    """Tests for agent-to-agent interaction logging."""

    def test_interaction_log_created(self):
        """Test that interactions are logged."""
        client = ProjectAgentClient()

        # Perform some operations that should be logged
        client.get_project_scope()
        client.get_current_phase()
        client.get_pending_tasks()

        log = client.get_interaction_log()
        assert len(log) >= 3

    def test_interaction_log_format(self):
        """Test interaction log entry format."""
        client = ProjectAgentClient()
        client.get_project_scope()

        log = client.get_interaction_log()
        assert len(log) > 0

        entry = log[0]
        assert isinstance(entry, InteractionLog)
        assert entry.source_agent == "prompt_architect_agent"
        assert entry.target_agent == "project_agent"
        assert entry.interaction_type is not None
        assert entry.summary is not None

    def test_export_interactions_to_memory(self):
        """Test exporting interactions to memory file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock memory file
            memory_dir = Path(tmpdir) / "agent_memory" / "agents"
            memory_dir.mkdir(parents=True)
            memory_file = memory_dir / "agent_prompt_architect_memory.md"
            memory_file.write_text(
                """# Agent Memory

## Agent to Agent Interactions

| Date | Agent | Summary |
|------|-------|---------|
| 2024-01-01 | test_agent | Initial interaction |

## Other Section
"""
            )

            client = ProjectAgentClient(
                repo_root=Path(tmpdir),
                agent_memory_path=str(tmpdir) + "/agent_memory",
            )

            # Perform operations
            client.get_project_scope()

            # Export to memory
            client.export_interactions_to_memory(memory_file)

            # Verify content was updated
            content = memory_file.read_text()
            assert "project_agent" in content


class TestProjectScopeDiscovery:
    """Tests for project scope discovery."""

    def test_discover_from_specifications(self):
        """Test discovering scope from specification files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock specification file
            spec_file = Path(tmpdir) / "SPECIFICATION.md"
            spec_file.write_text(
                """# Test Project

## Overview

This is a test project for testing purposes.

## Goals

- Goal 1
- Goal 2
"""
            )

            client = ProjectAgentClient(repo_root=Path(tmpdir))
            scope = client.get_project_scope()

            assert scope.name == "Test Project"


class TestPhaseDiscovery:
    """Tests for phase discovery."""

    def test_discover_phases_from_state(self):
        """Test discovering phases from prompt state file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock state file
            impl_dir = Path(tmpdir) / "implementation" / "project_prompts"
            impl_dir.mkdir(parents=True)
            state_file = impl_dir / "project_prompts_state.json"
            state_file.write_text(
                json.dumps(
                    {
                        "phase_definitions": {
                            "1": "Foundation",
                            "2": "Core Features",
                            "3": "Integration",
                        },
                        "prompts": [],
                    }
                )
            )

            client = ProjectAgentClient(repo_root=Path(tmpdir))
            phase = client.get_current_phase()

            # Should find phases from state
            if phase is not None:
                assert phase.id in ["1", "2", "3"]


class TestPendingTaskDiscovery:
    """Tests for pending task discovery."""

    def test_discover_pending_tasks(self):
        """Test discovering pending tasks from state file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock state file with pending tasks
            impl_dir = Path(tmpdir) / "implementation" / "project_prompts"
            impl_dir.mkdir(parents=True)
            state_file = impl_dir / "project_prompts_state.json"
            state_file.write_text(
                json.dumps(
                    {
                        "phase_definitions": {},
                        "prompts": [
                            {
                                "id": "5.1.1",
                                "title": "Test Task 1",
                                "phase": "5",
                                "epic": "5.1",
                                "tool": "Devin AI",
                                "done": False,
                                "merged": False,
                            },
                            {
                                "id": "5.1.2",
                                "title": "Test Task 2",
                                "phase": "5",
                                "epic": "5.1",
                                "tool": "Gemini",
                                "done": True,
                                "merged": False,
                            },
                        ],
                    }
                )
            )

            client = ProjectAgentClient(repo_root=Path(tmpdir))
            tasks = client.get_pending_tasks()

            # Should only return the pending task (not done)
            assert len(tasks) == 1
            assert tasks[0].id == "5.1.1"
            assert tasks[0].tool == "Devin AI"


@pytest.mark.integration
class TestOrchestratorIntegration:
    """Integration tests for orchestrator with Project Agent."""

    @pytest.mark.asyncio
    async def test_orchestrate_from_project(self):
        """Test orchestration using Project Agent as input source."""
        from lattice_lock.agents.prompt_architect.orchestrator import PromptOrchestrator

        orchestrator = PromptOrchestrator()
        result = await orchestrator.orchestrate_prompt_generation(
            from_project=True,
            dry_run=True,
        )

        # Should complete without errors
        assert result is not None
        assert result.status in ["success", "partial", "failure"]

    @pytest.mark.asyncio
    async def test_orchestrate_discovers_spec_from_project(self):
        """Test that orchestrator discovers spec from Project Agent."""
        from lattice_lock.agents.prompt_architect.orchestrator import PromptOrchestrator

        orchestrator = PromptOrchestrator()

        # The orchestrator should use ProjectAgentClient internally
        # when from_project=True
        result = await orchestrator.orchestrate_prompt_generation(
            from_project=True,
            dry_run=True,
        )

        assert result is not None


class TestTokenUsageTracking:
    """Tests for token usage tracking across agent boundaries."""

    def test_interaction_tracks_tokens(self):
        """Test that interactions track token usage."""
        client = ProjectAgentClient()

        # Perform operations
        client.get_project_scope()

        log = client.get_interaction_log()
        assert len(log) > 0

        # Token usage should be tracked (may be 0 for non-LLM operations)
        entry = log[0]
        assert hasattr(entry, "tokens_used")
        assert isinstance(entry.tokens_used, int)

    def test_interaction_tracks_duration(self):
        """Test that interactions track duration."""
        client = ProjectAgentClient()

        # Perform operations
        client.get_project_scope()

        log = client.get_interaction_log()
        assert len(log) > 0

        entry = log[0]
        assert hasattr(entry, "duration_seconds")
        assert isinstance(entry.duration_seconds, float)
