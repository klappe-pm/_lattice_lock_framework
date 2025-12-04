import os
import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path
from lattice_lock_cli.commands.sheriff import sheriff_command
from lattice_lock_sheriff.sheriff import Violation

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
        yield mock

def test_sheriff_cli_help(runner):
    result = runner.invoke(sheriff_command, ["--help"])
    assert result.exit_code == 0
    assert "Validates Python files" in result.output

def test_sheriff_cli_no_violations(runner, mock_validate_path, mock_config_from_yaml):
    mock_validate_path.return_value = ([], [])
    with runner.isolated_filesystem():
        Path("test.py").touch()
        result = runner.invoke(sheriff_command, ["test.py"])
        
    assert result.exit_code == 0
    assert "Sheriff found no violations" in result.output

def test_sheriff_cli_with_violations(runner, mock_validate_path, mock_config_from_yaml):
    violation = Violation(
        file=Path("test.py"),
        line=10,
        column=5,
        message="Test violation",
        rule="TEST_RULE",
        code="import bad"
    )
    mock_validate_path.return_value = ([violation], [])
    
    with runner.isolated_filesystem():
        Path("test.py").touch()
        result = runner.invoke(sheriff_command, ["test.py"])
        
    assert result.exit_code == 1
    assert "Sheriff found 1 violations" in result.output
    assert "test.py" in result.output
    assert "10:5" in result.output
    assert "TEST_RULE" in result.output
    assert "Test violation" in result.output

def test_sheriff_cli_with_ignored_violations(runner, mock_validate_path, mock_config_from_yaml):
    violation = Violation(
        file=Path("test.py"),
        line=10,
        column=5,
        message="Ignored violation",
        rule="TEST_RULE",
        code="import bad # lattice:ignore"
    )
    mock_validate_path.return_value = ([], [violation])
    
    with runner.isolated_filesystem():
        Path("test.py").touch()
        result = runner.invoke(sheriff_command, ["test.py"])
        
    assert result.exit_code == 0
    assert "Sheriff audited 1 ignored violations" in result.output
    assert "Ignored violation (IGNORED)" in result.output
    assert "Summary: 0 violations found (1 ignored)" in result.output

def test_sheriff_cli_json_output(runner, mock_validate_path, mock_config_from_yaml):
    violation = Violation(
        file=Path("test.py"),
        line=10,
        column=5,
        message="Test violation",
        rule="TEST_RULE",
        code="import bad"
    )
    ignored_violation = Violation(
        file=Path("test.py"),
        line=12,
        column=5,
        message="Ignored violation",
        rule="TEST_RULE",
        code="import bad # lattice:ignore"
    )
    mock_validate_path.return_value = ([violation], [ignored_violation])
    
    with runner.isolated_filesystem():
        Path("test.py").touch()
        result = runner.invoke(sheriff_command, ["test.py", "--json"])
        
    assert result.exit_code == 1 # JSON output should still exit with 1 if violations found
    
    data = json.loads(result.output)
    assert data["count"] == 1
    assert data["ignored_count"] == 1
    assert data["violations"][0]["rule"] == "TEST_RULE"
    assert data["ignored_violations"][0]["message"] == "Ignored violation"

def test_sheriff_cli_path_not_found(runner):
    result = runner.invoke(sheriff_command, ["non_existent.py"])
    assert result.exit_code == 1
    assert "Path 'non_existent.py' does not exist" in result.output

def test_sheriff_cli_config_loading(runner, mock_validate_path, mock_config_from_yaml):
    mock_validate_path.return_value = ([], [])
    with runner.isolated_filesystem():
        Path("test.py").touch()
        Path("my_config.yaml").touch()
        result = runner.invoke(sheriff_command, ["test.py", "--lattice", "my_config.yaml"])
        
    mock_config_from_yaml.assert_called_with("my_config.yaml")
    assert result.exit_code == 0
