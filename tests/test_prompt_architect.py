"""
Tests for the Prompt Architect Agent.

Tests the models, orchestrator, and CLI components.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

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

from lattice_lock.agents.prompt_architect.orchestrator import (
    SpecificationAnalyzer,
    RoadmapParser,
    ToolMatcher,
    PromptGenerator,
    PromptArchitectOrchestrator,
    DEFAULT_TOOL_CAPABILITIES,
)

from lattice_lock.agents.prompt_architect.cli import (
    create_parser,
    validate_prompts,
    format_result_json,
    main,
)


class TestToolType:
    """Tests for ToolType enum."""

    def test_tool_types_exist(self) -> None:
        """Test that all expected tool types exist."""
        assert ToolType.DEVIN.value == "devin"
        assert ToolType.GEMINI_CLI.value == "gemini_cli"
        assert ToolType.CODEX_CLI.value == "codex_cli"
        assert ToolType.CLAUDE_CLI.value == "claude_cli"
        assert ToolType.CLAUDE_APP.value == "claude_app"
        assert ToolType.CLAUDE_WEBSITE.value == "claude_website"


class TestPromptStatus:
    """Tests for PromptStatus enum."""

    def test_status_values(self) -> None:
        """Test that all expected status values exist."""
        assert PromptStatus.DRAFT.value == "draft"
        assert PromptStatus.READY.value == "ready"
        assert PromptStatus.IN_PROGRESS.value == "in_progress"
        assert PromptStatus.COMPLETED.value == "completed"
        assert PromptStatus.BLOCKED.value == "blocked"
        assert PromptStatus.FAILED.value == "failed"


class TestFileOwnership:
    """Tests for FileOwnership dataclass."""

    def test_owns_exact_path(self) -> None:
        """Test ownership of exact paths."""
        ownership = FileOwnership(
            tool=ToolType.DEVIN,
            paths=["src/main.py", "src/utils.py"],
        )
        assert ownership.owns_path("src/main.py")
        assert ownership.owns_path("src/utils.py")
        assert not ownership.owns_path("src/other.py")

    def test_owns_pattern_path(self) -> None:
        """Test ownership via patterns."""
        ownership = FileOwnership(
            tool=ToolType.DEVIN,
            paths=[],
            patterns=["src/agents/*", "tests/"],
        )
        assert ownership.owns_path("src/agents/prompt.py")
        assert ownership.owns_path("tests/test_main.py")
        assert not ownership.owns_path("docs/readme.md")


class TestToolCapability:
    """Tests for ToolCapability dataclass."""

    def test_can_handle_task_with_ownership(self) -> None:
        """Test task handling based on file ownership."""
        capability = ToolCapability(
            tool=ToolType.DEVIN,
            name="Devin",
            description="AI Engineer",
            strengths=["coding"],
            limitations=["slow"],
            file_ownership=[
                FileOwnership(
                    tool=ToolType.DEVIN,
                    paths=["src/main.py"],
                    patterns=["src/agents/*"],
                ),
            ],
        )
        assert capability.can_handle_task("code", ["src/main.py"])
        assert capability.can_handle_task("code", ["src/agents/test.py"])
        assert not capability.can_handle_task("code", ["docs/readme.md"])


class TestTaskAssignment:
    """Tests for TaskAssignment dataclass."""

    def test_create_assignment(self) -> None:
        """Test creating a task assignment."""
        assignment = TaskAssignment(
            task_id="task_1",
            task_name="Implement feature",
            description="Add new feature",
            tool=ToolType.DEVIN,
            file_paths=["src/feature.py"],
            dependencies=["task_0"],
            priority=TaskPriority.HIGH,
        )
        assert assignment.task_id == "task_1"
        assert assignment.tool == ToolType.DEVIN
        assert assignment.priority == TaskPriority.HIGH


class TestPromptContext:
    """Tests for PromptContext dataclass."""

    def test_create_context(self) -> None:
        """Test creating a prompt context."""
        context = PromptContext(
            project_name="Test Project",
            phase_name="Phase 1",
            epic_name="Epic 1.1",
            task_id="task_1.1.1",
            task_name="Implement feature",
            description="Add new feature to the system",
            requirements=["Must be fast", "Must be secure"],
            acceptance_criteria=["Tests pass", "Code reviewed"],
        )
        assert context.project_name == "Test Project"
        assert len(context.requirements) == 2
        assert len(context.acceptance_criteria) == 2


class TestPromptTemplate:
    """Tests for PromptTemplate dataclass."""

    def test_validate_context_success(self) -> None:
        """Test context validation with all required fields."""
        template = PromptTemplate(
            name="Standard",
            tool=ToolType.DEVIN,
            sections=["Context", "Requirements"],
            required_fields=["project_name", "task_name"],
        )
        context = PromptContext(
            project_name="Test",
            phase_name="Phase 1",
            epic_name="Epic 1",
            task_id="task_1",
            task_name="Task",
            description="Desc",
            requirements=[],
            acceptance_criteria=[],
        )
        errors = template.validate_context(context)
        assert len(errors) == 0

    def test_validate_context_missing_field(self) -> None:
        """Test context validation with missing required field."""
        template = PromptTemplate(
            name="Standard",
            tool=ToolType.DEVIN,
            sections=["Context"],
            required_fields=["nonexistent_field"],
        )
        context = PromptContext(
            project_name="Test",
            phase_name="Phase 1",
            epic_name="Epic 1",
            task_id="task_1",
            task_name="Task",
            description="Desc",
            requirements=[],
            acceptance_criteria=[],
        )
        errors = template.validate_context(context)
        assert len(errors) == 1
        assert "nonexistent_field" in errors[0]


class TestPromptOutput:
    """Tests for PromptOutput dataclass."""

    def test_create_output_with_defaults(self) -> None:
        """Test creating output with default timestamps."""
        output = PromptOutput(
            prompt_id="prompt_001",
            task_id="task_1",
            tool=ToolType.DEVIN,
            title="Test Prompt",
            content="# Test\n\nContent here",
            file_path="prompts/test.md",
        )
        assert output.status == PromptStatus.DRAFT
        assert output.created_at is not None
        assert output.updated_at is not None


class TestGenerationResult:
    """Tests for GenerationResult dataclass."""

    def test_add_prompt(self) -> None:
        """Test adding a prompt to results."""
        result = GenerationResult(
            success=True,
            prompts_generated=0,
            prompts_updated=0,
            prompts_skipped=0,
        )
        prompt = PromptOutput(
            prompt_id="prompt_001",
            task_id="task_1",
            tool=ToolType.DEVIN,
            title="Test",
            content="Content",
            file_path="test.md",
        )
        result.add_prompt(prompt)
        assert result.prompts_generated == 1
        assert len(result.generated_prompts) == 1

    def test_add_error(self) -> None:
        """Test adding an error to results."""
        result = GenerationResult(
            success=True,
            prompts_generated=0,
            prompts_updated=0,
            prompts_skipped=0,
        )
        result.add_error("Something went wrong")
        assert not result.success
        assert len(result.errors) == 1

    def test_add_warning(self) -> None:
        """Test adding a warning to results."""
        result = GenerationResult(
            success=True,
            prompts_generated=0,
            prompts_updated=0,
            prompts_skipped=0,
        )
        result.add_warning("Minor issue")
        assert result.success
        assert len(result.warnings) == 1


class TestSpecificationAnalyzer:
    """Tests for SpecificationAnalyzer."""

    def test_analyze_nonexistent_file(self) -> None:
        """Test analyzing a nonexistent file."""
        analyzer = SpecificationAnalyzer("/nonexistent/path.md")
        result = analyzer.analyze()
        assert result == {}

    def test_analyze_specification(self) -> None:
        """Test analyzing a specification file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Project\n\n")
            f.write("## Phases\n\n")
            f.write("- Phase 1: Foundation\n")
            f.write("- Phase 2: Implementation\n")
            f.write("\n## Components\n\n")
            f.write("- Component A\n")
            f.write("- Component B\n")
            f.flush()

            analyzer = SpecificationAnalyzer(f.name)
            result = analyzer.analyze()

            assert result["title"] == "Test Project"
            assert len(result["phases"]) == 2
            assert len(result["components"]) == 2

            Path(f.name).unlink()


