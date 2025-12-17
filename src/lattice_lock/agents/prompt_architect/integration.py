"""
Integration module for Prompt Architect Agent with Project Agent.

Provides interfaces for the Project Agent to request prompt generation
and track prompt execution status.
"""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lattice_lock.agents.prompt_architect.models import (
    GenerationRequest,
    GenerationResult,
    PromptOutput,
    PromptStatus,
    ToolType,
)
from lattice_lock.agents.prompt_architect.orchestrator import PromptArchitectOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class ProjectContext:
    """Context from the Project Agent for prompt generation."""

    project_id: str
    project_name: str
    current_phase: str
    active_epics: list[str] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)
    blocked_tasks: list[str] = field(default_factory=list)
    team_assignments: dict[str, str] = field(default_factory=dict)
    deadline: datetime | None = None
    priority_override: str | None = None


@dataclass
class PromptExecutionStatus:
    """Status of prompt execution for Project Agent tracking."""

    prompt_id: str
    task_id: str
    tool: ToolType
    status: PromptStatus
    assigned_to: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    output_summary: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class IntegrationConfig:
    """Configuration for the integration."""

    auto_assign: bool = True
    notify_on_completion: bool = True
    track_metrics: bool = True
    max_concurrent_prompts: int = 5
    retry_failed_prompts: bool = True
    max_retries: int = 3


