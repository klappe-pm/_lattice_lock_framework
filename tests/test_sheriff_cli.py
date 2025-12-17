import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from lattice_lock_cli.commands.sheriff import sheriff_command
from lattice_lock_sheriff.config import SheriffConfig
from lattice_lock_sheriff.rules import Violation


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_validate_path():
    with patch("lattice_lock_cli.commands.sheriff.validate_path_with_audit") as mock:
        yield mock


@pytest.fixture
def mock_config_from_yaml():
    with patch("lattice_lock_sheriff.config.SheriffConfig.from_yaml") as mock:
        mock.return_value = SheriffConfig()
        yield mock


def test_sheriff_cli_help(runner):
    result = runner.invoke(sheriff_command, ["--help"])
    assert result.exit_code == 0
    assert "Validates Python files" in result.output


def test_sheriff_cli_no_violations(runner, mock_validate_path, mock_config_from_yaml):
    mock_validate_path.return_value = ([], [])
    with runner.isolated_filesystem():
        Path("test.py").touch()
        result = runner.invoke(sheriff_command, ["test.py", "--no-cache"])

    assert result.exit_code == 0
    assert "no violations" in result.output.lower()


def test_sheriff_cli_with_violations(runner, mock_validate_path, mock_config_from_yaml):
    violation = Violation(
        rule_id="TEST_RULE", message="Test violation", line_number=10, filename="test.py"
    )
    mock_validate_path.return_value = ([violation], [])

    with runner.isolated_filesystem():
        Path("test.py").touch()
        result = runner.invoke(sheriff_command, ["test.py", "--no-cache"])

    assert result.exit_code == 1
    assert "1 violations" in result.output
    assert "test.py" in result.output
    assert "TEST_RULE" in result.output
    assert "Test violation" in result.output


def test_sheriff_cli_with_ignored_violations(runner, mock_validate_path, mock_config_from_yaml):
    violation = Violation(
        rule_id="TEST_RULE", message="Ignored violation", line_number=10, filename="test.py"
    )
    mock_validate_path.return_value = ([], [violation])

    with runner.isolated_filesystem():
        Path("test.py").touch()
        result = runner.invoke(sheriff_command, ["test.py", "--no-cache"])

    # With no active violations, exit code should be 0
    assert result.exit_code == 0


def test_sheriff_cli_json_output(runner, mock_validate_path, mock_config_from_yaml):
    violation = Violation(
        rule_id="TEST_RULE", message="Test violation", line_number=10, filename="test.py"
    )
    mock_validate_path.return_value = ([violation], [])

    with runner.isolated_filesystem():
        Path("test.py").touch()
        result = runner.invoke(sheriff_command, ["test.py", "--format", "json", "--no-cache"])

    assert result.exit_code == 1  # JSON output should still exit with 1 if violations found

    data = json.loads(result.output)
    assert data["count"] == 1
    assert data["violations"][0]["rule_id"] == "TEST_RULE"
    assert data["violations"][0]["message"] == "Test violation"


def test_sheriff_cli_path_not_found(runner):
    result = runner.invoke(sheriff_command, ["non_existent.py"])
    assert result.exit_code == 1
    assert "Path 'non_existent.py' does not exist" in result.output


def test_sheriff_cli_config_loading(runner, mock_validate_path, mock_config_from_yaml):
    mock_validate_path.return_value = ([], [])
    with runner.isolated_filesystem():
        Path("test.py").touch()
        Path("my_config.yaml").touch()
        result = runner.invoke(
            sheriff_command, ["test.py", "--lattice", "my_config.yaml", "--no-cache"]
        )

    mock_config_from_yaml.assert_called_with("my_config.yaml")
    assert result.exit_code == 0
