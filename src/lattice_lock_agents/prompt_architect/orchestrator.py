"""
Prompt Architect Orchestrator - Coordinates the prompt generation pipeline.

This module provides the main orchestration logic that coordinates the four
subagents (spec_analyzer, roadmap_parser, tool_matcher, prompt_generator)
to generate prompts from specifications and roadmaps.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from lattice_lock_agents.prompt_architect.agent import GenerationResult, PromptArchitectAgent
from lattice_lock_agents.prompt_architect.subagents.tool_profiles import Task

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationConfig:
    """Configuration for the orchestration pipeline."""

    spec_path: Optional[str] = None
    roadmap_path: Optional[str] = None
    output_dir: Optional[str] = None
    dry_run: bool = False
    from_project: bool = False
    phases: Optional[list[str]] = None
    tools: Optional[list[str]] = None
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class PipelineStage:
    """Represents a stage in the orchestration pipeline."""

    name: str
    status: str = "pending"  # pending, running, completed, failed, skipped
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retries: int = 0


@dataclass
class OrchestrationState:
    """State of the orchestration pipeline."""

    stages: dict[str, PipelineStage] = field(default_factory=dict)
    spec_analysis: Any = None
    roadmap_structure: Any = None
    tool_assignments: list[Any] = field(default_factory=list)
    generated_prompts: list[Any] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialize pipeline stages."""
        if not self.stages:
            self.stages = {
                "spec_analysis": PipelineStage(name="Specification Analysis"),
                "roadmap_parsing": PipelineStage(name="Roadmap Parsing"),
                "tool_matching": PipelineStage(name="Tool Matching"),
                "prompt_generation": PipelineStage(name="Prompt Generation"),
            }


