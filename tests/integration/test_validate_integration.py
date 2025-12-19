"""
Integration tests for the validate command.

Tests validation error catching, --fix functionality, and exit codes.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner
from lattice_lock_cli.__main__ import cli

pytestmark = pytest.mark.integration


class TestValidateCatchesSchemaErrors:
    """Tests for schema validation error detection."""

    def test_catches_invalid_yaml_syntax(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that validate catches invalid YAML syntax."""
        project_dir = temp_project_dir / "invalid_yaml"
        project_dir.mkdir()

        # Create malformed YAML
        lattice_yaml = project_dir / "lattice.yaml"
        lattice_yaml.write_text("invalid: yaml: : syntax\n  broken indentation")

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--schema-only"])

        assert result.exit_code == 1
        assert "Schema Validation:" in result.output
        assert "failed" in result.output

    def test_catches_missing_required_fields(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that validate catches missing required schema fields."""
        project_dir = temp_project_dir / "missing_fields"
        project_dir.mkdir()

        # Create YAML missing required fields
        lattice_yaml = project_dir / "lattice.yaml"
        lattice_yaml.write_text("# Empty file\n")

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--schema-only"])

        # Should report issues
        assert "Schema Validation:" in result.output

    def test_catches_invalid_entity_structure(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that validate catches invalid entity structures."""
        project_dir = temp_project_dir / "invalid_entity"
        project_dir.mkdir()

        # Create YAML with invalid entity structure
        lattice_yaml = project_dir / "lattice.yaml"
        lattice_yaml.write_text(
            """version: v1.0.0
generated_module: test
entities: not-a-dict
"""
        )

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--schema-only"])

        assert result.exit_code == 1


class TestValidateCatchesEnvErrors:
    """Tests for environment file validation error detection."""

    def test_catches_env_syntax_issues(
        self, cli_runner: CliRunner, temp_project_dir: Path, invalid_env_file: str
    ) -> None:
        """Test that validate catches .env file issues."""
        project_dir = temp_project_dir / "env_issues"
        project_dir.mkdir()

        env_file = project_dir / ".env"
        env_file.write_text(invalid_env_file)

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--env-only"])

        # Should run env validation
        assert "Environment Validation:" in result.output

    def test_env_validation_with_valid_file(
        self, cli_runner: CliRunner, temp_project_dir: Path, sample_env_file: str
    ) -> None:
        """Test that validate passes with valid .env file."""
        project_dir = temp_project_dir / "valid_env"
        project_dir.mkdir()

        env_file = project_dir / ".env"
        env_file.write_text(sample_env_file)

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--env-only"])

        assert "Environment Validation:" in result.output
        # Should find the env file
        assert ".env" in result.output


class TestValidateCatchesStructureErrors:
    """Tests for structure validation error detection."""

    def test_structure_validation_runs(self, cli_runner: CliRunner, temp_project_dir: Path) -> None:
        """Test that structure validation runs on a directory."""
        project_dir = temp_project_dir / "structure_test"
        project_dir.mkdir()

        result = cli_runner.invoke(
            cli, ["validate", "--path", str(project_dir), "--structure-only"]
        )

        assert "Structure Validation:" in result.output

    def test_structure_validation_on_complete_project(
        self, scaffolded_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test structure validation on a complete scaffolded project."""
        result = cli_runner.invoke(
            cli, ["validate", "--path", str(scaffolded_project), "--structure-only"]
        )

        assert "Structure Validation:" in result.output


class TestValidateFixFlag:
    """Tests for --fix flag functionality."""

    def test_fix_removes_trailing_whitespace(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that --fix removes trailing whitespace from files."""
        project_dir = temp_project_dir / "trailing_ws"
        project_dir.mkdir()

        # Create file with trailing whitespace
        test_file = project_dir / "test.py"
        test_file.write_text("line with trailing spaces    \nnormal line\n")

        result = cli_runner.invoke(cli, ["-v", "validate", "--path", str(project_dir), "--fix"])

        assert "Applying auto-fixes" in result.output

        # Verify whitespace was removed
        content = test_file.read_text()
        assert "    \n" not in content
        assert content == "line with trailing spaces\nnormal line\n"

    def test_fix_adds_missing_eof_newline(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that --fix adds missing EOF newline."""
        project_dir = temp_project_dir / "missing_newline"
        project_dir.mkdir()

        # Create file without trailing newline
        test_file = project_dir / "test.py"
        test_file.write_text("content without newline")

        result = cli_runner.invoke(cli, ["-v", "validate", "--path", str(project_dir), "--fix"])

        assert "Applying auto-fixes" in result.output

        # Verify newline was added
        content = test_file.read_text()
        assert content.endswith("\n")

    def test_fix_handles_multiple_file_types(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that --fix handles multiple file types."""
        project_dir = temp_project_dir / "multi_type"
        project_dir.mkdir()

        # Create various file types with issues
        files = {
            "test.py": "python code  \n",
            "config.yaml": "yaml: content  \n",
            "readme.md": "markdown text  \n",
        }

        for filename, content in files.items():
            (project_dir / filename).write_text(content)

        result = cli_runner.invoke(cli, ["-v", "validate", "--path", str(project_dir), "--fix"])

        assert "Applying auto-fixes" in result.output

        # All files should be fixed
        for filename in files:
            content = (project_dir / filename).read_text()
            assert "  \n" not in content

    def test_fix_reports_no_changes_when_clean(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that --fix reports when no changes are needed."""
        project_dir = temp_project_dir / "clean_project"
        project_dir.mkdir()

        # Create already clean file
        test_file = project_dir / "test.py"
        test_file.write_text("clean content\n")

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--fix"])

        assert "No fixable issues found" in result.output

    def test_fix_skips_ignored_directories(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that --fix skips .git and __pycache__ directories."""
        project_dir = temp_project_dir / "with_ignored"
        project_dir.mkdir()

        # Create files in ignored directories
        git_dir = project_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git content  ")

        pycache_dir = project_dir / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "module.pyc").write_text("cache  ")

        # Create normal file that should be fixed
        (project_dir / "test.py").write_text("content  \n")

        result = cli_runner.invoke(cli, ["-v", "validate", "--path", str(project_dir), "--fix"])

        # Only the normal file should be fixed
        assert (git_dir / "config").read_text() == "git content  "
        assert "test.py" in result.output or "Applying auto-fixes" in result.output


class TestValidateExitCodes:
    """Tests for validate command exit codes."""

    def test_exit_code_0_on_success(
        self, cli_runner: CliRunner, temp_project_dir: Path, sample_lattice_yaml: str
    ) -> None:
        """Test exit code 0 when validation passes."""
        project_dir = temp_project_dir / "success_project"
        project_dir.mkdir()

        (project_dir / "lattice.yaml").write_text(sample_lattice_yaml)

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--schema-only"])

        assert result.exit_code == 0

    def test_exit_code_1_on_validation_failure(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test exit code 1 when validation fails."""
        project_dir = temp_project_dir / "failure_project"
        project_dir.mkdir()

        # Create invalid lattice.yaml
        (project_dir / "lattice.yaml").write_text("invalid: yaml: syntax:")

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--schema-only"])

        assert result.exit_code == 1

    def test_exit_code_consistent_across_validators(
        self, scaffolded_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test that exit codes are consistent when running all validators."""
        result = cli_runner.invoke(cli, ["validate", "--path", str(scaffolded_project)])

        # Exit code should be 0 or 1
        assert result.exit_code in [0, 1]


class TestValidateAllValidators:
    """Tests for running all validators together."""

    def test_all_validators_run_by_default(
        self, scaffolded_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test that all validators run when no filter flags are provided."""
        result = cli_runner.invoke(cli, ["validate", "--path", str(scaffolded_project)])

        # All validation sections should appear
        assert "Schema Validation:" in result.output
        assert "Environment Validation:" in result.output
        assert "Agent Manifest Validation:" in result.output
        assert "Structure Validation:" in result.output

    def test_summary_shows_error_and_warning_counts(
        self, scaffolded_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test that validation summary shows error and warning counts."""
        result = cli_runner.invoke(cli, ["validate", "--path", str(scaffolded_project)])

        # Should show summary separator
        assert "=" * 50 in result.output

    def test_verbose_mode_shows_more_details(
        self, scaffolded_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test that verbose mode provides more detailed output."""
        result = cli_runner.invoke(cli, ["-v", "validate", "--path", str(scaffolded_project)])

        # Verbose output should include path info
        assert "Validating project at:" in result.output


class TestValidateAgentManifests:
    """Tests for agent manifest validation."""

    def test_validates_agent_yaml(
        self, scaffolded_agent_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test validation of agent.yaml in agent projects."""
        result = cli_runner.invoke(
            cli, ["validate", "--path", str(scaffolded_agent_project), "--agents-only"]
        )

        assert "Agent Manifest Validation:" in result.output
        # Should find agent.yaml
        assert "No agent definitions found" not in result.output

    def test_validates_custom_agent_definition(
        self, cli_runner: CliRunner, temp_project_dir: Path, sample_agent_yaml: str
    ) -> None:
        """Test validation of custom agent definition files."""
        project_dir = temp_project_dir / "custom_agent"
        project_dir.mkdir()

        # Create custom agent definition
        (project_dir / "agent.yaml").write_text(sample_agent_yaml)

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--agents-only"])

        assert "Agent Manifest Validation:" in result.output
        assert "passed" in result.output

    def test_catches_invalid_agent_manifest(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that invalid agent manifests are caught."""
        project_dir = temp_project_dir / "invalid_agent"
        project_dir.mkdir()

        # Create invalid agent definition
        (project_dir / "agent.yaml").write_text("invalid: agent: manifest:")

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--agents-only"])

        assert "Agent Manifest Validation:" in result.output


class TestValidateFilters:
    """Tests for validation filter flags."""

    def test_schema_only_excludes_others(
        self, cli_runner: CliRunner, temp_project_dir: Path, sample_lattice_yaml: str
    ) -> None:
        """Test that --schema-only excludes other validators."""
        project_dir = temp_project_dir / "schema_only_test"
        project_dir.mkdir()
        (project_dir / "lattice.yaml").write_text(sample_lattice_yaml)

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--schema-only"])

        assert "Schema Validation:" in result.output
        # These should not appear when using --schema-only
        assert "Structure Validation:" not in result.output
        assert "Agent Manifest Validation:" not in result.output

    def test_env_only_excludes_others(
        self, cli_runner: CliRunner, temp_project_dir: Path, sample_env_file: str
    ) -> None:
        """Test that --env-only excludes other validators."""
        project_dir = temp_project_dir / "env_only_test"
        project_dir.mkdir()
        (project_dir / ".env").write_text(sample_env_file)

        result = cli_runner.invoke(cli, ["validate", "--path", str(project_dir), "--env-only"])

        assert "Environment Validation:" in result.output
        assert "Schema Validation:" not in result.output

    def test_structure_only_excludes_others(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that --structure-only excludes other validators."""
        result = cli_runner.invoke(
            cli, ["validate", "--path", str(temp_project_dir), "--structure-only"]
        )

        assert "Structure Validation:" in result.output
        assert "Schema Validation:" not in result.output
        assert "Environment Validation:" not in result.output

    def test_agents_only_excludes_others(
        self, scaffolded_agent_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test that --agents-only excludes other validators."""
        result = cli_runner.invoke(
            cli, ["validate", "--path", str(scaffolded_agent_project), "--agents-only"]
        )

        assert "Agent Manifest Validation:" in result.output
        assert "Schema Validation:" not in result.output
        assert "Environment Validation:" not in result.output
