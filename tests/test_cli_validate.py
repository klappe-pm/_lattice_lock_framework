"""
Tests for the Lattice Lock CLI validate command.

Tests the validate command with various options and scenarios.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner
from lattice_lock_cli.__main__ import cli


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary project with lattice.yaml."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create a valid lattice.yaml
    lattice_yaml = project_dir / "lattice.yaml"
    lattice_yaml.write_text(
        """
version: v1.0.0
generated_module: test_module
entities:
  User:
    fields:
      id:
        type: uuid
        primary_key: true
      name:
        type: str
"""
    )

    return project_dir


@pytest.fixture
def temp_project_with_env(tmp_path: Path) -> Path:
    """Create a temporary project with .env file."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create a .env file
    env_file = project_dir / ".env"
    env_file.write_text(
        """
ORCHESTRATOR_STRATEGY=round_robin
LOG_LEVEL=DEBUG
"""
    )

    return project_dir


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_help(self, runner: CliRunner) -> None:
        """Test that validate --help shows options."""
        result = runner.invoke(cli, ["validate", "--help"])

        assert result.exit_code == 0
        assert "--path" in result.output
        assert "--fix" in result.output
        assert "--schema-only" in result.output
        assert "--env-only" in result.output
        assert "--agents-only" in result.output
        assert "--structure-only" in result.output

    def test_validate_with_valid_schema(self, runner: CliRunner, temp_project: Path) -> None:
        """Test validate with a valid lattice.yaml."""
        result = runner.invoke(cli, ["validate", "--path", str(temp_project), "--schema-only"])

        assert "Schema Validation:" in result.output
        assert "passed" in result.output

    def test_validate_schema_only_flag(self, runner: CliRunner, temp_project: Path) -> None:
        """Test that --schema-only only runs schema validation."""
        result = runner.invoke(cli, ["validate", "--path", str(temp_project), "--schema-only"])

        assert "Schema Validation:" in result.output
        # Should not run other validations
        assert (
            "Environment Validation:" not in result.output or "No .env file found" in result.output
        )

    def test_validate_env_only_flag(self, runner: CliRunner, temp_project_with_env: Path) -> None:
        """Test that --env-only only runs environment validation."""
        result = runner.invoke(
            cli, ["validate", "--path", str(temp_project_with_env), "--env-only"]
        )

        assert "Environment Validation:" in result.output
        assert "Schema Validation:" not in result.output

    def test_validate_structure_only_flag(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --structure-only only runs structure validation."""
        result = runner.invoke(cli, ["validate", "--path", str(tmp_path), "--structure-only"])

        assert "Structure Validation:" in result.output
        assert "Schema Validation:" not in result.output

    def test_validate_nonexistent_path(self, runner: CliRunner) -> None:
        """Test validate with nonexistent path."""
        result = runner.invoke(cli, ["validate", "--path", "/nonexistent/path"])

        # Click should report invalid path
        assert result.exit_code != 0

    def test_validate_no_lattice_yaml(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test validate on project without lattice.yaml."""
        result = runner.invoke(cli, ["validate", "--path", str(tmp_path), "--schema-only"])

        assert "No lattice.yaml found" in result.output

    def test_validate_default_path(self, runner: CliRunner) -> None:
        """Test validate uses current directory by default."""
        result = runner.invoke(cli, ["validate", "--schema-only"])

        # Should run without path error
        assert "Schema Validation:" in result.output


class TestValidateFixFlag:
    """Tests for the --fix flag."""

    def test_fix_trailing_whitespace(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --fix removes trailing whitespace."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line with trailing    \nnormal line\n")

        result = runner.invoke(cli, ["-v", "validate", "--path", str(tmp_path), "--fix"])

        assert "Applying auto-fixes" in result.output
        content = test_file.read_text()
        assert "trailing    " not in content
        assert content == "line with trailing\nnormal line\n"

    def test_fix_missing_eof_newline(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that --fix adds missing EOF newline."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line without newline")

        result = runner.invoke(cli, ["-v", "validate", "--path", str(tmp_path), "--fix"])

        assert "Applying auto-fixes" in result.output
        content = test_file.read_text()
        assert content.endswith("\n")

    def test_fix_no_changes_needed(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test --fix when no fixes are needed."""
        test_file = tmp_path / "test.py"
        test_file.write_text("clean file\n")

        result = runner.invoke(cli, ["validate", "--path", str(tmp_path), "--fix"])

        assert "No fixable issues found" in result.output


class TestValidateExitCodes:
    """Tests for validate exit codes."""

    def test_exit_code_success(self, runner: CliRunner, temp_project: Path) -> None:
        """Test exit code 0 on success."""
        result = runner.invoke(cli, ["validate", "--path", str(temp_project), "--schema-only"])

        assert result.exit_code == 0

    def test_exit_code_failure_invalid_schema(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test exit code 1 on failure."""
        # Create invalid lattice.yaml
        lattice_yaml = tmp_path / "lattice.yaml"
        lattice_yaml.write_text("invalid: yaml: syntax")

        result = runner.invoke(cli, ["validate", "--path", str(tmp_path), "--schema-only"])

        assert result.exit_code == 1


class TestValidateVerbose:
    """Tests for verbose output."""

    def test_verbose_shows_warnings(self, runner: CliRunner, temp_project_with_env: Path) -> None:
        """Test that verbose mode shows warnings."""
        # Create env with warning-triggering content
        env_file = temp_project_with_env / ".env"
        env_file.write_text(
            """
ORCHESTRATOR_STRATEGY=round_robin
LOG_LEVEL=DEBUG
some_lower_case=value
"""
        )

        result = runner.invoke(
            cli, ["-v", "validate", "--path", str(temp_project_with_env), "--env-only"]
        )

        # Verbose should show more details
        assert "Environment Validation:" in result.output


class TestValidateAgents:
    """Tests for agent manifest validation."""

    def test_validate_agents_only(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test --agents-only flag."""
        # Create an agent definition
        agent_dir = tmp_path / "agent_definitions" / "test"
        agent_dir.mkdir(parents=True)

        agent_file = agent_dir / "test_agent_definition.yaml"
        agent_file.write_text(
            """
agent:
  identity:
    name: test_agent
    version: v1.0.0
    description: A test agent
    role: tester
directive:
  primary_goal: Test things
responsibilities:
  - name: testing
    description: Run tests
scope:
  can_access:
    - /tests
  cannot_access:
    - /secrets
"""
        )

        result = runner.invoke(cli, ["validate", "--path", str(tmp_path), "--agents-only"])

        assert "Agent Manifest Validation:" in result.output
        assert "passed" in result.output