class PromptOrchestrator:
    """
    Orchestrates the prompt generation pipeline.

    Coordinates the four subagents in sequence:
    1. spec_analyzer - Analyzes specifications
    2. roadmap_parser - Parses roadmaps into tasks
    3. tool_matcher - Assigns tasks to tools
    4. prompt_generator - Generates detailed prompts
    """

    def __init__(
        self,
        agent: Optional[PromptArchitectAgent] = None,
        repo_root: Optional[Path] = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            agent: PromptArchitectAgent instance (created if not provided).
            repo_root: Root directory of the repository.
        """
        self.agent = agent or PromptArchitectAgent(repo_root=repo_root)
        self.repo_root = repo_root or self.agent.repo_root
        self.state = OrchestrationState()

    def reset(self) -> None:
        """Reset the orchestrator state for a new run."""
        self.state = OrchestrationState()
        self.agent.reset_state()

    async def orchestrate_prompt_generation(
        self,
        spec_path: Optional[str] = None,
        roadmap_path: Optional[str] = None,
        output_dir: Optional[str] = None,
        dry_run: bool = False,
        from_project: bool = False,
        phases: Optional[list[str]] = None,
        tools: Optional[list[str]] = None,
    ) -> GenerationResult:
        """
        Orchestrate the full prompt generation pipeline.

        Args:
            spec_path: Path to the specification file.
            roadmap_path: Path to the roadmap/WBS file.
            output_dir: Directory to output generated prompts.
            dry_run: If True, don't write files, just simulate.
            from_project: If True, discover spec/roadmap from Project Agent.
            phases: Filter to specific phases (e.g., ["1", "2"]).
            tools: Filter to specific tools (e.g., ["devin", "gemini"]).

        Returns:
            GenerationResult with statistics and any errors.
        """
        self.reset()
        self.state.start_time = datetime.now()

        config = OrchestrationConfig(
            spec_path=spec_path,
            roadmap_path=roadmap_path,
            output_dir=output_dir,
            dry_run=dry_run,
            from_project=from_project,
            phases=phases,
            tools=tools,
        )

        logger.info("Starting prompt generation orchestration")
        logger.info(f"Config: spec={spec_path}, roadmap={roadmap_path}, dry_run={dry_run}")

        try:
            # Stage 1: Specification Analysis
            if spec_path or from_project:
                await self._run_spec_analysis(config)

            # Stage 2: Roadmap Parsing
            if roadmap_path or from_project:
                await self._run_roadmap_parsing(config)

            # Stage 3: Tool Matching
            await self._run_tool_matching(config)

            # Stage 4: Prompt Generation
            await self._run_prompt_generation(config)

        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            self.state.errors.append(str(e))

        self.state.end_time = datetime.now()
        return self._build_result()

    async def _run_spec_analysis(self, config: OrchestrationConfig) -> None:
        """Run the specification analysis stage."""
        stage = self.state.stages["spec_analysis"]
        stage.status = "running"
        stage.start_time = datetime.now()

        try:
            if config.from_project:
                # Discover spec from Project Agent
                spec_path = await self._discover_spec_from_project()
            else:
                spec_path = config.spec_path

            if not spec_path:
                stage.status = "skipped"
                logger.info("Skipping spec analysis - no spec path provided")
                return

            # Validate path exists
            if not Path(spec_path).exists():
                raise FileNotFoundError(f"Specification file not found: {spec_path}")

            # Run analysis with retries
            for attempt in range(config.max_retries):
                try:
                    self.state.spec_analysis = self.agent.invoke_spec_analyzer(spec_path)
                    stage.result = self.state.spec_analysis
                    stage.status = "completed"
                    logger.info(
                        f"Spec analysis completed: {len(self.state.spec_analysis.requirements)} requirements found"
                    )
                    break
                except Exception as e:
                    stage.retries += 1
                    if attempt == config.max_retries - 1:
                        raise
                    logger.warning(f"Spec analysis attempt {attempt + 1} failed: {e}, retrying...")
                    await asyncio.sleep(config.retry_delay)

        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
            self.state.errors.append(f"Spec analysis failed: {e}")
            logger.error(f"Spec analysis failed: {e}")

        stage.end_time = datetime.now()

    async def _run_roadmap_parsing(self, config: OrchestrationConfig) -> None:
        """Run the roadmap parsing stage."""
        stage = self.state.stages["roadmap_parsing"]
        stage.status = "running"
        stage.start_time = datetime.now()

        try:
            if config.from_project:
                # Discover roadmap from Project Agent
                roadmap_path = await self._discover_roadmap_from_project()
            else:
                roadmap_path = config.roadmap_path

            if not roadmap_path:
                stage.status = "skipped"
                logger.info("Skipping roadmap parsing - no roadmap path provided")
                return

            # Validate path exists
            if not Path(roadmap_path).exists():
                raise FileNotFoundError(f"Roadmap file not found: {roadmap_path}")

            # Run parsing with retries
            for attempt in range(config.max_retries):
                try:
                    self.state.roadmap_structure = self.agent.invoke_roadmap_parser(roadmap_path)
                    stage.result = self.state.roadmap_structure
                    stage.status = "completed"
                    phase_count = len(self.state.roadmap_structure.phases)
                    logger.info(f"Roadmap parsing completed: {phase_count} phases found")
                    break
                except Exception as e:
                    stage.retries += 1
                    if attempt == config.max_retries - 1:
                        raise
                    logger.warning(
                        f"Roadmap parsing attempt {attempt + 1} failed: {e}, retrying..."
                    )
                    await asyncio.sleep(config.retry_delay)

        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
            self.state.errors.append(f"Roadmap parsing failed: {e}")
            logger.error(f"Roadmap parsing failed: {e}")

        stage.end_time = datetime.now()

    async def _run_tool_matching(self, config: OrchestrationConfig) -> None:
        """Run the tool matching stage."""
        stage = self.state.stages["tool_matching"]
        stage.status = "running"
        stage.start_time = datetime.now()

        try:
            # Build task list from roadmap structure
            tasks = self._build_task_list(config)

            if not tasks:
                stage.status = "skipped"
                logger.info("Skipping tool matching - no tasks to match")
                stage.end_time = datetime.now()
                return

            # Run matching with retries
            for attempt in range(config.max_retries):
                try:
                    self.state.tool_assignments = self.agent.invoke_tool_matcher(tasks)
                    stage.result = self.state.tool_assignments
                    stage.status = "completed"
                    logger.info(
                        f"Tool matching completed: {len(self.state.tool_assignments)} assignments"
                    )
                    break
                except Exception as e:
                    stage.retries += 1
                    if attempt == config.max_retries - 1:
                        raise
                    logger.warning(f"Tool matching attempt {attempt + 1} failed: {e}, retrying...")
                    await asyncio.sleep(config.retry_delay)

        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
            self.state.errors.append(f"Tool matching failed: {e}")
            logger.error(f"Tool matching failed: {e}")

        stage.end_time = datetime.now()

    async def _run_prompt_generation(self, config: OrchestrationConfig) -> None:
        """Run the prompt generation stage."""
        stage = self.state.stages["prompt_generation"]
        stage.status = "running"
        stage.start_time = datetime.now()

        try:
            if not self.state.tool_assignments:
                stage.status = "skipped"
                logger.info("Skipping prompt generation - no tool assignments")
                stage.end_time = datetime.now()
                return

            # Filter assignments by tools if specified
            assignments = self.state.tool_assignments
            if config.tools:
                assignments = [a for a in assignments if a.tool in config.tools]

            # Generate prompts for each assignment
            for assignment in assignments:
                if config.dry_run:
                    logger.info(f"[DRY RUN] Would generate prompt for {assignment.task_id}")
                    continue

                try:
                    context_data = self._build_context_data(assignment)
                    prompt = await self.agent.invoke_prompt_generator(assignment, context_data)
                    self.state.generated_prompts.append(prompt)
                    logger.info(f"Generated prompt: {prompt.prompt_id}")
                except Exception as e:
                    error_msg = f"Failed to generate prompt for {assignment.task_id}: {e}"
                    self.state.errors.append(error_msg)
                    logger.error(error_msg)

            stage.result = self.state.generated_prompts
            stage.status = "completed"
            logger.info(f"Prompt generation completed: {len(self.state.generated_prompts)} prompts")

        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
            self.state.errors.append(f"Prompt generation failed: {e}")
            logger.error(f"Prompt generation failed: {e}")

        stage.end_time = datetime.now()

    def _build_task_list(self, config: OrchestrationConfig) -> list[Task]:
        """Build a list of tasks from the roadmap structure."""
        tasks = []

        if not self.state.roadmap_structure:
            return tasks

        for phase in self.state.roadmap_structure.phases:
            # Filter by phases if specified
            if config.phases and phase.id not in config.phases:
                continue

            for epic in phase.epics:
                for task in epic.tasks:
                    tasks.append(
                        Task(
                            id=task.id,
                            description=task.description,
                            files=task.files if hasattr(task, "files") else [],
                        )
                    )

        return tasks

    def _build_context_data(self, assignment: Any) -> dict[str, Any]:
        """Build context data for prompt generation."""
        context_data: dict[str, Any] = {
            "task_id": assignment.task_id,
            "tool": assignment.tool,
            "files_owned": assignment.files_owned,
        }

        # Add spec analysis context if available
        if self.state.spec_analysis:
            context_data["spec_analysis"] = {
                "project_name": self.state.spec_analysis.project_name,
                "requirements_count": len(self.state.spec_analysis.requirements),
                "components_count": len(self.state.spec_analysis.components),
            }

        # Add roadmap context if available
        if self.state.roadmap_structure:
            context_data["roadmap"] = {
                "phases_count": len(self.state.roadmap_structure.phases),
            }

        return context_data

    async def _discover_spec_from_project(self) -> Optional[str]:
        """Discover specification path from Project Agent."""
        # This will be implemented in 5.1.2 with ProjectAgentClient
        # For now, try to find a default spec file
        default_paths = [
            self.repo_root / "specifications" / "lattice_lock_framework_specifications.md",
            self.repo_root / "SPECIFICATION.md",
            self.repo_root / "spec.md",
        ]

        for path in default_paths:
            if path.exists():
                logger.info(f"Discovered spec file: {path}")
                return str(path)

        logger.warning("Could not discover spec file from project")
        return None

    async def _discover_roadmap_from_project(self) -> Optional[str]:
        """Discover roadmap path from Project Agent."""
        # This will be implemented in 5.1.2 with ProjectAgentClient
        # For now, try to find a default roadmap file
        default_paths = [
            self.repo_root / "project_prompts" / "work_breakdown_structure.md",
            self.repo_root
            / "developer_documentation"
            / "development"
            / "lattice_lock_work_breakdown_v2_1.md",
            self.repo_root / "ROADMAP.md",
        ]

        for path in default_paths:
            if path.exists():
                logger.info(f"Discovered roadmap file: {path}")
                return str(path)

        logger.warning("Could not discover roadmap file from project")
        return None

    def _build_result(self) -> GenerationResult:
        """Build the final generation result."""
        # Calculate tool distribution
        tool_distribution: dict[str, int] = {}
        for assignment in self.state.tool_assignments:
            tool = assignment.tool
            tool_distribution[tool] = tool_distribution.get(tool, 0) + 1

        # Determine phases covered
        phases_covered: list[str] = []
        if self.state.roadmap_structure:
            phases_covered = [p.id for p in self.state.roadmap_structure.phases]

        # Determine status
        if self.state.errors:
            status = "partial" if self.state.generated_prompts else "failure"
        else:
            status = "success"

        # Calculate duration
        duration = None
        if self.state.start_time and self.state.end_time:
            duration = (self.state.end_time - self.state.start_time).total_seconds()

        return GenerationResult(
            status=status,
            prompts_generated=len(self.state.generated_prompts),
            prompts_updated=0,  # TODO: Track updates separately
            phases_covered=phases_covered,
            tool_distribution=tool_distribution,
            errors=self.state.errors,
            metrics={
                "start_time": self.state.start_time.isoformat() if self.state.start_time else None,
                "end_time": self.state.end_time.isoformat() if self.state.end_time else None,
                "duration_seconds": duration,
                "stages": {
                    name: {
                        "status": stage.status,
                        "retries": stage.retries,
                        "error": stage.error,
                    }
                    for name, stage in self.state.stages.items()
                },
            },
        )

    def get_stage_status(self, stage_name: str) -> Optional[PipelineStage]:
        """Get the status of a specific pipeline stage."""
        return self.state.stages.get(stage_name)

    def get_all_stages(self) -> dict[str, PipelineStage]:
        """Get all pipeline stages."""
        return self.state.stages


async def orchestrate_prompt_generation(
    spec_path: Optional[str] = None,
    roadmap_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    dry_run: bool = False,
    from_project: bool = False,
    phases: Optional[list[str]] = None,
    tools: Optional[list[str]] = None,
    repo_root: Optional[Path] = None,
) -> GenerationResult:
    """
    Convenience function to orchestrate prompt generation.

    This is the main entry point for the orchestration pipeline.

    Args:
        spec_path: Path to the specification file.
        roadmap_path: Path to the roadmap/WBS file.
        output_dir: Directory to output generated prompts.
        dry_run: If True, don't write files, just simulate.
        from_project: If True, discover spec/roadmap from Project Agent.
        phases: Filter to specific phases (e.g., ["1", "2"]).
        tools: Filter to specific tools (e.g., ["devin", "gemini"]).
        repo_root: Root directory of the repository.

    Returns:
        GenerationResult with statistics and any errors.
    """
    orchestrator = PromptOrchestrator(repo_root=repo_root)
    return await orchestrator.orchestrate_prompt_generation(
        spec_path=spec_path,
        roadmap_path=roadmap_path,
        output_dir=output_dir,
        dry_run=dry_run,
        from_project=from_project,
        phases=phases,
        tools=tools,
    )


__all__ = [
    "PromptOrchestrator",
    "OrchestrationConfig",
    "OrchestrationState",
    "PipelineStage",
    "orchestrate_prompt_generation",
]
