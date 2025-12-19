"""
Tests for the Prompt Architect Agent integration with Project Agent.

Tests the integration layer, callbacks, and Project Agent interface.
"""

import tempfile
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from lattice_lock.agents.prompt_architect.integration import (
    IntegrationConfig,
    ProjectAgentInterface,
    ProjectContext,
    PromptArchitectIntegration,
    PromptExecutionStatus,
)
from lattice_lock.agents.prompt_architect.models import GenerationResult, PromptStatus, ToolType


class TestProjectContext:
    """Tests for ProjectContext dataclass."""

    def test_create_context(self) -> None:
        """Test creating a project context."""
        context = ProjectContext(
            project_id="proj_001",
            project_name="Test Project",
            current_phase="phase_1",
            active_epics=["epic_1.1", "epic_1.2"],
            completed_tasks=["task_1.1.1"],
        )
        assert context.project_id == "proj_001"
        assert context.project_name == "Test Project"
        assert len(context.active_epics) == 2
        assert len(context.completed_tasks) == 1

    def test_context_with_deadline(self) -> None:
        """Test context with deadline."""
        deadline = datetime(2025, 12, 31)
        context = ProjectContext(
            project_id="proj_001",
            project_name="Test",
            current_phase="phase_1",
            deadline=deadline,
        )
        assert context.deadline == deadline


class TestPromptExecutionStatus:
    """Tests for PromptExecutionStatus dataclass."""

    def test_create_status(self) -> None:
        """Test creating an execution status."""
        status = PromptExecutionStatus(
            prompt_id="prompt_001",
            task_id="task_1.1.1",
            tool=ToolType.DEVIN,
            status=PromptStatus.IN_PROGRESS,
            assigned_to="devin_instance_1",
        )
        assert status.prompt_id == "prompt_001"
        assert status.tool == ToolType.DEVIN
        assert status.status == PromptStatus.IN_PROGRESS

    def test_status_with_times(self) -> None:
        """Test status with start and completion times."""
        now = datetime.now(timezone.utc)
        status = PromptExecutionStatus(
            prompt_id="prompt_001",
            task_id="task_1",
            tool=ToolType.DEVIN,
            status=PromptStatus.COMPLETED,
            started_at=now,
            completed_at=now,
        )
        assert status.started_at is not None
        assert status.completed_at is not None


