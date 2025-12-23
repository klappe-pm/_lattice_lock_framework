from unittest.mock import patch

import pytest
from click.testing import CliRunner

from lattice_lock.cli.__main__ import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_generator():
    with patch("lattice_lock.cli.commands.gauntlet.GauntletGenerator") as mock:
        yield mock


@pytest.fixture
def mock_pytest():
    with patch("lattice_lock.cli.commands.gauntlet.pytest") as mock:
        mock.main.return_value = 0
        yield mock


def test_generate_mode(runner, mock_generator):
    """Test that --generate flag triggers generation."""
    result = runner.invoke(cli, ["test", "--generate"])
    assert result.exit_code == 0
    assert "Generating tests" in result.output
    mock_generator.assert_called_once()
    mock_generator.return_value.generate.assert_called_once()


def test_run_mode_default(runner, mock_pytest):
    """Test that default behavior is to run tests."""
    with patch("pathlib.Path.exists", return_value=True):
        result = runner.invoke(cli, ["test"])
        assert result.exit_code == 0
        assert "Running tests" in result.output
        mock_pytest.main.assert_called_once()
        args = mock_pytest.main.call_args[0][0]
        assert "tests/gauntlet" in args


def test_run_mode_explicit(runner, mock_pytest):
    """Test that --run flag triggers execution."""
    with patch("pathlib.Path.exists", return_value=True):
        result = runner.invoke(cli, ["test", "--run"])
        assert result.exit_code == 0
        mock_pytest.main.assert_called_once()


def test_generate_and_run(runner, mock_generator, mock_pytest):
    """Test that --generate and --run together do both."""
    with patch("pathlib.Path.exists", return_value=True):
        result = runner.invoke(cli, ["test", "--generate", "--run"])
        assert result.exit_code == 0
        mock_generator.return_value.generate.assert_called_once()
        mock_pytest.main.assert_called_once()


def test_generate_only_implicit(runner, mock_generator, mock_pytest):
    """Test that --generate without --run implies NO run."""
    result = runner.invoke(cli, ["test", "--generate"])
    assert result.exit_code == 0
    mock_generator.return_value.generate.assert_called_once()
    mock_pytest.main.assert_not_called()


def test_coverage_flag(runner, mock_pytest):
    """Test that --coverage passes correct flags to pytest."""
    with patch("pathlib.Path.exists", return_value=True):
        result = runner.invoke(cli, ["test", "--coverage"])
        assert result.exit_code == 0
        args = mock_pytest.main.call_args[0][0]
        assert "--cov" in args
        assert "--cov-report=term-missing" in args


def test_missing_test_dir(runner):
    """Test error when test directory is missing for run."""
    with patch("pathlib.Path.exists", return_value=False):
        result = runner.invoke(cli, ["test"])
        assert result.exit_code == 1
        assert "Test directory tests/gauntlet does not exist" in result.output
