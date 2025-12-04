"""
Prompt Architect Agent Orchestrator

Coordinates the generation of LLM prompts from project specifications.
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from lattice_lock.agents.prompt_architect.models import (
    ToolType,
    PromptStatus,
    TaskPriority,
    FileOwnership,
    ToolCapability,
    TaskAssignment,
    PromptContext,
    PromptTemplate,
    PromptOutput,
    GenerationRequest,
    GenerationResult,
    PhaseSpec,
    EpicSpec,
    TaskSpec,
)

logger = logging.getLogger(__name__)


DEFAULT_TOOL_CAPABILITIES = [
    ToolCapability(
        tool=ToolType.DEVIN,
        name="Devin AI",
        description="Autonomous AI software engineer",
        strengths=[
            "Full-stack development",
            "Complex multi-file changes",
            "CI/CD integration",
            "Long-running tasks",
        ],
        limitations=[
            "May be slower for simple tasks",
            "Higher cost for small changes",
        ],
        file_ownership=[
            FileOwnership(
                tool=ToolType.DEVIN,
                paths=[],
                patterns=["src/lattice_lock/agents/*", "pilot_projects/*"],
                description="Agent implementations and pilot projects",
            ),
        ],
        max_context_tokens=200000,
        supports_code_execution=True,
        supports_file_editing=True,
        supports_web_browsing=True,
    ),
    ToolCapability(
        tool=ToolType.GEMINI_CLI,
        name="Gemini CLI",
        description="Google's Gemini model via CLI",
        strengths=[
            "Fast response times",
            "Good at code analysis",
            "Schema validation",
        ],
        limitations=[
            "Limited file editing",
            "No persistent state",
        ],
        file_ownership=[
            FileOwnership(
                tool=ToolType.GEMINI_CLI,
                paths=[],
                patterns=["src/lattice_lock_validator/*"],
                description="Validator implementations",
            ),
        ],
        max_context_tokens=100000,
        supports_code_execution=False,
        supports_file_editing=True,
        supports_web_browsing=False,
    ),
    ToolCapability(
        tool=ToolType.CLAUDE_CLI,
        name="Claude CLI",
        description="Anthropic's Claude via CLI",
        strengths=[
            "Excellent reasoning",
            "Code generation",
            "Documentation",
        ],
        limitations=[
            "Rate limits",
            "Context window constraints",
        ],
        file_ownership=[
            FileOwnership(
                tool=ToolType.CLAUDE_CLI,
                paths=[],
                patterns=["src/lattice_lock_cli/*"],
                description="CLI implementations",
            ),
        ],
        max_context_tokens=200000,
        supports_code_execution=False,
        supports_file_editing=True,
        supports_web_browsing=False,
    ),
    ToolCapability(
        tool=ToolType.CODEX_CLI,
        name="Codex CLI",
        description="OpenAI Codex via CLI",
        strengths=[
            "Code completion",
            "Quick edits",
            "Test generation",
        ],
        limitations=[
            "Limited reasoning",
            "Smaller context",
        ],
        file_ownership=[
            FileOwnership(
                tool=ToolType.CODEX_CLI,
                paths=[".pre-commit-config.yaml"],
                patterns=["src/lattice_lock_validator/*"],
                description="Pre-commit and validator",
            ),
        ],
        max_context_tokens=8000,
        supports_code_execution=False,
        supports_file_editing=True,
        supports_web_browsing=False,
    ),
]


class SpecificationAnalyzer:
    """Analyzes project specifications to extract requirements."""

    def __init__(self, spec_path: str) -> None:
        self.spec_path = Path(spec_path)
        self._cache: dict[str, Any] = {}

    def analyze(self) -> dict[str, Any]:
        """Analyze the specification file and extract structured data."""
        if not self.spec_path.exists():
            logger.warning(f"Specification file not found: {self.spec_path}")
            return {}

        content = self.spec_path.read_text()
        return self._parse_specification(content)

    def _parse_specification(self, content: str) -> dict[str, Any]:
        """Parse specification content into structured data."""
        result: dict[str, Any] = {
            "title": "",
            "version": "",
            "phases": [],
            "components": [],
            "requirements": [],
        }

        lines = content.split("\n")
        current_section = ""

        for line in lines:
            if line.startswith("# "):
                result["title"] = line[2:].strip()
            elif line.startswith("## "):
                current_section = line[3:].strip().lower()
            elif line.startswith("- ") and current_section:
                item = line[2:].strip()
                if "phase" in current_section:
                    result["phases"].append(item)
                elif "component" in current_section:
                    result["components"].append(item)
                elif "requirement" in current_section:
                    result["requirements"].append(item)

        return result

    def extract_phases(self) -> list[PhaseSpec]:
        """Extract phase specifications from the document."""
        data = self.analyze()
        phases = []

        for i, phase_name in enumerate(data.get("phases", []), 1):
            phase = PhaseSpec(
                phase_id=f"phase_{i}",
                name=phase_name,
                description=f"Phase {i}: {phase_name}",
                epics=[],
            )
            phases.append(phase)

        return phases


class RoadmapParser:
    """Parses roadmaps and phase plans into task hierarchies."""

    def __init__(self, roadmap_path: str) -> None:
        self.roadmap_path = Path(roadmap_path)

    def parse(self) -> list[PhaseSpec]:
        """Parse the roadmap file into phase specifications."""
        if not self.roadmap_path.exists():
            logger.warning(f"Roadmap file not found: {self.roadmap_path}")
            return []

        content = self.roadmap_path.read_text()
        return self._parse_roadmap(content)

    def _parse_roadmap(self, content: str) -> list[PhaseSpec]:
        """Parse roadmap content into phase specifications."""
        phases = []
        current_phase: Optional[PhaseSpec] = None
        current_epic: Optional[EpicSpec] = None

        lines = content.split("\n")
        for line in lines:
            if line.startswith("# Phase"):
                match = re.match(r"# Phase (\d+)[:\s]+(.+)", line)
                if match:
                    phase_num = match.group(1)
                    phase_name = match.group(2).strip()
                    current_phase = PhaseSpec(
                        phase_id=f"phase_{phase_num}",
                        name=phase_name,
                        description=f"Phase {phase_num}: {phase_name}",
                        epics=[],
                    )
                    phases.append(current_phase)
                    current_epic = None

            elif line.startswith("## Epic") and current_phase:
                match = re.match(r"## Epic (\d+\.\d+)[:\s]+(.+)", line)
                if match:
                    epic_id = match.group(1)
                    epic_name = match.group(2).strip()
                    current_epic = EpicSpec(
                        epic_id=f"epic_{epic_id}",
                        name=epic_name,
                        description=epic_name,
                        tasks=[],
                    )
                    current_phase.epics.append(current_epic)

            elif line.startswith("### Task") and current_epic:
                match = re.match(r"### Task (\d+\.\d+\.\d+)[:\s]+(.+)", line)
                if match:
                    task_id = match.group(1)
                    task_name = match.group(2).strip()
                    task = TaskSpec(
                        task_id=f"task_{task_id}",
                        name=task_name,
                        description=task_name,
                        requirements=[],
                        acceptance_criteria=[],
                    )
                    current_epic.tasks.append(task)

        return phases


class ToolMatcher:
    """Matches tasks to appropriate tools based on capabilities."""

    def __init__(
        self,
        capabilities: Optional[list[ToolCapability]] = None,
    ) -> None:
        self.capabilities = capabilities or DEFAULT_TOOL_CAPABILITIES
        self._capability_map = {cap.tool: cap for cap in self.capabilities}

    def match_task(self, task: TaskSpec) -> TaskAssignment:
        """Match a task to the most appropriate tool."""
        best_tool = ToolType.DEVIN
        best_score = 0.0

        for capability in self.capabilities:
            score = self._calculate_match_score(task, capability)
            if score > best_score:
                best_score = score
                best_tool = capability.tool

        return TaskAssignment(
            task_id=task.task_id,
            task_name=task.name,
            description=task.description,
            tool=best_tool,
            file_paths=task.file_paths,
            dependencies=task.dependencies,
            priority=TaskPriority.MEDIUM,
        )

    def _calculate_match_score(
        self,
        task: TaskSpec,
        capability: ToolCapability,
    ) -> float:
        """Calculate how well a tool matches a task."""
        score = 0.0

        for ownership in capability.file_ownership:
            for path in task.file_paths:
                if ownership.owns_path(path):
                    score += 10.0

        if task.assigned_tool == capability.tool:
            score += 5.0

        return score

    def check_conflicts(
        self,
        assignments: list[TaskAssignment],
    ) -> list[str]:
        """Check for file ownership conflicts between assignments."""
        conflicts = []
        file_owners: dict[str, ToolType] = {}

        for assignment in assignments:
            for path in assignment.file_paths:
                if path in file_owners:
                    existing_tool = file_owners[path]
                    if existing_tool != assignment.tool:
                        conflicts.append(
                            f"File conflict: {path} assigned to both "
                            f"{existing_tool.value} and {assignment.tool.value}"
                        )
                else:
                    file_owners[path] = assignment.tool

        return conflicts


class PromptGenerator:
    """Generates detailed prompts from task specifications."""

    def __init__(self, output_dir: str = "project_prompts") -> None:
        self.output_dir = Path(output_dir)
        self._prompt_counter = 0

    def generate(
        self,
        context: PromptContext,
        assignment: TaskAssignment,
    ) -> PromptOutput:
        """Generate a prompt from context and assignment."""
        self._prompt_counter += 1
        prompt_id = f"prompt_{self._prompt_counter:04d}"

        content = self._build_prompt_content(context, assignment)
        file_name = self._generate_file_name(context, assignment)
        file_path = str(self.output_dir / context.phase_name / file_name)

        return PromptOutput(
            prompt_id=prompt_id,
            task_id=context.task_id,
            tool=assignment.tool,
            title=context.task_name,
            content=content,
            file_path=file_path,
            status=PromptStatus.READY,
            metadata={
                "phase": context.phase_name,
                "epic": context.epic_name,
                "dependencies": context.dependencies,
            },
        )

    def _build_prompt_content(
        self,
        context: PromptContext,
        assignment: TaskAssignment,
    ) -> str:
        """Build the prompt content from context and assignment."""
        sections = []

        sections.append(f"# {context.task_name}")
        sections.append("")
        sections.append(f"**Task ID:** {context.task_id}")
        sections.append(f"**Tool:** {assignment.tool.value}")
        sections.append(f"**Phase:** {context.phase_name}")
        sections.append(f"**Epic:** {context.epic_name}")
        sections.append("")

        sections.append("## Context")
        sections.append("")
        sections.append(context.description)
        sections.append("")

        if context.requirements:
            sections.append("## Requirements")
            sections.append("")
            for req in context.requirements:
                sections.append(f"- {req}")
            sections.append("")

        if context.acceptance_criteria:
            sections.append("## Acceptance Criteria")
            sections.append("")
            for criterion in context.acceptance_criteria:
                sections.append(f"- {criterion}")
            sections.append("")

        if context.file_paths:
            sections.append("## Files to Modify")
            sections.append("")
            for path in context.file_paths:
                sections.append(f"- `{path}`")
            sections.append("")

        if context.do_not_touch:
            sections.append("## Do NOT Touch")
            sections.append("")
            sections.append("The following files are owned by other tools and must not be modified:")
            sections.append("")
            for path in context.do_not_touch:
                sections.append(f"- `{path}`")
            sections.append("")

        if context.dependencies:
            sections.append("## Dependencies")
            sections.append("")
            sections.append("This task depends on the completion of:")
            sections.append("")
            for dep in context.dependencies:
                sections.append(f"- {dep}")
            sections.append("")

        sections.append("## Instructions")
        sections.append("")
        sections.append("1. Review the requirements and acceptance criteria above")
        sections.append("2. Implement the required changes in the specified files")
        sections.append("3. Write tests to verify the implementation")
        sections.append("4. Ensure all existing tests continue to pass")
        sections.append("5. Update documentation as needed")
        sections.append("")

        sections.append("## Success Criteria")
        sections.append("")
        sections.append("- All acceptance criteria are met")
        sections.append("- All tests pass")
        sections.append("- Code follows project conventions")
        sections.append("- No regressions introduced")
        sections.append("")

        return "\n".join(sections)

    def _generate_file_name(
        self,
        context: PromptContext,
        assignment: TaskAssignment,
    ) -> str:
        """Generate a file name for the prompt."""
        task_id = context.task_id.replace("task_", "")
        tool_name = assignment.tool.value
        task_slug = re.sub(r"[^a-z0-9]+", "_", context.task_name.lower())
        task_slug = task_slug[:30].strip("_")

        return f"{task_id}_{tool_name}_{task_slug}.md"

    def save_prompt(self, prompt: PromptOutput) -> bool:
        """Save a prompt to disk."""
        try:
            file_path = Path(prompt.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(prompt.content)
            logger.info(f"Saved prompt to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save prompt: {e}")
            return False


class PromptArchitectOrchestrator:
    """Main orchestrator for the Prompt Architect Agent."""

    def __init__(
        self,
        spec_path: str = "specifications/lattice_lock_framework_specifications.md",
        roadmap_dir: str = "developer_documentation",
        output_dir: str = "project_prompts",
        state_file: str = "project_prompts/project_prompts_state.json",
    ) -> None:
        self.spec_analyzer = SpecificationAnalyzer(spec_path)
        self.roadmap_dir = Path(roadmap_dir)
        self.tool_matcher = ToolMatcher()
        self.prompt_generator = PromptGenerator(output_dir)
        self.state_file = Path(state_file)
        self._state: dict[str, Any] = {}

    def load_state(self) -> None:
        """Load the current state from disk."""
        if self.state_file.exists():
            try:
                self._state = json.loads(self.state_file.read_text())
            except json.JSONDecodeError:
                logger.warning("Failed to parse state file, starting fresh")
                self._state = {}
        else:
            self._state = {}

    def save_state(self) -> None:
        """Save the current state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state["updated_at"] = datetime.utcnow().isoformat()
        self.state_file.write_text(json.dumps(self._state, indent=2))

    def generate_prompts(self, request: GenerationRequest) -> GenerationResult:
        """Generate prompts based on the request."""
        start_time = time.time()
        result = GenerationResult(
            success=True,
            prompts_generated=0,
            prompts_updated=0,
            prompts_skipped=0,
        )

        self.load_state()

        phases = self._get_phases(request)
        if not phases:
            result.add_warning("No phases found to process")
            return result

        for phase in phases:
            if request.phase and phase.phase_id != f"phase_{request.phase}":
                continue

            for epic in phase.epics:
                if request.epic and epic.epic_id != f"epic_{request.epic}":
                    continue

                for task in epic.tasks:
                    if request.task_ids and task.task_id not in request.task_ids:
                        continue

                    try:
                        prompt = self._generate_task_prompt(
                            phase, epic, task, request
                        )
                        if prompt:
                            result.add_prompt(prompt)
                            if not request.dry_run:
                                self.prompt_generator.save_prompt(prompt)
                    except Exception as e:
                        result.add_error(f"Failed to generate prompt for {task.task_id}: {e}")

        if not request.dry_run:
            self._update_state(result)
            self.save_state()

        result.execution_time_seconds = time.time() - start_time
        return result

    def _get_phases(self, request: GenerationRequest) -> list[PhaseSpec]:
        """Get phases from roadmap files."""
        phases = []

        for roadmap_file in self.roadmap_dir.glob("*_phase_*_plan.md"):
            parser = RoadmapParser(str(roadmap_file))
            phases.extend(parser.parse())

        if not phases:
            phases = self.spec_analyzer.extract_phases()

        return phases

    def _generate_task_prompt(
        self,
        phase: PhaseSpec,
        epic: EpicSpec,
        task: TaskSpec,
        request: GenerationRequest,
    ) -> Optional[PromptOutput]:
        """Generate a prompt for a single task."""
        assignment = self.tool_matcher.match_task(task)

        do_not_touch = self._get_do_not_touch_paths(assignment.tool)

        context = PromptContext(
            project_name=request.project_name,
            phase_name=phase.name,
            epic_name=epic.name,
            task_id=task.task_id,
            task_name=task.name,
            description=task.description,
            requirements=task.requirements,
            acceptance_criteria=task.acceptance_criteria,
            dependencies=task.dependencies,
            file_paths=task.file_paths,
            do_not_touch=do_not_touch,
        )

        return self.prompt_generator.generate(context, assignment)

    def _get_do_not_touch_paths(self, tool: ToolType) -> list[str]:
        """Get paths that should not be touched by a tool."""
        do_not_touch = []

        for capability in self.tool_matcher.capabilities:
            if capability.tool != tool:
                for ownership in capability.file_ownership:
                    do_not_touch.extend(ownership.paths)
                    do_not_touch.extend(ownership.patterns)

        return do_not_touch

    def _update_state(self, result: GenerationResult) -> None:
        """Update the state with generation results."""
        if "prompts" not in self._state:
            self._state["prompts"] = {}

        for prompt in result.generated_prompts:
            self._state["prompts"][prompt.prompt_id] = {
                "task_id": prompt.task_id,
                "tool": prompt.tool.value,
                "file_path": prompt.file_path,
                "status": prompt.status.value,
                "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
            }

        self._state["last_generation"] = {
            "prompts_generated": result.prompts_generated,
            "prompts_updated": result.prompts_updated,
            "errors": result.errors,
            "timestamp": datetime.utcnow().isoformat(),
        }


__all__ = [
    "SpecificationAnalyzer",
    "RoadmapParser",
    "ToolMatcher",
    "PromptGenerator",
    "PromptArchitectOrchestrator",
    "DEFAULT_TOOL_CAPABILITIES",
]