class TestRoadmapParser:
    """Tests for RoadmapParser."""

    def test_parse_nonexistent_file(self) -> None:
        """Test parsing a nonexistent file."""
        parser = RoadmapParser("/nonexistent/roadmap.md")
        result = parser.parse()
        assert result == []

    def test_parse_roadmap(self) -> None:
        """Test parsing a roadmap file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Phase 1: Foundation\n\n")
            f.write("## Epic 1.1: Setup\n\n")
            f.write("### Task 1.1.1: Initialize project\n\n")
            f.write("### Task 1.1.2: Configure CI\n\n")
            f.write("## Epic 1.2: Core\n\n")
            f.write("### Task 1.2.1: Implement core\n\n")
            f.flush()

            parser = RoadmapParser(f.name)
            phases = parser.parse()

            assert len(phases) == 1
            assert phases[0].name == "Foundation"
            assert len(phases[0].epics) == 2
            assert len(phases[0].epics[0].tasks) == 2

            Path(f.name).unlink()


class TestToolMatcher:
    """Tests for ToolMatcher."""

    def test_match_task_default(self) -> None:
        """Test matching a task with default capabilities."""
        matcher = ToolMatcher()
        task = TaskSpec(
            task_id="task_1",
            name="Test task",
            description="A test task",
            requirements=[],
            acceptance_criteria=[],
            file_paths=["src/unknown/file.py"],
        )
        assignment = matcher.match_task(task)
        assert assignment.task_id == "task_1"
        assert assignment.tool is not None

    def test_match_task_with_ownership(self) -> None:
        """Test matching a task based on file ownership."""
        capabilities = [
            ToolCapability(
                tool=ToolType.GEMINI_CLI,
                name="Gemini",
                description="Gemini CLI",
                strengths=[],
                limitations=[],
                file_ownership=[
                    FileOwnership(
                        tool=ToolType.GEMINI_CLI,
                        paths=[],
                        patterns=["src/validator/*"],
                    ),
                ],
            ),
        ]
        matcher = ToolMatcher(capabilities)
        task = TaskSpec(
            task_id="task_1",
            name="Validator task",
            description="A validator task",
            requirements=[],
            acceptance_criteria=[],
            file_paths=["src/validator/main.py"],
        )
        assignment = matcher.match_task(task)
        assert assignment.tool == ToolType.GEMINI_CLI

    def test_check_conflicts_no_conflicts(self) -> None:
        """Test conflict checking with no conflicts."""
        matcher = ToolMatcher()
        assignments = [
            TaskAssignment(
                task_id="task_1",
                task_name="Task 1",
                description="",
                tool=ToolType.DEVIN,
                file_paths=["src/a.py"],
            ),
            TaskAssignment(
                task_id="task_2",
                task_name="Task 2",
                description="",
                tool=ToolType.GEMINI_CLI,
                file_paths=["src/b.py"],
            ),
        ]
        conflicts = matcher.check_conflicts(assignments)
        assert len(conflicts) == 0

    def test_check_conflicts_with_conflict(self) -> None:
        """Test conflict checking with a conflict."""
        matcher = ToolMatcher()
        assignments = [
            TaskAssignment(
                task_id="task_1",
                task_name="Task 1",
                description="",
                tool=ToolType.DEVIN,
                file_paths=["src/shared.py"],
            ),
            TaskAssignment(
                task_id="task_2",
                task_name="Task 2",
                description="",
                tool=ToolType.GEMINI_CLI,
                file_paths=["src/shared.py"],
            ),
        ]
        conflicts = matcher.check_conflicts(assignments)
        assert len(conflicts) == 1
        assert "shared.py" in conflicts[0]


class TestPromptGenerator:
    """Tests for PromptGenerator."""

    def test_generate_prompt(self) -> None:
        """Test generating a prompt."""
        generator = PromptGenerator()
        context = PromptContext(
            project_name="Test Project",
            phase_name="phase_1",
            epic_name="Epic 1.1",
            task_id="task_1.1.1",
            task_name="Implement feature",
            description="Add new feature",
            requirements=["Must be fast"],
            acceptance_criteria=["Tests pass"],
            file_paths=["src/feature.py"],
            do_not_touch=["src/cli/main.py"],
        )
        assignment = TaskAssignment(
            task_id="task_1.1.1",
            task_name="Implement feature",
            description="Add new feature",
            tool=ToolType.DEVIN,
            file_paths=["src/feature.py"],
        )
        prompt = generator.generate(context, assignment)

        assert prompt.task_id == "task_1.1.1"
        assert prompt.tool == ToolType.DEVIN
        assert "Implement feature" in prompt.content
        assert "Must be fast" in prompt.content
        assert "Tests pass" in prompt.content
        assert "src/feature.py" in prompt.content
        assert "src/cli/main.py" in prompt.content

    def test_save_prompt(self) -> None:
        """Test saving a prompt to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PromptGenerator(tmpdir)
            prompt = PromptOutput(
                prompt_id="prompt_001",
                task_id="task_1",
                tool=ToolType.DEVIN,
                title="Test",
                content="# Test Content",
                file_path=f"{tmpdir}/phase_1/test.md",
            )
            success = generator.save_prompt(prompt)
            assert success
            assert Path(prompt.file_path).exists()
            assert Path(prompt.file_path).read_text() == "# Test Content"