class PromptArchitectIntegration:
    """
    Integration layer between Prompt Architect and Project Agent.

    Provides methods for the Project Agent to:
    - Request prompt generation for phases/epics/tasks
    - Track prompt execution status
    - Receive notifications on prompt completion
    - Query prompt metrics and statistics
    """

    def __init__(
        self,
        orchestrator: PromptArchitectOrchestrator | None = None,
        config: IntegrationConfig | None = None,
        state_file: str = "project_prompts/integration_state.json",
    ) -> None:
        self.orchestrator = orchestrator or PromptArchitectOrchestrator()
        self.config = config or IntegrationConfig()
        self.state_file = Path(state_file)
        self._state: dict[str, Any] = {}
        self._callbacks: dict[str, list[Callable]] = {
            "on_prompt_generated": [],
            "on_prompt_started": [],
            "on_prompt_completed": [],
            "on_prompt_failed": [],
        }

    def load_state(self) -> None:
        """Load integration state from disk."""
        if self.state_file.exists():
            try:
                self._state = json.loads(self.state_file.read_text())
            except json.JSONDecodeError:
                logger.warning("Failed to parse integration state, starting fresh")
                self._state = {}
        else:
            self._state = {}

    def save_state(self) -> None:
        """Save integration state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.state_file.write_text(json.dumps(self._state, indent=2))

    def register_callback(
        self,
        event: str,
        callback: Callable,
    ) -> None:
        """Register a callback for an event."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
        else:
            raise ValueError(f"Unknown event: {event}")

    def _trigger_callbacks(self, event: str, data: Any) -> None:
        """Trigger all callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")

    def request_prompts_for_phase(
        self,
        context: ProjectContext,
        phase: str,
        force_regenerate: bool = False,
    ) -> GenerationResult:
        """
        Request prompt generation for an entire phase.

        Called by Project Agent when starting a new phase.
        """
        self.load_state()

        request = GenerationRequest(
            project_name=context.project_name,
            phase=phase,
            force_regenerate=force_regenerate,
        )

        result = self.orchestrator.generate_prompts(request)

        for prompt in result.generated_prompts:
            self._track_prompt(prompt, context)
            self._trigger_callbacks("on_prompt_generated", prompt)

        self.save_state()
        return result

    def request_prompts_for_epic(
        self,
        context: ProjectContext,
        epic: str,
        force_regenerate: bool = False,
    ) -> GenerationResult:
        """
        Request prompt generation for a specific epic.

        Called by Project Agent when focusing on an epic.
        """
        self.load_state()

        request = GenerationRequest(
            project_name=context.project_name,
            phase=context.current_phase,
            epic=epic,
            force_regenerate=force_regenerate,
        )

        result = self.orchestrator.generate_prompts(request)

        for prompt in result.generated_prompts:
            self._track_prompt(prompt, context)
            self._trigger_callbacks("on_prompt_generated", prompt)

        self.save_state()
        return result

    def request_prompts_for_tasks(
        self,
        context: ProjectContext,
        task_ids: list[str],
        force_regenerate: bool = False,
    ) -> GenerationResult:
        """
        Request prompt generation for specific tasks.

        Called by Project Agent for targeted prompt generation.
        """
        self.load_state()

        request = GenerationRequest(
            project_name=context.project_name,
            phase=context.current_phase,
            task_ids=task_ids,
            force_regenerate=force_regenerate,
        )

        result = self.orchestrator.generate_prompts(request)

        for prompt in result.generated_prompts:
            self._track_prompt(prompt, context)
            self._trigger_callbacks("on_prompt_generated", prompt)

        self.save_state()
        return result

    def _track_prompt(
        self,
        prompt: PromptOutput,
        context: ProjectContext,
    ) -> None:
        """Track a generated prompt in the integration state."""
        if "prompts" not in self._state:
            self._state["prompts"] = {}

        self._state["prompts"][prompt.prompt_id] = {
            "task_id": prompt.task_id,
            "tool": prompt.tool.value,
            "status": prompt.status.value,
            "file_path": prompt.file_path,
            "project_id": context.project_id,
            "phase": context.current_phase,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "assigned_to": context.team_assignments.get(prompt.task_id),
        }

    def mark_prompt_started(
        self,
        prompt_id: str,
        assigned_to: str | None = None,
    ) -> bool:
        """
        Mark a prompt as started (in progress).

        Called by Project Agent when a tool begins executing a prompt.
        """
        self.load_state()

        if "prompts" not in self._state:
            return False

        if prompt_id not in self._state["prompts"]:
            return False

        self._state["prompts"][prompt_id]["status"] = PromptStatus.IN_PROGRESS.value
        self._state["prompts"][prompt_id]["started_at"] = datetime.now(timezone.utc).isoformat()
        if assigned_to:
            self._state["prompts"][prompt_id]["assigned_to"] = assigned_to

        self.save_state()

        status = self._get_execution_status(prompt_id)
        self._trigger_callbacks("on_prompt_started", status)

        return True

    def mark_prompt_completed(
        self,
        prompt_id: str,
        output_summary: str = "",
    ) -> bool:
        """
        Mark a prompt as completed.

        Called by Project Agent when a tool finishes executing a prompt.
        """
        self.load_state()

        if "prompts" not in self._state:
            return False

        if prompt_id not in self._state["prompts"]:
            return False

        self._state["prompts"][prompt_id]["status"] = PromptStatus.COMPLETED.value
        self._state["prompts"][prompt_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._state["prompts"][prompt_id]["output_summary"] = output_summary

        self.save_state()

        status = self._get_execution_status(prompt_id)
        self._trigger_callbacks("on_prompt_completed", status)

        return True

    def mark_prompt_failed(
        self,
        prompt_id: str,
        error: str,
    ) -> bool:
        """
        Mark a prompt as failed.

        Called by Project Agent when a tool fails to execute a prompt.
        """
        self.load_state()

        if "prompts" not in self._state:
            return False

        if prompt_id not in self._state["prompts"]:
            return False

        prompt_state = self._state["prompts"][prompt_id]
        prompt_state["status"] = PromptStatus.FAILED.value
        prompt_state["completed_at"] = datetime.now(timezone.utc).isoformat()

        if "errors" not in prompt_state:
            prompt_state["errors"] = []
        prompt_state["errors"].append(error)

        self.save_state()

        status = self._get_execution_status(prompt_id)
        self._trigger_callbacks("on_prompt_failed", status)

        return True

    def mark_prompt_blocked(
        self,
        prompt_id: str,
        reason: str,
    ) -> bool:
        """
        Mark a prompt as blocked.

        Called by Project Agent when a prompt cannot proceed.
        """
        self.load_state()

        if "prompts" not in self._state:
            return False

        if prompt_id not in self._state["prompts"]:
            return False

        self._state["prompts"][prompt_id]["status"] = PromptStatus.BLOCKED.value
        self._state["prompts"][prompt_id]["blocked_reason"] = reason

        self.save_state()
        return True

    def _get_execution_status(self, prompt_id: str) -> PromptExecutionStatus | None:
        """Get the execution status for a prompt."""
        if "prompts" not in self._state:
            return None

        if prompt_id not in self._state["prompts"]:
            return None

        prompt_data = self._state["prompts"][prompt_id]

        return PromptExecutionStatus(
            prompt_id=prompt_id,
            task_id=prompt_data.get("task_id", ""),
            tool=ToolType(prompt_data.get("tool", "devin")),
            status=PromptStatus(prompt_data.get("status", "draft")),
            assigned_to=prompt_data.get("assigned_to"),
            started_at=(
                datetime.fromisoformat(prompt_data["started_at"])
                if prompt_data.get("started_at")
                else None
            ),
            completed_at=(
                datetime.fromisoformat(prompt_data["completed_at"])
                if prompt_data.get("completed_at")
                else None
            ),
            output_summary=prompt_data.get("output_summary", ""),
            errors=prompt_data.get("errors", []),
        )

    def get_prompt_status(self, prompt_id: str) -> PromptExecutionStatus | None:
        """
        Get the current status of a prompt.

        Called by Project Agent to check on prompt progress.
        """
        self.load_state()
        return self._get_execution_status(prompt_id)

    def get_phase_status(self, phase: str) -> dict[str, Any]:
        """
        Get the status of all prompts in a phase.

        Called by Project Agent for phase-level reporting.
        """
        self.load_state()

        status = {
            "phase": phase,
            "total": 0,
            "draft": 0,
            "ready": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "blocked": 0,
            "prompts": [],
        }

        for prompt_id, prompt_data in self._state.get("prompts", {}).items():
            if prompt_data.get("phase") == phase:
                status["total"] += 1
                prompt_status = prompt_data.get("status", "draft")
                if prompt_status in status:
                    status[prompt_status] += 1
                status["prompts"].append(
                    {
                        "prompt_id": prompt_id,
                        "task_id": prompt_data.get("task_id"),
                        "status": prompt_status,
                    }
                )

        return status

    def get_metrics(self) -> dict[str, Any]:
        """
        Get metrics for prompt generation and execution.

        Called by Project Agent for reporting and analytics.
        """
        self.load_state()

        metrics = {
            "total_prompts": 0,
            "by_status": {},
            "by_tool": {},
            "completion_rate": 0.0,
            "average_execution_time": 0.0,
        }

        prompts = self._state.get("prompts", {})
        metrics["total_prompts"] = len(prompts)

        execution_times = []

        for prompt_data in prompts.values():
            status = prompt_data.get("status", "draft")
            tool = prompt_data.get("tool", "unknown")

            metrics["by_status"][status] = metrics["by_status"].get(status, 0) + 1
            metrics["by_tool"][tool] = metrics["by_tool"].get(tool, 0) + 1

            if prompt_data.get("started_at") and prompt_data.get("completed_at"):
                started = datetime.fromisoformat(prompt_data["started_at"])
                completed = datetime.fromisoformat(prompt_data["completed_at"])
                execution_times.append((completed - started).total_seconds())

        if metrics["total_prompts"] > 0:
            completed = metrics["by_status"].get("completed", 0)
            metrics["completion_rate"] = completed / metrics["total_prompts"]

        if execution_times:
            metrics["average_execution_time"] = sum(execution_times) / len(execution_times)

        return metrics

    def get_pending_prompts(
        self,
        tool: ToolType | None = None,
    ) -> list[PromptExecutionStatus]:
        """
        Get all pending prompts, optionally filtered by tool.

        Called by Project Agent to find work for tools.
        """
        self.load_state()

        pending = []

        for prompt_id, prompt_data in self._state.get("prompts", {}).items():
            if prompt_data.get("status") == PromptStatus.READY.value:
                if tool is None or prompt_data.get("tool") == tool.value:
                    status = self._get_execution_status(prompt_id)
                    if status:
                        pending.append(status)

        return pending

    def retry_failed_prompts(self) -> list[str]:
        """
        Retry all failed prompts.

        Called by Project Agent to recover from failures.
        """
        self.load_state()

        retried = []

        for prompt_id, prompt_data in self._state.get("prompts", {}).items():
            if prompt_data.get("status") == PromptStatus.FAILED.value:
                retry_count = prompt_data.get("retry_count", 0)
                if retry_count < self.config.max_retries:
                    prompt_data["status"] = PromptStatus.READY.value
                    prompt_data["retry_count"] = retry_count + 1
                    del prompt_data["completed_at"]
                    retried.append(prompt_id)

        if retried:
            self.save_state()

        return retried


class ProjectAgentInterface:
    """
    Interface for Project Agent to interact with Prompt Architect.

    Provides a simplified API for common operations.
    """

    def __init__(
        self,
        integration: PromptArchitectIntegration | None = None,
    ) -> None:
        self.integration = integration or PromptArchitectIntegration()

    def start_phase(
        self,
        project_id: str,
        project_name: str,
        phase: str,
    ) -> GenerationResult:
        """Start a new phase and generate all prompts for it."""
        context = ProjectContext(
            project_id=project_id,
            project_name=project_name,
            current_phase=phase,
        )
        return self.integration.request_prompts_for_phase(context, phase)

    def get_next_task(self, tool: ToolType) -> PromptExecutionStatus | None:
        """Get the next pending task for a specific tool."""
        pending = self.integration.get_pending_prompts(tool)
        return pending[0] if pending else None

    def complete_task(self, prompt_id: str, summary: str) -> bool:
        """Mark a task as completed."""
        return self.integration.mark_prompt_completed(prompt_id, summary)

    def fail_task(self, prompt_id: str, error: str) -> bool:
        """Mark a task as failed."""
        return self.integration.mark_prompt_failed(prompt_id, error)

    def get_progress(self, phase: str) -> dict[str, Any]:
        """Get progress for a phase."""
        return self.integration.get_phase_status(phase)


__all__ = [
    "ProjectContext",
    "PromptExecutionStatus",
    "IntegrationConfig",
    "PromptArchitectIntegration",
    "ProjectAgentInterface",
]
