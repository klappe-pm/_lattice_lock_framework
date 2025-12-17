"""
PromptArchitectAgent - Main agent class for automated prompt generation.

This module provides the core agent class that loads the YAML definition,
coordinates subagents, and manages the prompt generation workflow.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from lattice_lock_agents.prompt_architect.subagents.roadmap_parser import RoadmapParser
from lattice_lock_agents.prompt_architect.subagents.spec_analyzer import SpecAnalyzer
from lattice_lock_agents.prompt_architect.subagents.tool_matcher import ToolMatcher
from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

if TYPE_CHECKING:
    from lattice_lock_agents.prompt_architect.subagents.prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration loaded from the agent YAML definition."""

    name: str
    version: str
    description: str
    role: str
    default_provider: str = "local"
    default_model: str = "deepseek-r1:70b"
    max_steps: int = 100
    timeout_seconds: int = 600
    log_level: str = "INFO"


@dataclass
class GenerationResult:
    """Result of a prompt generation run."""

    status: str  # success, failure, partial
    prompts_generated: int = 0
    prompts_updated: int = 0
    phases_covered: list[str] = field(default_factory=list)
    tool_distribution: dict[str, int] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status,
            "prompts_generated": self.prompts_generated,
            "prompts_updated": self.prompts_updated,
            "phases_covered": self.phases_covered,
            "tool_distribution": self.tool_distribution,
            "metrics": self.metrics,
            "errors": self.errors,
        }


