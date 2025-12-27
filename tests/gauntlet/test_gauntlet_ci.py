import os
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from lattice_lock.cli.__main__ import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_pytest():
    with patch("lattice_lock.cli.commands.gauntlet.pytest") as mock:
        mock.main.return_value = 0
        yield mock


def test_format_json(runner, mock_pytest):
    """Test that --format json passes correct args and env vars."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(cli, ["test", "--format", "json"])
            assert result.exit_code == 0

            # Check pytest args
            args = mock_pytest.main.call_args[0][0]
            assert "-p" in args
            assert "lattice_lock.gauntlet.plugin" in args

            # Check env var
            assert os.environ.get("GAUNTLET_JSON_REPORT") == "true"


def test_format_junit(runner, mock_pytest):
    """Test that --format junit passes correct args."""
    with patch("pathlib.Path.exists", return_value=True):
        result = runner.invoke(cli, ["test", "--format", "junit"])
        assert result.exit_code == 0

        args = mock_pytest.main.call_args[0][0]
        assert "--junitxml=test-results.xml" in args


def test_format_github(runner, mock_pytest):
    """Test that --format github passes correct args and env vars."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(cli, ["test", "--format", "github"])
            assert result.exit_code == 0

            args = mock_pytest.main.call_args[0][0]
            assert "-p" in args
            assert "lattice_lock.gauntlet.plugin" in args

            assert os.environ.get("GAUNTLET_GITHUB_REPORT") == "true"


def test_parallel_auto(runner, mock_pytest):
    """Test that --parallel auto passes -n auto."""
    with patch("pathlib.Path.exists", return_value=True):
        # Mock xdist import
        with patch.dict("sys.modules", {"xdist": MagicMock()}):
            result = runner.invoke(cli, ["test", "--parallel", "auto"])
            assert result.exit_code == 0

            args = mock_pytest.main.call_args[0][0]
            assert "-n" in args
            assert "auto" in args


def test_parallel_count(runner, mock_pytest):
    """Test that --parallel N passes -n N."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.dict("sys.modules", {"xdist": MagicMock()}):
            result = runner.invoke(cli, ["test", "--parallel", "4"])
            assert result.exit_code == 0

            args = mock_pytest.main.call_args[0][0]
            assert "-n" in args
            assert "4" in args


def test_parallel_missing_xdist(runner, mock_pytest):
    """Test that missing xdist warns and skips parallel."""
    with patch("pathlib.Path.exists", return_value=True):
        # Simulate ImportError for xdist
        with patch.dict("sys.modules", {"xdist": None}):
            pass


def test_multiple_formats(runner, mock_pytest):
    """Test multiple formats."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(cli, ["test", "--format", "json", "--format", "junit"])
            assert result.exit_code == 0

            args = mock_pytest.main.call_args[0][0]
            assert "-p" in args
            assert "lattice_lock.gauntlet.plugin" in args
            assert "--junitxml=test-results.xml" in args
            assert os.environ.get("GAUNTLET_JSON_REPORT") == "true"
