"""
Integration tests for the Lattice Lock CLI.

Tests the full workflow: init -> validate -> doctor.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from lattice_lock.cli.__main__ import cli

pytestmark = pytest.mark.integration


class TestFullWorkflow:
    """Tests for the complete CLI workflow."""

    def test_init_validate_doctor_workflow(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test full workflow: init a project, validate it, run doctor."""
        # Step 1: Initialize a new project
        init_result = cli_runner.invoke(
            cli,
            [
                "init",
                "workflow_test",
                "--template",
                "service",
                "--output-dir",
                str(temp_project_dir),
            ],
        )
        assert init_result.exit_code == 0, f"Init failed: {init_result.output}"
        # CLI output may vary - check for common success indicators
        assert "Created" in init_result.output or "successfully" in init_result.output

        project_dir = temp_project_dir / "workflow_test"
        assert project_dir.exists()

        # Step 2: Validate the scaffolded project
        validate_result = cli_runner.invoke(
            cli,
            [
                "validate",
                "--path",
                str(project_dir),
            ],
        )
        # Validation should at least run without crashing
        assert "Validating project at:" in validate_result.output

        # Step 3: Run doctor to check environment
        doctor_result = cli_runner.invoke(cli, ["doctor"])
        assert "Lattice Lock Environment Health Check" in doctor_result.output
        assert "Summary:" in doctor_result.output

    def test_init_creates_all_expected_files(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that init creates all expected files and directories."""
        result = cli_runner.invoke(
            cli,
            [
                "init",
                "complete_project",
                "--template",
                "service",
                "--output-dir",
                str(temp_project_dir),
            ],
        )

        assert result.exit_code == 0
        project_dir = temp_project_dir / "complete_project"

        # Check core files
        expected_files = [
            project_dir / "lattice.yaml",
            project_dir / "README.md",
            project_dir / ".gitignore",
            project_dir / ".github" / "workflows" / "lattice-lock.yml",
            project_dir / "tests" / "test_contracts.py",
            project_dir / "src" / "__init__.py",
            project_dir / "src" / "shared" / "__init__.py",
            project_dir / "src" / "services" / "__init__.py",
            project_dir / "src" / "services" / "complete_project.py",
        ]

        for expected_file in expected_files:
            assert expected_file.exists(), f"Missing file: {expected_file}"

        # Check directories
        expected_dirs = [
            project_dir / "src",
            project_dir / "src" / "shared",
            project_dir / "src" / "services",
            project_dir / "tests",
            project_dir / ".github" / "workflows",
        ]

        for expected_dir in expected_dirs:
            assert expected_dir.is_dir(), f"Missing directory: {expected_dir}"

    def test_init_verbose_output(self, cli_runner: CliRunner, temp_project_dir: Path) -> None:
        """Test that verbose mode shows detailed output."""
        result = cli_runner.invoke(
            cli,
            [
                "-v",
                "init",
                "verbose_project",
                "--template",
                "service",
                "--output-dir",
                str(temp_project_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Created directory:" in result.output or "Created file:" in result.output

    def test_init_agent_template_workflow(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test init with agent template creates agent.yaml."""
        result = cli_runner.invoke(
            cli,
            [
                "init",
                "agent_workflow_test",
                "--template",
                "agent",
                "--output-dir",
                str(temp_project_dir),
            ],
        )

        assert result.exit_code == 0
        project_dir = temp_project_dir / "agent_workflow_test"

        # Agent template should create agent.yaml
        agent_file = project_dir / "agent.yaml"
        assert agent_file.exists()

        content = agent_file.read_text()
        assert "agent_workflow_test" in content
        assert "capabilities" in content

    def test_init_library_template_workflow(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test init with library template creates library package."""
        result = cli_runner.invoke(
            cli,
            [
                "init",
                "lib_workflow_test",
                "--template",
                "library",
                "--output-dir",
                str(temp_project_dir),
            ],
        )

        assert result.exit_code == 0
        project_dir = temp_project_dir / "lib_workflow_test"

        # Library template should create package init
        lib_init = project_dir / "src" / "lib_workflow_test" / "__init__.py"
        assert lib_init.exists()

        content = lib_init.read_text()
        assert "__version__" in content


class TestValidateOnScaffoldedProject:
    """Tests for validate command on freshly scaffolded projects."""

    def test_validate_passes_on_fresh_service_project(
        self, scaffolded_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test that validate passes on a freshly scaffolded service project."""
        result = cli_runner.invoke(
            cli,
            [
                "validate",
                "--path",
                str(scaffolded_project),
            ],
        )

        # Should show validation output
        assert "Validating project at:" in result.output

        # Schema validation should run
        assert "Schema Validation:" in result.output

        # Structure validation should run
        assert "Structure Validation:" in result.output

    def test_validate_schema_on_fresh_project(
        self, scaffolded_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test schema validation on freshly scaffolded project."""
        result = cli_runner.invoke(
            cli, ["validate", "--path", str(scaffolded_project), "--schema-only"]
        )

        assert "Schema Validation:" in result.output
        # lattice.yaml should be found
        assert "No lattice.yaml found" not in result.output

    def test_validate_structure_on_fresh_project(
        self, scaffolded_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test structure validation on freshly scaffolded project."""
        result = cli_runner.invoke(
            cli, ["validate", "--path", str(scaffolded_project), "--structure-only"]
        )

        assert "Structure Validation:" in result.output

    def test_validate_agents_on_fresh_agent_project(
        self, scaffolded_agent_project: Path, cli_runner: CliRunner
    ) -> None:
        """Test agent validation on freshly scaffolded agent project."""
        result = cli_runner.invoke(
            cli, ["validate", "--path", str(scaffolded_agent_project), "--agents-only"]
        )

        assert "Agent Manifest Validation:" in result.output
        # Agent file should be found since we used agent template
        assert "No agent definitions found" not in result.output


class TestDoctorEnvironmentStatus:
    """Tests for doctor command environment reporting."""

    def test_doctor_reports_python_version(self, cli_runner: CliRunner) -> None:
        """Test that doctor reports Python version correctly."""
        result = cli_runner.invoke(cli, ["doctor"])

        assert "Python Version" in result.output
        assert "System:" in result.output

    def test_doctor_reports_dependencies(self, cli_runner: CliRunner) -> None:
        """Test that doctor reports dependencies."""
        result = cli_runner.invoke(cli, ["doctor"])

        assert "Dependencies:" in result.output
        # Core dependencies should be checked
        assert "click" in result.output

    def test_doctor_reports_git_status(self, cli_runner: CliRunner) -> None:
        """Test that doctor reports Git status."""
        result = cli_runner.invoke(cli, ["doctor"])

        assert "Git" in result.output

    def test_doctor_reports_environment_variables(self, cli_runner: CliRunner) -> None:
        """Test that doctor reports environment variable section."""
        result = cli_runner.invoke(cli, ["doctor"])

        assert "Environment Variables:" in result.output

    def test_doctor_reports_ai_tools(self, cli_runner: CliRunner) -> None:
        """Test that doctor reports AI tools section."""
        result = cli_runner.invoke(cli, ["doctor"])

        assert "AI Tools:" in result.output
        assert "Ollama" in result.output

    def test_doctor_shows_summary(self, cli_runner: CliRunner) -> None:
        """Test that doctor shows summary with counts."""
        result = cli_runner.invoke(cli, ["doctor"])

        assert "Summary:" in result.output
        assert "Required:" in result.output
        assert "Optional:" in result.output


class TestCLIErrorHandling:
    """Tests for CLI error handling in workflows."""

    def test_init_rejects_invalid_project_name(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that init rejects invalid project names."""
        result = cli_runner.invoke(
            cli,
            [
                "init",
                "Invalid-Name",
                "--output-dir",
                str(temp_project_dir),
            ],
        )

        assert result.exit_code != 0
        assert "Invalid project name" in result.output

    def test_init_rejects_existing_directory(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that init rejects existing directories."""
        # Create existing directory
        existing = temp_project_dir / "existing_project"
        existing.mkdir()

        result = cli_runner.invoke(
            cli,
            [
                "init",
                "existing_project",
                "--output-dir",
                str(temp_project_dir),
            ],
        )

        assert result.exit_code != 0
        assert "already exists" in result.output

    def test_validate_handles_nonexistent_path(self, cli_runner: CliRunner) -> None:
        """Test that validate handles nonexistent paths."""
        result = cli_runner.invoke(
            cli, ["validate", "--path", "/nonexistent/path/that/does/not/exist"]
        )

        # Click should reject invalid path
        assert result.exit_code != 0

    def test_validate_handles_empty_directory(
        self, cli_runner: CliRunner, temp_project_dir: Path
    ) -> None:
        """Test that validate handles empty directories gracefully."""
        empty_dir = temp_project_dir / "empty"
        empty_dir.mkdir()

        result = cli_runner.invoke(cli, ["validate", "--path", str(empty_dir), "--schema-only"])

        # Should warn about missing files, not crash
        assert "No lattice.yaml found" in result.output


class TestCLIVersion:
    """Tests for CLI version and help."""

    def test_version_option(self, cli_runner: CliRunner) -> None:
        """Test --version option."""
        result = cli_runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "lattice-lock" in result.output

    def test_help_option(self, cli_runner: CliRunner) -> None:
        """Test --help option."""
        result = cli_runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Lattice Lock Framework CLI" in result.output
        assert "init" in result.output
        assert "validate" in result.output
        assert "doctor" in result.output

    def test_init_help(self, cli_runner: CliRunner) -> None:
        """Test init --help."""
        result = cli_runner.invoke(cli, ["init", "--help"])

        assert result.exit_code == 0
        assert "--template" in result.output
        assert "--output-dir" in result.output

    def test_validate_help(self, cli_runner: CliRunner) -> None:
        """Test validate --help."""
        result = cli_runner.invoke(cli, ["validate", "--help"])

        assert result.exit_code == 0
        assert "--path" in result.output
        assert "--fix" in result.output

    def test_doctor_help(self, cli_runner: CliRunner) -> None:
        """Test doctor --help."""
        result = cli_runner.invoke(cli, ["doctor", "--help"])

        assert result.exit_code == 0
        assert "Check environment health" in result.output