class TestPromptArchitectOrchestrator:
    """Tests for PromptArchitectOrchestrator."""

    def test_load_save_state(self) -> None:
        """Test loading and saving state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/state.json"
            orchestrator = PromptArchitectOrchestrator(
                state_file=state_file,
            )
            orchestrator.load_state()
            assert orchestrator._state == {}

            orchestrator._state["test"] = "value"
            orchestrator.save_state()

            orchestrator2 = PromptArchitectOrchestrator(
                state_file=state_file,
            )
            orchestrator2.load_state()
            assert orchestrator2._state["test"] == "value"

    def test_generate_prompts_empty(self) -> None:
        """Test generating prompts with no phases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = PromptArchitectOrchestrator(
                spec_path=f"{tmpdir}/nonexistent.md",
                roadmap_dir=tmpdir,
                output_dir=tmpdir,
                state_file=f"{tmpdir}/state.json",
            )
            request = GenerationRequest(
                project_name="Test",
                dry_run=True,
            )
            result = orchestrator.generate_prompts(request)
            assert result.success
            assert result.prompts_generated == 0


class TestCLI:
    """Tests for the CLI."""

    def test_create_parser(self) -> None:
        """Test creating the argument parser."""
        parser = create_parser()
        assert parser is not None

    def test_validate_prompts_empty_dir(self) -> None:
        """Test validating an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = validate_prompts(Path(tmpdir))
            assert results["valid"]
            assert results["total"] == 0

    def test_validate_prompts_valid(self) -> None:
        """Test validating valid prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_file = Path(tmpdir) / "test.md"
            prompt_file.write_text(
                "# Test\n\n"
                "## Context\n\nContext here\n\n"
                "## Requirements\n\n- Req 1\n\n"
                "## Acceptance Criteria\n\n- Criterion 1\n"
            )
            results = validate_prompts(Path(tmpdir))
            assert results["valid"]
            assert results["total"] == 1
            assert results["valid_count"] == 1

    def test_validate_prompts_invalid(self) -> None:
        """Test validating invalid prompts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_file = Path(tmpdir) / "test.md"
            prompt_file.write_text("# Test\n\nNo sections here\n")
            results = validate_prompts(Path(tmpdir))
            assert not results["valid"]
            assert results["invalid_count"] == 1

    def test_format_result_json(self) -> None:
        """Test formatting result as JSON."""
        result = GenerationResult(
            success=True,
            prompts_generated=5,
            prompts_updated=2,
            prompts_skipped=1,
            execution_time_seconds=1.5,
        )
        json_str = format_result_json(result)
        data = json.loads(json_str)
        assert data["success"]
        assert data["prompts_generated"] == 5

    def test_main_no_command(self) -> None:
        """Test main with no command."""
        with patch("sys.stdout"):
            result = main([])
            assert result == 0

    def test_main_help(self) -> None:
        """Test main with help flag."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0


class TestDefaultToolCapabilities:
    """Tests for default tool capabilities."""

    def test_default_capabilities_exist(self) -> None:
        """Test that default capabilities are defined."""
        assert len(DEFAULT_TOOL_CAPABILITIES) > 0

    def test_devin_capability(self) -> None:
        """Test Devin capability configuration."""
        devin_cap = next(
            (c for c in DEFAULT_TOOL_CAPABILITIES if c.tool == ToolType.DEVIN),
            None,
        )
        assert devin_cap is not None
        assert devin_cap.supports_code_execution
        assert devin_cap.supports_web_browsing
