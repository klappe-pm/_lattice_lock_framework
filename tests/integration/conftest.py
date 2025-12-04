"""
Fixtures for integration tests.

Provides shared fixtures for CLI integration testing.
"""

import pytest
from pathlib import Path
from click.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click test runner for CLI invocation.

    Returns:
        CliRunner: Click test runner instance.
    """
    return CliRunner()


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test projects.

    Args:
        tmp_path: Pytest's temporary path fixture.

    Returns:
        Path: Temporary directory path.
    """
    project_dir = tmp_path / "test_projects"
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


@pytest.fixture
def sample_lattice_yaml() -> str:
    """Provide valid lattice.yaml content.

    Returns:
        str: Valid lattice.yaml content.
    """
    return """version: v1.0.0
generated_module: test_module
entities:
  User:
    fields:
      id:
        type: uuid
        primary_key: true
      name:
        type: str
        max_length: 255
      email:
        type: str
        max_length: 255
"""


@pytest.fixture
def sample_env_file() -> str:
    """Provide valid .env content.

    Returns:
        str: Valid .env file content.
    """
    return """# Lattice Lock Configuration
ORCHESTRATOR_STRATEGY=round_robin
LOG_LEVEL=INFO
MAX_RETRIES=3
"""


@pytest.fixture
def sample_agent_yaml() -> str:
    """Provide valid agent.yaml content.

    Returns:
        str: Valid agent.yaml content.
    """
    return """agent:
  identity:
    name: test_agent
    version: v1.0.0
    description: A test agent for integration testing
    role: tester
directive:
  primary_goal: Execute tests and validate functionality
responsibilities:
  - name: testing
    description: Run automated tests
  - name: validation
    description: Validate test results
scope:
  can_access:
    - /tests
    - /src
  cannot_access:
    - /secrets
    - /.env
capabilities:
  - test_execution
  - result_reporting
"""


@pytest.fixture
def invalid_lattice_yaml() -> str:
    """Provide invalid lattice.yaml content for error testing.

    Returns:
        str: Invalid lattice.yaml content.
    """
    return """version: invalid-version-format
# Missing required fields
entities: not-a-dict
"""


@pytest.fixture
def invalid_env_file() -> str:
    """Provide .env content with issues for warning testing.

    Returns:
        str: .env content that triggers warnings.
    """
    return """# Non-standard variable naming
lower_case_var=value
DUPLICATE_VAR=first
DUPLICATE_VAR=second
no_value_var=
"""


@pytest.fixture
def scaffolded_project(cli_runner: CliRunner, temp_project_dir: Path) -> Path:
    """Create a scaffolded project for integration testing.

    Args:
        cli_runner: Click test runner.
        temp_project_dir: Temporary directory for projects.

    Returns:
        Path: Path to the scaffolded project.
    """
    from lattice_lock_cli.__main__ import cli

    result = cli_runner.invoke(cli, [
        "init", "integration_test_project",
        "--template", "service",
        "--output-dir", str(temp_project_dir),
    ])

    assert result.exit_code == 0, f"Failed to scaffold project: {result.output}"

    return temp_project_dir / "integration_test_project"


@pytest.fixture
def scaffolded_agent_project(cli_runner: CliRunner, temp_project_dir: Path) -> Path:
    """Create a scaffolded agent project for integration testing.

    Args:
        cli_runner: Click test runner.
        temp_project_dir: Temporary directory for projects.

    Returns:
        Path: Path to the scaffolded agent project.
    """
    from lattice_lock_cli.__main__ import cli

    result = cli_runner.invoke(cli, [
        "init", "agent_test_project",
        "--template", "agent",
        "--output-dir", str(temp_project_dir),
    ])

    assert result.exit_code == 0, f"Failed to scaffold agent project: {result.output}"

    return temp_project_dir / "agent_test_project"
