"""Convention checker for prompt file naming and placement."""

import logging
import os
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConventionResult(BaseModel):
    """Result of convention checking."""

    prompt_path: str
    is_valid: bool = True
    filename_valid: bool = True
    placement_valid: bool = True
    format_valid: bool = True
    tool_assignment_valid: bool = True
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    extracted_info: dict[str, Any] = Field(default_factory=dict)

    def add_error(self, error: str) -> None:
        """Add an error and mark as invalid."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning."""
        self.warnings.append(warning)


class ConventionChecker:
    """Checks prompt files against naming and placement conventions."""

    # Valid tool identifiers (ordered by specificity - longer matches first)
    VALID_TOOLS = {
        "claude_docs": "Claude Code Website",
        "claude_app": "Claude Code App",
        "claude_cli": "Claude Code CLI",
        "claude": "Claude Code CLI",
        "devin": "Devin AI",
        "gemini": "Gemini CLI",
        "codex": "Codex CLI",
    }

    # Filename pattern: {phase}.{epic}.{task}_{tool}_{description}.md
    # Examples: 1.1.1_devin_package_infrastructure.md, 5.4.2_claude_app_validation_integration.md
    # Also supports DONE- or STARTED- prefix
    # Tool pattern matches known tools (longest first to handle claude_app before claude)
    _TOOL_PATTERN = "|".join(sorted(VALID_TOOLS.keys(), key=len, reverse=True))
    FILENAME_PATTERN = re.compile(
        rf"^(?:DONE-|STARTED-)?(\d+)\.(\d+)\.(\d+)_({_TOOL_PATTERN})_(.+)\.md$"
    )

    # Phase directory patterns
    PHASE_DIR_PATTERN = re.compile(r"^phase(\d+)_([a-z_]+)$")

    # Tool to file ownership patterns
    TOOL_OWNERSHIP = {
        "devin": [
            "src/lattice_lock/orchestrator/",
            "src/lattice_lock/__init__.py",
            "src/lattice_lock/agents/",
            "pyproject.toml",
        ],
        "gemini": [
            "src/lattice_lock/validator/",
            "src/lattice_lock/sheriff/",
        ],
        "codex": [
            "src/lattice_lock/validator/",
            "src/lattice_lock/gauntlet/",
            "src/lattice_lock/dashboard/",
            ".pre-commit-config.yaml",
        ],
        "claude_cli": [
            "src/lattice_lock/cli/",
        ],
        "claude_app": [
            "src/lattice_lock/cli/commands/validate.py",
            "src/lattice_lock/cli/commands/doctor.py",
            "src/lattice_lock/admin/",
        ],
        "claude_docs": [
            "docs/",
        ],
    }

    def __init__(self, prompts_root: str = "project_prompts"):
        """
        Initialize the convention checker.

        Args:
            prompts_root: Root directory for prompts
        """
        self.prompts_root = prompts_root

    def check(self, prompt_path: str) -> ConventionResult:
        """
        Check a prompt file against conventions.

        Args:
            prompt_path: Path to the prompt file

        Returns:
            ConventionResult with all checks
        """
        result = ConventionResult(prompt_path=prompt_path)

        # Get path components
        path = Path(prompt_path)
        filename = path.name
        parent_dir = path.parent.name if path.parent else ""

        # Check filename convention
        self._check_filename(filename, result)

        # Check directory placement
        self._check_placement(prompt_path, parent_dir, result)

        # Check markdown formatting (requires file read)
        if os.path.exists(prompt_path):
            self._check_markdown_format(prompt_path, result)

        # Check tool assignment if we have extracted info
        if result.extracted_info.get("tool"):
            self._check_tool_assignment(prompt_path, result)

        return result

    def check_filename(self, filename: str) -> ConventionResult:
        """
        Check just the filename against conventions.

        Args:
            filename: The prompt filename

        Returns:
            ConventionResult for filename only
        """
        result = ConventionResult(prompt_path=filename)
        self._check_filename(filename, result)
        return result

    def _check_filename(self, filename: str, result: ConventionResult) -> None:
        """Check filename follows convention."""
        match = self.FILENAME_PATTERN.match(filename)

        if not match:
            result.filename_valid = False
            result.add_error(
                f"Filename '{filename}' does not match convention: "
                "{{phase}}.{{epic}}.{{task}}_{{tool}}_{{description}}.md"
            )
            return

        # Extract components
        phase = match.group(1)
        epic = match.group(2)
        task = match.group(3)
        tool = match.group(4)
        description = match.group(5)

        result.extracted_info = {
            "phase": int(phase),
            "epic": int(epic),
            "task": int(task),
            "task_id": f"{phase}.{epic}.{task}",
            "tool": tool,
            "description": description,
            "has_done_prefix": filename.startswith("DONE-"),
            "has_started_prefix": filename.startswith("STARTED-"),
        }

        # Validate tool identifier
        if tool not in self.VALID_TOOLS:
            result.add_warning(
                f"Tool identifier '{tool}' is not in known tools: {list(self.VALID_TOOLS.keys())}"
            )

        # Check description is present
        if not description:
            result.add_warning("Filename missing description after tool identifier")

    def _check_placement(self, prompt_path: str, parent_dir: str, result: ConventionResult) -> None:
        """Check file is in correct phase directory."""
        # Check if in a phase directory
        match = self.PHASE_DIR_PATTERN.match(parent_dir)
        if not match:
            result.placement_valid = False
            result.add_error("Prompt not in a valid phase directory. Expected: phase{N}_{name}")
            return

        dir_phase = int(match.group(1))

        # Check phase matches filename
        file_phase = result.extracted_info.get("phase")
        if file_phase is not None and file_phase != dir_phase:
            result.placement_valid = False
            result.add_error(
                f"Prompt phase ({file_phase}) doesn't match directory phase ({dir_phase})"
            )

    def _check_markdown_format(self, prompt_path: str, result: ConventionResult) -> None:
        """Check markdown formatting conventions."""
        try:
            with open(prompt_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"Failed to read file for format check: {e}")
            return

        lines = content.split("\n")

        # Check for proper heading structure
        if not lines or not lines[0].startswith("# "):
            result.format_valid = False
            result.add_error("File must start with a level 1 heading (# )")

        # Check for required ## sections
        section_headers = [line for line in lines if line.startswith("## ")]
        required_sections = ["Context", "Goal", "Steps", "Do NOT Touch", "Success Criteria"]
        found_sections = [h[3:].strip() for h in section_headers]

        for section in required_sections:
            if section not in found_sections:
                result.add_warning(f"Missing section header: ## {section}")

        # Check for trailing whitespace (style warning)
        for i, line in enumerate(lines, 1):
            if line.endswith(" "):
                result.add_warning(f"Line {i} has trailing whitespace")
                break  # Only report first occurrence

        # Check for consistent list formatting
        has_numbered = any(re.match(r"^\d+\.", line) for line in lines)
        has_bulleted = any(line.startswith("- ") for line in lines)

        if has_numbered and has_bulleted:
            # Check if they're mixed within sections
            in_steps = False
            for line in lines:
                if line.startswith("## Steps"):
                    in_steps = True
                elif line.startswith("## ") and in_steps:
                    in_steps = False
                elif in_steps:
                    if line.startswith("- ") and not line.strip().startswith("-"):
                        result.add_warning("Steps section should use numbered lists for main steps")
                        break

    def _check_tool_assignment(self, prompt_path: str, result: ConventionResult) -> None:
        """Check tool assignment matches file ownership patterns."""
        tool = result.extracted_info.get("tool")
        if not tool:
            return

        # Read file content to check Do NOT Touch section
        try:
            with open(prompt_path, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return

        # Extract Do NOT Touch section
        do_not_touch_match = re.search(r"## Do NOT Touch\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)

        if not do_not_touch_match:
            return

        do_not_touch_content = do_not_touch_match.group(1)

        # Check that files owned by other tools are in Do NOT Touch
        for other_tool, patterns in self.TOOL_OWNERSHIP.items():
            if other_tool == tool or other_tool.startswith(tool):
                continue

            for pattern in patterns:
                # The pattern should be mentioned in Do NOT Touch
                # (This is a soft check - we just warn if major patterns are missing)
                if pattern.endswith("/") and pattern not in do_not_touch_content:
                    # Only warn for high-value directories
                    if pattern in [
                        "src/lattice_lock/cli/",
                        "src/lattice_lock/validator/",
                        "docs/",
                    ]:
                        result.add_warning(
                            f"Consider adding '{pattern}' to Do NOT Touch section "
                            f"(owned by {self.VALID_TOOLS.get(other_tool, other_tool)})"
                        )

    def get_expected_directory(self, phase: int) -> str:
        """
        Get the expected directory name for a phase.

        Args:
            phase: Phase number

        Returns:
            Expected directory name pattern
        """
        # Map phase numbers to directory suffixes
        phase_suffixes = {
            1: "foundation",
            2: "cicd",
            3: "error_handling",
            4: "documentation",
            5: "prompt_automation",
        }

        suffix = phase_suffixes.get(phase, "generic")
        return f"phase{phase}_{suffix}"

    def suggest_filename(
        self, phase: int, epic: int, task: int, tool: str, description: str
    ) -> str:
        """
        Suggest a properly formatted filename.

        Args:
            phase: Phase number
            epic: Epic number
            task: Task number
            tool: Tool identifier
            description: Task description

        Returns:
            Properly formatted filename
        """
        # Clean description for filename
        clean_desc = description.lower()
        clean_desc = re.sub(r"[^a-z0-9\s]", "", clean_desc)
        clean_desc = re.sub(r"\s+", "_", clean_desc.strip())
        clean_desc = clean_desc[:50]  # Limit length

        return f"{phase}.{epic}.{task}_{tool}_{clean_desc}.md"