class PromptArchitectAgent:
    """
    Main agent class for automated prompt generation.

    Loads the YAML definition, coordinates the four subagents
    (spec_analyzer, roadmap_parser, tool_matcher, prompt_generator),
    and manages the prompt generation workflow.
    """

    DEFAULT_DEFINITION_PATH = "agent_definitions/prompt_architect_agent/prompt_architect_agent.yaml"
    DEFAULT_TOOL_PROFILES_PATH = (
        "agent_definitions/prompt_architect_agent/subagents/tool_matcher.yaml"
    )

    def __init__(
        self,
        definition_path: str | None = None,
        repo_root: Path | None = None,
    ):
        """
        Initialize the PromptArchitectAgent.

        Args:
            definition_path: Path to the agent YAML definition file.
            repo_root: Root directory of the repository.
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

        if definition_path is None:
            definition_path = str(repo_root / self.DEFAULT_DEFINITION_PATH)

        self.definition_path = Path(definition_path)
        self.definition = self._load_definition()
        self.config = self._parse_config()

        # Initialize state tracking
        self._state: dict[str, Any] = {
            "current_phase": None,
            "prompts_generated": 0,
            "prompts_updated": 0,
            "errors": [],
            "start_time": None,
            "end_time": None,
        }

        # Initialize subagents (lazy loading)
        self._spec_analyzer: SpecAnalyzer | None = None
        self._roadmap_parser: RoadmapParser | None = None
        self._tool_matcher: ToolMatcher | None = None
        self._prompt_generator: PromptGenerator | None = None
        self._tracker_client: TrackerClient | None = None

        logger.info(f"PromptArchitectAgent initialized: {self.config.name} v{self.config.version}")

    def _load_definition(self) -> dict[str, Any]:
        """Load the YAML definition file."""
        if not self.definition_path.exists():
            logger.warning(f"Definition file not found at {self.definition_path}, using defaults")
            return {}

        with open(self.definition_path) as f:
            return yaml.safe_load(f) or {}

    def _parse_config(self) -> AgentConfig:
        """Parse configuration from the loaded definition."""
        agent_section = self.definition.get("agent", {})
        identity = agent_section.get("identity", {})
        configuration = agent_section.get("configuration", {})
        model_selection = self.definition.get("model_selection", {})

        return AgentConfig(
            name=identity.get("name", "prompt_architect_agent"),
            version=identity.get("version", "1.0.0"),
            description=identity.get("description", "Prompt Architect Agent"),
            role=identity.get("role", "Prompt Architect"),
            default_provider=model_selection.get("default_provider", "local"),
            default_model=model_selection.get("default_model", "deepseek-r1:70b"),
            max_steps=configuration.get("max_steps", 100),
            timeout_seconds=configuration.get("timeout_seconds", 600),
            log_level=configuration.get("log_level", "INFO"),
        )

    @property
    def spec_analyzer(self) -> SpecAnalyzer:
        """Get or create the SpecAnalyzer subagent."""
        if self._spec_analyzer is None:
            self._spec_analyzer = SpecAnalyzer(use_llm=False)
        return self._spec_analyzer

    @property
    def roadmap_parser(self) -> RoadmapParser:
        """Get or create the RoadmapParser subagent."""
        if self._roadmap_parser is None:
            self._roadmap_parser = RoadmapParser()
        return self._roadmap_parser

    @property
    def tool_matcher(self) -> ToolMatcher:
        """Get or create the ToolMatcher subagent."""
        if self._tool_matcher is None:
            tool_profiles_path = str(self.repo_root / self.DEFAULT_TOOL_PROFILES_PATH)
            self._tool_matcher = ToolMatcher(config_path=tool_profiles_path)
        return self._tool_matcher

    @property
    def prompt_generator(self) -> "PromptGenerator":
        """Get or create the PromptGenerator subagent."""
        if self._prompt_generator is None:
            config_path = str(
                self.repo_root
                / "agent_definitions/prompt_architect_agent/subagents/prompt_generator.yaml"
            )
            from lattice_lock_agents.prompt_architect.subagents.prompt_generator import (
                PromptGenerator,
            )

            self._prompt_generator = PromptGenerator(config_path=config_path)
        return self._prompt_generator

    @property
    def tracker_client(self) -> TrackerClient:
        """Get or create the TrackerClient."""
        if self._tracker_client is None:
            self._tracker_client = TrackerClient(repo_root=self.repo_root)
        return self._tracker_client

    def get_definition(self) -> dict[str, Any]:
        """Get the full agent definition."""
        return self.definition

    def get_config(self) -> AgentConfig:
        """Get the parsed agent configuration."""
        return self.config

    def get_state(self) -> dict[str, Any]:
        """Get the current agent state."""
        return self._state.copy()

    def reset_state(self) -> None:
        """Reset the agent state for a new generation run."""
        self._state = {
            "current_phase": None,
            "prompts_generated": 0,
            "prompts_updated": 0,
            "errors": [],
            "start_time": None,
            "end_time": None,
        }

    def get_subagents(self) -> list[dict[str, Any]]:
        """Get the list of configured subagents from the definition."""
        delegation = self.definition.get("delegation", {})
        return delegation.get("allowed_subagents", [])

    def get_model_strategy(self, task_type: str) -> dict[str, Any]:
        """
        Get the model selection strategy for a specific task type.

        Args:
            task_type: Type of task (specification_analysis, roadmap_parsing, etc.)

        Returns:
            Strategy configuration with primary and fallback models.
        """
        model_selection = self.definition.get("model_selection", {})
        strategies = model_selection.get("strategies", {})
        return strategies.get(
            task_type,
            {
                "primary": self.config.default_model,
                "fallback": "claude-sonnet-4.5",
                "selection_criteria": "balanced",
            },
        )

    def get_guardrails(self) -> list[str]:
        """Get the list of guardrails from the definition."""
        return self.definition.get("guardrails", [])

    def validate_guardrails(self, action: str, target: str) -> bool:
        """
        Validate an action against the agent's guardrails.

        Args:
            action: The action being performed (e.g., "modify", "generate")
            target: The target of the action (e.g., file path)

        Returns:
            True if the action is allowed, False otherwise.
        """
        _guardrails = self.get_guardrails()  # Reserved for future guardrail checks

        # Check for credential/secret access
        if "credentials" in target.lower() or "secrets" in target.lower():
            logger.warning(f"Guardrail violation: Cannot access {target}")
            return False

        # Check for file ownership conflicts
        scope = self.definition.get("scope", {})
        cannot_modify = scope.get("cannot_modify", [])
        for restricted in cannot_modify:
            if target.startswith(restricted.lstrip("/")):
                logger.warning(f"Guardrail violation: Cannot modify {target}")
                return False

        return True

    def invoke_spec_analyzer(self, spec_path: str) -> Any:
        """
        Invoke the spec_analyzer subagent.

        Args:
            spec_path: Path to the specification file.

        Returns:
            SpecificationAnalysis result.
        """
        logger.info(f"Invoking spec_analyzer on {spec_path}")
        self._state["current_phase"] = "specification_analysis"
        return self.spec_analyzer.analyze(spec_path)

    def invoke_roadmap_parser(self, roadmap_path: str) -> Any:
        """
        Invoke the roadmap_parser subagent.

        Args:
            roadmap_path: Path to the roadmap file.

        Returns:
            RoadmapStructure result.
        """
        logger.info(f"Invoking roadmap_parser on {roadmap_path}")
        self._state["current_phase"] = "roadmap_parsing"
        return self.roadmap_parser.parse(roadmap_path)

    def invoke_tool_matcher(self, tasks: list[Any]) -> list[Any]:
        """
        Invoke the tool_matcher subagent.

        Args:
            tasks: List of tasks to match to tools.

        Returns:
            List of ToolAssignment results.
        """
        logger.info(f"Invoking tool_matcher on {len(tasks)} tasks")
        self._state["current_phase"] = "tool_matching"
        return self.tool_matcher.match(tasks)

    async def invoke_prompt_generator(
        self,
        assignment: Any,
        context_data: dict[str, Any],
    ) -> Any:
        """
        Invoke the prompt_generator subagent.

        Args:
            assignment: ToolAssignment for the task.
            context_data: Context data for prompt generation.

        Returns:
            GeneratedPrompt result.
        """
        logger.info(f"Invoking prompt_generator for task {assignment.task_id}")
        self._state["current_phase"] = "prompt_generation"
        return await self.prompt_generator.generate(assignment, context_data)

    def update_tracker_state(self, prompt_id: str, **kwargs: Any) -> dict[str, Any]:
        """
        Update the tracker state for a prompt.

        Args:
            prompt_id: The prompt ID to update.
            **kwargs: Fields to update (done, merged, pr_url, model).

        Returns:
            Update result.
        """
        return self.tracker_client.update_prompt(prompt_id, **kwargs)

    def get_generation_summary(self) -> GenerationResult:
        """
        Get a summary of the current generation run.

        Returns:
            GenerationResult with current statistics.
        """
        return GenerationResult(
            status="success" if not self._state["errors"] else "partial",
            prompts_generated=self._state["prompts_generated"],
            prompts_updated=self._state["prompts_updated"],
            phases_covered=[self._state["current_phase"]] if self._state["current_phase"] else [],
            errors=self._state["errors"],
            metrics={
                "start_time": self._state["start_time"],
                "end_time": self._state["end_time"],
            },
        )


__all__ = ["PromptArchitectAgent", "AgentConfig", "GenerationResult"]