class TestIntegrationConfig:
    """Tests for IntegrationConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = IntegrationConfig()
        assert config.auto_assign is True
        assert config.notify_on_completion is True
        assert config.max_concurrent_prompts == 5
        assert config.max_retries == 3

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = IntegrationConfig(
            auto_assign=False,
            max_concurrent_prompts=10,
            max_retries=5,
        )
        assert config.auto_assign is False
        assert config.max_concurrent_prompts == 10
        assert config.max_retries == 5


class TestPromptArchitectIntegration:
    """Tests for PromptArchitectIntegration."""

    def test_load_save_state(self) -> None:
        """Test loading and saving state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration.load_state()
            assert integration._state == {}

            integration._state["test"] = "value"
            integration.save_state()

            integration2 = PromptArchitectIntegration(state_file=state_file)
            integration2.load_state()
            assert integration2._state["test"] == "value"

    def test_register_callback(self) -> None:
        """Test registering callbacks."""
        integration = PromptArchitectIntegration()
        callback = MagicMock()

        integration.register_callback("on_prompt_generated", callback)
        assert callback in integration._callbacks["on_prompt_generated"]

    def test_register_invalid_callback(self) -> None:
        """Test registering callback for invalid event."""
        integration = PromptArchitectIntegration()
        callback = MagicMock()

        with pytest.raises(ValueError):
            integration.register_callback("invalid_event", callback)

    def test_mark_prompt_started(self) -> None:
        """Test marking a prompt as started."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "ready",
                    }
                }
            }
            integration.save_state()

            result = integration.mark_prompt_started("prompt_001", "devin_1")
            assert result is True

            integration.load_state()
            assert integration._state["prompts"]["prompt_001"]["status"] == "in_progress"
            assert integration._state["prompts"]["prompt_001"]["assigned_to"] == "devin_1"

    def test_mark_prompt_started_not_found(self) -> None:
        """Test marking a nonexistent prompt as started."""
        integration = PromptArchitectIntegration()
        integration._state = {"prompts": {}}

        result = integration.mark_prompt_started("nonexistent")
        assert result is False

    def test_mark_prompt_completed(self) -> None:
        """Test marking a prompt as completed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "in_progress",
                    }
                }
            }
            integration.save_state()

            result = integration.mark_prompt_completed("prompt_001", "Task completed successfully")
            assert result is True

            integration.load_state()
            assert integration._state["prompts"]["prompt_001"]["status"] == "completed"
            assert (
                integration._state["prompts"]["prompt_001"]["output_summary"]
                == "Task completed successfully"
            )

    def test_mark_prompt_failed(self) -> None:
        """Test marking a prompt as failed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "in_progress",
                    }
                }
            }
            integration.save_state()

            result = integration.mark_prompt_failed("prompt_001", "Connection timeout")
            assert result is True

            integration.load_state()
            assert integration._state["prompts"]["prompt_001"]["status"] == "failed"
            assert "Connection timeout" in integration._state["prompts"]["prompt_001"]["errors"]

    def test_mark_prompt_blocked(self) -> None:
        """Test marking a prompt as blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "ready",
                    }
                }
            }
            integration.save_state()

            result = integration.mark_prompt_blocked("prompt_001", "Waiting for dependency")
            assert result is True

            integration.load_state()
            assert integration._state["prompts"]["prompt_001"]["status"] == "blocked"
            assert (
                integration._state["prompts"]["prompt_001"]["blocked_reason"]
                == "Waiting for dependency"
            )

    def test_get_prompt_status(self) -> None:
        """Test getting prompt status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "in_progress",
                        "assigned_to": "devin_1",
                    }
                }
            }
            integration.save_state()

            status = integration.get_prompt_status("prompt_001")
            assert status is not None
            assert status.prompt_id == "prompt_001"
            assert status.tool == ToolType.DEVIN
            assert status.status == PromptStatus.IN_PROGRESS

    def test_get_prompt_status_not_found(self) -> None:
        """Test getting status for nonexistent prompt."""
        integration = PromptArchitectIntegration()
        integration._state = {"prompts": {}}

        status = integration.get_prompt_status("nonexistent")
        assert status is None

    def test_get_phase_status(self) -> None:
        """Test getting phase status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "completed",
                        "phase": "phase_1",
                    },
                    "prompt_002": {
                        "task_id": "task_2",
                        "tool": "gemini_cli",
                        "status": "in_progress",
                        "phase": "phase_1",
                    },
                    "prompt_003": {
                        "task_id": "task_3",
                        "tool": "devin",
                        "status": "ready",
                        "phase": "phase_2",
                    },
                }
            }
            integration.save_state()

            status = integration.get_phase_status("phase_1")
            assert status["phase"] == "phase_1"
            assert status["total"] == 2
            assert status["completed"] == 1
            assert status["in_progress"] == 1

    def test_get_metrics(self) -> None:
        """Test getting metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "completed",
                    },
                    "prompt_002": {
                        "task_id": "task_2",
                        "tool": "devin",
                        "status": "completed",
                    },
                    "prompt_003": {
                        "task_id": "task_3",
                        "tool": "gemini_cli",
                        "status": "in_progress",
                    },
                }
            }
            integration.save_state()

            metrics = integration.get_metrics()
            assert metrics["total_prompts"] == 3
            assert metrics["by_status"]["completed"] == 2
            assert metrics["by_status"]["in_progress"] == 1
            assert metrics["by_tool"]["devin"] == 2
            assert metrics["by_tool"]["gemini_cli"] == 1

    def test_get_pending_prompts(self) -> None:
        """Test getting pending prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "ready",
                    },
                    "prompt_002": {
                        "task_id": "task_2",
                        "tool": "gemini_cli",
                        "status": "ready",
                    },
                    "prompt_003": {
                        "task_id": "task_3",
                        "tool": "devin",
                        "status": "completed",
                    },
                }
            }
            integration.save_state()

            all_pending = integration.get_pending_prompts()
            assert len(all_pending) == 2

            devin_pending = integration.get_pending_prompts(ToolType.DEVIN)
            assert len(devin_pending) == 1
            assert devin_pending[0].tool == ToolType.DEVIN

    def test_retry_failed_prompts(self) -> None:
        """Test retrying failed prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "failed",
                        "completed_at": "2025-01-01T00:00:00",
                        "retry_count": 0,
                    },
                    "prompt_002": {
                        "task_id": "task_2",
                        "tool": "devin",
                        "status": "failed",
                        "completed_at": "2025-01-01T00:00:00",
                        "retry_count": 3,
                    },
                }
            }
            integration.save_state()

            retried = integration.retry_failed_prompts()
            assert len(retried) == 1
            assert "prompt_001" in retried

            integration.load_state()
            assert integration._state["prompts"]["prompt_001"]["status"] == "ready"
            assert integration._state["prompts"]["prompt_001"]["retry_count"] == 1
            assert integration._state["prompts"]["prompt_002"]["status"] == "failed"

    def test_callback_triggered_on_completion(self) -> None:
        """Test that callbacks are triggered on prompt completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            integration = PromptArchitectIntegration(state_file=state_file)

            callback = MagicMock()
            integration.register_callback("on_prompt_completed", callback)

            integration._state = {
                "prompts": {
                    "prompt_001": {
                        "task_id": "task_1",
                        "tool": "devin",
                        "status": "in_progress",
                    }
                }
            }
            integration.save_state()

            integration.mark_prompt_completed("prompt_001", "Done")
            callback.assert_called_once()


