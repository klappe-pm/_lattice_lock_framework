"""
ProjectAgentClient - Integration with the Project Agent.

This module provides a client for querying project state from the Project Agent,
enabling the Prompt Architect to automatically discover specifications and roadmaps.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ProjectScope:
    """Represents the scope of a project."""

    name: str
    description: str
    goals: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    stakeholders: list[str] = field(default_factory=list)
    timeline: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectPhase:
    """Represents a phase in the project."""

    id: str
    name: str
    description: str
    status: str = "pending"  # pending, in_progress, completed
    start_date: str | None = None
    end_date: str | None = None
    deliverables: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class PendingTask:
    """Represents a pending task from the project."""

    id: str
    title: str
    description: str
    phase: str
    epic: str
    tool: str | None = None
    priority: str = "medium"
    files: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"


@dataclass
class InteractionLog:
    """Log entry for agent-to-agent interactions."""

    timestamp: datetime
    source_agent: str
    target_agent: str
    interaction_type: str
    summary: str
    tokens_used: int = 0
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ProjectAgentClient:
    """
    Client for interacting with the Project Agent.

    Provides methods to query project state, including scope, current phase,
    and pending tasks. Also handles agent-to-agent interaction logging.
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        agent_definitions_path: str | None = None,
        agent_memory_path: str | None = None,
    ):
        """
        Initialize the ProjectAgentClient.

        Args:
            repo_root: Root directory of the repository.
            agent_definitions_path: Path to agent definitions directory.
            agent_memory_path: Path to agent memory directory.
        """
        if repo_root is None:
            # Auto-detect repo root
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "agent_definitions").exists():
                    repo_root = parent
                    break
            if repo_root is None:
                repo_root = Path.cwd()

        self.repo_root = repo_root
        self.agent_definitions_path = Path(
            agent_definitions_path or repo_root / "agent_definitions"
        )
        self.agent_memory_path = Path(agent_memory_path or repo_root / "agent_memory")

        # Load Project Agent definition
        self.project_agent_def = self._load_project_agent_definition()

        # Interaction log
        self._interaction_log: list[InteractionLog] = []

    def _load_project_agent_definition(self) -> dict[str, Any]:
        """Load the Project Agent YAML definition."""
        def_path = self.agent_definitions_path / "project_agent" / "project_agent.yaml"
        if not def_path.exists():
            logger.warning(f"Project Agent definition not found at {def_path}")
            return {}

        with open(def_path) as f:
            return yaml.safe_load(f) or {}

    def get_project_scope(self) -> ProjectScope:
        """
        Get the current project scope.

        Returns:
            ProjectScope with project information.
        """
        self._log_interaction("get_project_scope", "Querying project scope")

        # Try to find project scope from various sources
        scope_data = self._discover_project_scope()

        return ProjectScope(
            name=scope_data.get("name", "Lattice Lock Framework"),
            description=scope_data.get("description", ""),
            goals=scope_data.get("goals", []),
            constraints=scope_data.get("constraints", []),
            stakeholders=scope_data.get("stakeholders", []),
            timeline=scope_data.get("timeline"),
            metadata=scope_data.get("metadata", {}),
        )

    def _discover_project_scope(self) -> dict[str, Any]:
        """Discover project scope from available sources."""
        scope_data: dict[str, Any] = {}

        # Try to read from project memory
        project_memory_path = self.agent_memory_path / "projects"
        if project_memory_path.exists():
            for memory_file in project_memory_path.glob("*.md"):
                content = memory_file.read_text()
                # Parse basic info from memory file
                if "## Project Scope" in content or "## Project Goals" in content:
                    scope_data["name"] = memory_file.stem
                    scope_data["description"] = self._extract_section(content, "Project Scope")
                    goals_text = self._extract_section(content, "Project Goals")
                    if goals_text:
                        scope_data["goals"] = [
                            line.strip("- ").strip()
                            for line in goals_text.split("\n")
                            if line.strip().startswith("-")
                        ]
                    break

        # Try to read from specifications
        spec_paths = [
            self.repo_root / "specifications" / "lattice_lock_framework_specifications.md",
            self.repo_root / "SPECIFICATION.md",
        ]
        for spec_path in spec_paths:
            if spec_path.exists():
                content = spec_path.read_text()
                if not scope_data.get("name"):
                    # Extract project name from first heading
                    for line in content.split("\n"):
                        if line.startswith("# "):
                            scope_data["name"] = line[2:].strip()
                            break
                if not scope_data.get("description"):
                    scope_data["description"] = self._extract_section(content, "Overview")
                break

        # Default values if nothing found
        if not scope_data.get("name"):
            scope_data["name"] = "Lattice Lock Framework"
        if not scope_data.get("description"):
            scope_data[
                "description"
            ] = "Governance-first framework for AI-assisted software development"

        return scope_data

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a section from markdown content."""
        lines = content.split("\n")
        in_section = False
        section_lines = []

        for line in lines:
            if line.startswith("## ") or line.startswith("# "):
                if section_name.lower() in line.lower():
                    in_section = True
                    continue
                elif in_section:
                    break
            elif in_section:
                section_lines.append(line)

        return "\n".join(section_lines).strip()

    def get_current_phase(self) -> ProjectPhase | None:
        """
        Get the current active phase of the project.

        Returns:
            ProjectPhase for the current phase, or None if not determinable.
        """
        self._log_interaction("get_current_phase", "Querying current project phase")

        phases = self._discover_phases()
        for phase in phases:
            if phase.status == "in_progress":
                return phase

        # If no phase is in progress, return the first pending phase
        for phase in phases:
            if phase.status == "pending":
                return phase

        return phases[0] if phases else None

    def _discover_phases(self) -> list[ProjectPhase]:
        """Discover project phases from available sources."""
        phases: list[ProjectPhase] = []

        # Try to read from work breakdown structure
        wbs_paths = [
            self.repo_root / "docs" / "development" / "lattice_lock_work_breakdown_v2_1.md",
            self.repo_root / "project_prompts" / "work_breakdown_structure.md",
        ]

        for wbs_path in wbs_paths:
            if wbs_path.exists():
                content = wbs_path.read_text()
                phases = self._parse_phases_from_wbs(content)
                if phases:
                    break

        # Try to read from prompt tracker state
        if not phases:
            state_path = (
                self.repo_root / "implementation" / "project_prompts" / "project_prompts_state.json"
            )
            if state_path.exists():
                import json

                with open(state_path) as f:
                    state = json.load(f)
                phase_defs = state.get("phase_definitions", {})
                for phase_id, phase_name in phase_defs.items():
                    phases.append(
                        ProjectPhase(
                            id=phase_id,
                            name=phase_name,
                            description=f"Phase {phase_id}: {phase_name}",
                            status="pending",
                        )
                    )

        return phases

    def _parse_phases_from_wbs(self, content: str) -> list[ProjectPhase]:
        """Parse phases from Work Breakdown Structure content."""
        phases: list[ProjectPhase] = []
        lines = content.split("\n")

        current_phase = None
        for line in lines:
            # Look for phase headers (e.g., "## Phase 1: Foundation")
            if line.startswith("## Phase ") or line.startswith("### Phase "):
                if current_phase:
                    phases.append(current_phase)

                # Parse phase info
                parts = line.lstrip("#").strip().split(":", 1)
                phase_id = parts[0].replace("Phase ", "").strip()
                phase_name = parts[1].strip() if len(parts) > 1 else f"Phase {phase_id}"

                current_phase = ProjectPhase(
                    id=phase_id,
                    name=phase_name,
                    description="",
                    status="pending",
                )
            elif current_phase and line.strip() and not line.startswith("#"):
                # Add to description
                if not current_phase.description:
                    current_phase.description = line.strip()

        if current_phase:
            phases.append(current_phase)

        return phases

    def get_pending_tasks(
        self,
        phase: str | None = None,
        tool: str | None = None,
    ) -> list[PendingTask]:
        """
        Get pending tasks from the project.

        Args:
            phase: Filter by phase ID.
            tool: Filter by assigned tool.

        Returns:
            List of PendingTask objects.
        """
        self._log_interaction(
            "get_pending_tasks", f"Querying pending tasks (phase={phase}, tool={tool})"
        )

        tasks: list[PendingTask] = []

        # Read from prompt tracker state
        state_path = (
            self.repo_root / "implementation" / "project_prompts" / "project_prompts_state.json"
        )
        if state_path.exists():
            import json

            with open(state_path) as f:
                state = json.load(f)

            for prompt in state.get("prompts", []):
                # Skip if already done or merged
                if prompt.get("done") or prompt.get("merged"):
                    continue

                # Apply filters
                if phase and prompt.get("phase") != phase:
                    continue
                if tool and prompt.get("tool") != tool:
                    continue

                tasks.append(
                    PendingTask(
                        id=prompt.get("id", ""),
                        title=prompt.get("title", ""),
                        description=prompt.get("title", ""),  # Use title as description
                        phase=prompt.get("phase", ""),
                        epic=prompt.get("epic", ""),
                        tool=prompt.get("tool"),
                        priority="medium",
                        status="pending" if not prompt.get("picked_up") else "in_progress",
                    )
                )

        return tasks

    def get_specification_path(self) -> str | None:
        """
        Get the path to the project specification file.

        Returns:
            Path to specification file, or None if not found.
        """
        self._log_interaction("get_specification_path", "Discovering specification path")

        spec_paths = [
            self.repo_root / "specifications" / "lattice_lock_framework_specifications.md",
            self.repo_root / "SPECIFICATION.md",
            self.repo_root / "spec.md",
        ]

        for path in spec_paths:
            if path.exists():
                logger.info(f"Found specification at {path}")
                return str(path)

        return None

    def get_roadmap_path(self) -> str | None:
        """
        Get the path to the project roadmap/WBS file.

        Returns:
            Path to roadmap file, or None if not found.
        """
        self._log_interaction("get_roadmap_path", "Discovering roadmap path")

        roadmap_paths = [
            self.repo_root / "docs" / "development" / "lattice_lock_work_breakdown_v2_1.md",
            self.repo_root / "project_prompts" / "work_breakdown_structure.md",
            self.repo_root / "ROADMAP.md",
        ]

        for path in roadmap_paths:
            if path.exists():
                logger.info(f"Found roadmap at {path}")
                return str(path)

        return None

    def _log_interaction(
        self,
        interaction_type: str,
        summary: str,
        tokens_used: int = 0,
        duration_seconds: float = 0.0,
    ) -> None:
        """Log an agent-to-agent interaction."""
        log_entry = InteractionLog(
            timestamp=datetime.now(),
            source_agent="prompt_architect_agent",
            target_agent="project_agent",
            interaction_type=interaction_type,
            summary=summary,
            tokens_used=tokens_used,
            duration_seconds=duration_seconds,
        )
        self._interaction_log.append(log_entry)
        logger.debug(f"Interaction logged: {interaction_type} - {summary}")

    def get_interaction_log(self) -> list[InteractionLog]:
        """Get the interaction log."""
        return self._interaction_log.copy()

    def export_interactions_to_memory(self, memory_file_path: Path | None = None) -> None:
        """
        Export interactions to the agent memory file.

        Args:
            memory_file_path: Path to the memory file. If None, uses default.
        """
        if memory_file_path is None:
            memory_file_path = (
                self.agent_memory_path / "agents" / "agent_prompt_architect_memory.md"
            )

        if not memory_file_path.exists():
            logger.warning(f"Memory file not found at {memory_file_path}")
            return

        # Read existing content
        content = memory_file_path.read_text()

        # Find the interaction table section
        interaction_section = "## Agent to Agent Interactions"
        if interaction_section not in content:
            logger.warning("Interaction section not found in memory file")
            return

        # Build new interaction rows
        new_rows = []
        for log in self._interaction_log:
            date_str = log.timestamp.strftime("%Y-%m-%d")
            new_rows.append(f"| {date_str} | {log.target_agent} | {log.summary} |")

        if new_rows:
            # Append to the interaction table
            # Find the table and append rows
            lines = content.split("\n")
            new_lines = []
            in_table = False
            table_ended = False

            for line in lines:
                new_lines.append(line)
                if interaction_section in line:
                    in_table = True
                elif in_table and line.startswith("|") and "---" in line:
                    # This is the header separator, add rows after next data row
                    pass
                elif in_table and not line.startswith("|") and line.strip():
                    # End of table
                    if not table_ended:
                        for row in new_rows:
                            new_lines.insert(-1, row)
                        table_ended = True
                    in_table = False

            # Write updated content
            memory_file_path.write_text("\n".join(new_lines))
            logger.info(f"Exported {len(new_rows)} interactions to {memory_file_path}")


__all__ = [
    "ProjectAgentClient",
    "ProjectScope",
    "ProjectPhase",
    "PendingTask",
    "InteractionLog",
]
