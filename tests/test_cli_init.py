"""
Tests for the Lattice Lock CLI init command.

Tests project scaffolding, validation, and template rendering.
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from lattice_lock_cli.__main__ import cli
from lattice_lock_cli.commands.init import create_project_structure, validate_project_name


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for tests."""
    return tmp_path


class TestProjectNameValidation:
    """Tests for project name validation."""

    def test_valid_snake_case_names(self) -> None:
        """Test that valid snake_case names are accepted."""
        valid_names = [
            "my_project",
            "myproject",
            "project123",
            "my_project_v2",
            "a",
            "abc_def_ghi",
        ]
        for name in valid_names:
            assert validate_project_name(name), f"'{name}' should be valid"

    def test_invalid_names_rejected(self) -> None:
        """Test that invalid names are rejected."""
        invalid_names = [
            "MyProject",  # PascalCase
            "my-project",  # kebab-case
            "my project",  # spaces
            "123project",  # starts with number
            "_private",  # starts with underscore
            "project!",  # special characters
            "PROJECT",  # uppercase
            "",  # empty
        ]
        for name in invalid_names:
            assert not validate_project_name(name), f"'{name}' should be invalid"


class TestInitCommand:
    """Tests for the init command."""

    def test_successful_project_creation(self, runner: CliRunner, temp_dir: Path) -> None:
        """Test that a project is created successfully."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_test_project",
                "--output-dir",
                str(temp_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Project created successfully!" in result.output

        # Check directory structure
        project_dir = temp_dir / "my_test_project"
        assert project_dir.exists()
        assert (project_dir / "lattice.yaml").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / ".gitignore").exists()
        assert (project_dir / "src" / "shared").exists()
        assert (project_dir / "src" / "services").exists()
        assert (project_dir / "tests" / "test_contracts.py").exists()
        assert (project_dir / ".github" / "workflows" / "lattice-lock.yml").exists()

    def test_invalid_project_name_rejected(self, runner: CliRunner, temp_dir: Path) -> None:
        """Test that invalid project names are rejected."""
        result = runner.invoke(
            cli,
            [
                "init",
                "Invalid-Name",
                "--output-dir",
                str(temp_dir),
            ],
        )

        assert result.exit_code != 0
        assert "Invalid project name" in result.output

    def test_existing_directory_rejected(self, runner: CliRunner, temp_dir: Path) -> None:
        """Test that existing directories are not overwritten."""
        # Create existing directory
        existing_dir = temp_dir / "existing_project"
        existing_dir.mkdir()

        result = runner.invoke(
            cli,
            [
                "init",
                "existing_project",
                "--output-dir",
                str(temp_dir),
            ],
        )

        assert result.exit_code != 0
        assert "already exists" in result.output

    def test_service_template_creates_service_file(self, runner: CliRunner, temp_dir: Path) -> None:
        """Test that service template creates the service scaffold."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_service",
                "--template",
                "service",
                "--output-dir",
                str(temp_dir),
            ],
        )

        assert result.exit_code == 0
        service_file = temp_dir / "my_service" / "src" / "services" / "my_service.py"
        assert service_file.exists()

        content = service_file.read_text()
        assert "class MyserviceService" in content or "MyService" in content

    def test_agent_template_creates_agent_file(self, runner: CliRunner, temp_dir: Path) -> None:
        """Test that agent template creates the agent definition."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_agent",
                "--template",
                "agent",
                "--output-dir",
                str(temp_dir),
            ],
        )

        assert result.exit_code == 0
        agent_file = temp_dir / "my_agent" / "agent.yaml"
        assert agent_file.exists()

        content = agent_file.read_text()
        assert "my_agent" in content
        assert "capabilities" in content

    def test_library_template_creates_library_file(self, runner: CliRunner, temp_dir: Path) -> None:
        """Test that library template creates the library init file."""
        result = runner.invoke(
            cli,
            [
                "init",
                "my_library",
                "--template",
                "library",
                "--output-dir",
                str(temp_dir),
            ],
        )

        assert result.exit_code == 0
        lib_file = temp_dir / "my_library" / "src" / "my_library" / "__init__.py"
        assert lib_file.exists()

        content = lib_file.read_text()
        assert "__version__" in content

    def test_default_template_is_service(self, runner: CliRunner, temp_dir: Path) -> None:
        """Test that the default template is 'service'."""
        result = runner.invoke(
            cli,
            [
                "init",
                "default_project",
                "--output-dir",
                str(temp_dir),
            ],
        )

        assert result.exit_code == 0
        # Service template creates a service file
        service_file = temp_dir / "default_project" / "src" / "services" / "default_project.py"
        assert service_file.exists()

    def test_verbose_output(self, runner: CliRunner, temp_dir: Path) -> None:
        """Test that verbose flag produces detailed output."""
        result = runner.invoke(
            cli,
            [
                "-v",
                "init",
                "verbose_project",
                "--output-dir",
                str(temp_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Created directory:" in result.output or "Created file:" in result.output

    def test_help_shows_options(self, runner: CliRunner) -> None:
        """Test that init --help shows all options."""
        result = runner.invoke(cli, ["init", "--help"])

        assert result.exit_code == 0
        assert "--template" in result.output
        assert "--output-dir" in result.output
        assert "agent" in result.output
        assert "service" in result.output
        assert "library" in result.output


class TestProjectStructure:
    """Tests for the project structure creation function."""

    def test_creates_all_required_directories(self, temp_dir: Path) -> None:
        """Test that all required directories are created."""
        create_project_structure(
            project_name="test_project",
            project_type="service",
            output_dir=temp_dir,
        )

        project_dir = temp_dir / "test_project"
        assert (project_dir / "src" / "shared").is_dir()
        assert (project_dir / "src" / "services").is_dir()
        assert (project_dir / "tests").is_dir()
        assert (project_dir / ".github" / "workflows").is_dir()

    def test_creates_all_required_files(self, temp_dir: Path) -> None:
        """Test that all required files are created."""
        created_files = create_project_structure(
            project_name="test_project",
            project_type="service",
            output_dir=temp_dir,
        )

        assert len(created_files) > 0
        project_dir = temp_dir / "test_project"
        assert (project_dir / "lattice.yaml").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / ".gitignore").exists()
        assert (project_dir / "tests" / "test_contracts.py").exists()

    def test_lattice_yaml_contains_project_name(self, temp_dir: Path) -> None:
        """Test that lattice.yaml contains the project name."""
        create_project_structure(
            project_name="my_special_project",
            project_type="service",
            output_dir=temp_dir,
        )

        lattice_file = temp_dir / "my_special_project" / "lattice.yaml"
        content = lattice_file.read_text()
        assert "my_special_project" in content