class TestProjectAgentInterface:
    """Tests for ProjectAgentInterface."""

    def test_start_phase(self) -> None:
        """Test starting a phase."""
        mock_integration = MagicMock()
        mock_integration.request_prompts_for_phase.return_value = GenerationResult(
            success=True,
            prompts_generated=5,
            prompts_updated=0,
            prompts_skipped=0,
        )

        interface = ProjectAgentInterface(integration=mock_integration)
        result = interface.start_phase("proj_001", "Test Project", "phase_1")

        assert result.success
        assert result.prompts_generated == 5
        mock_integration.request_prompts_for_phase.assert_called_once()

    def test_get_next_task(self) -> None:
        """Test getting next task for a tool."""
        mock_integration = MagicMock()
        mock_status = PromptExecutionStatus(
            prompt_id="prompt_001",
            task_id="task_1",
            tool=ToolType.DEVIN,
            status=PromptStatus.READY,
        )
        mock_integration.get_pending_prompts.return_value = [mock_status]

        interface = ProjectAgentInterface(integration=mock_integration)
        task = interface.get_next_task(ToolType.DEVIN)

        assert task is not None
        assert task.prompt_id == "prompt_001"

    def test_get_next_task_none_available(self) -> None:
        """Test getting next task when none available."""
        mock_integration = MagicMock()
        mock_integration.get_pending_prompts.return_value = []

        interface = ProjectAgentInterface(integration=mock_integration)
        task = interface.get_next_task(ToolType.DEVIN)

        assert task is None

    def test_complete_task(self) -> None:
        """Test completing a task."""
        mock_integration = MagicMock()
        mock_integration.mark_prompt_completed.return_value = True

        interface = ProjectAgentInterface(integration=mock_integration)
        result = interface.complete_task("prompt_001", "Task completed")

        assert result is True
        mock_integration.mark_prompt_completed.assert_called_once_with(
            "prompt_001", "Task completed"
        )

    def test_fail_task(self) -> None:
        """Test failing a task."""
        mock_integration = MagicMock()
        mock_integration.mark_prompt_failed.return_value = True

        interface = ProjectAgentInterface(integration=mock_integration)
        result = interface.fail_task("prompt_001", "Error occurred")

        assert result is True
        mock_integration.mark_prompt_failed.assert_called_once_with("prompt_001", "Error occurred")

    def test_get_progress(self) -> None:
        """Test getting progress for a phase."""
        mock_integration = MagicMock()
        mock_integration.get_phase_status.return_value = {
            "phase": "phase_1",
            "total": 10,
            "completed": 5,
        }

        interface = ProjectAgentInterface(integration=mock_integration)
        progress = interface.get_progress("phase_1")

        assert progress["total"] == 10
        assert progress["completed"] == 5
