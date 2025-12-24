"""
Tests for the Lattice Lock CLI doctor command.

Tests environment health checks.
"""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from lattice_lock.cli.__main__ import cli
from lattice_lock.cli.commands.doctor import (
    CheckResult,
    _check_git,
    _check_ollama,
    _check_python_version,
    _check_required_dependencies,
)


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


class TestDoctorCommand:
    """Tests for the doctor command."""

    def test_doctor_help(self, runner: CliRunner) -> None:
        """Test that doctor --help works."""
        result = runner.invoke(cli, ["doctor", "--help"])

        assert result.exit_code == 0
        assert "Check environment health" in result.output

    def test_doctor_runs_without_error(self, runner: CliRunner) -> None:
        """Test that doctor command runs successfully."""
        result = runner.invoke(cli, ["doctor"])

        # Doctor should run without crashing
        assert "Lattice Lock Environment Health Check" in result.output
        assert "Summary:" in result.output

    def test_doctor_shows_python_version(self, runner: CliRunner) -> None:
        """Test that doctor shows Python version."""
        result = runner.invoke(cli, ["doctor"])

        assert "Python Version" in result.output

    def test_doctor_shows_dependencies(self, runner: CliRunner) -> None:
        """Test that doctor shows dependencies."""
        result = runner.invoke(cli, ["doctor"])

        assert "Dependencies:" in result.output
        assert "click" in result.output

    def test_doctor_shows_environment_variables(self, runner: CliRunner) -> None:
        """Test that doctor shows environment variables section."""
        result = runner.invoke(cli, ["doctor"])

        assert "Environment Variables:" in result.output

    def test_doctor_shows_ai_tools(self, runner: CliRunner) -> None:
        """Test that doctor shows AI tools section."""
        result = runner.invoke(cli, ["doctor"])

        assert "AI Tools:" in result.output


class TestPythonVersionCheck:
    """Tests for Python version check."""

    def test_python_version_passes_on_310_plus(self) -> None:
        """Test that Python 3.10+ passes."""
        result = _check_python_version()

        # We're running on Python 3.10+
        assert result.passed
        assert "Python" in result.message

    def test_python_version_result_format(self) -> None:
        """Test that result has correct format."""
        result = _check_python_version()

        assert isinstance(result, CheckResult)
        assert result.name == "Python Version"
        assert isinstance(result.passed, bool)
        assert isinstance(result.message, str)


class TestDependencyCheck:
    """Tests for dependency checks."""

    def test_required_dependencies_check(self) -> None:
        """Test checking required dependencies."""
        results = _check_required_dependencies()

        assert len(results) > 0
        # All results should be CheckResult
        for r in results:
            assert isinstance(r, CheckResult)

    def test_click_dependency_passes(self) -> None:
        """Test that click dependency check passes."""
        results = _check_required_dependencies()

        click_results = [r for r in results if "click" in r.name.lower()]
        assert len(click_results) == 1
        assert click_results[0].passed

    def test_optional_dependencies_marked(self) -> None:
        """Test that optional dependencies are marked as optional."""
        results = _check_required_dependencies()

        # pytest is optional in our list
        pytest_results = [r for r in results if "pytest" in r.name.lower()]
        if pytest_results:
            assert pytest_results[0].optional


class TestGitCheck:
    """Tests for Git check."""

    def test_git_check_on_system_with_git(self) -> None:
        """Test Git check when Git is installed."""
        result = _check_git()

        assert isinstance(result, CheckResult)
        assert result.name == "Git"
        # Most dev systems have Git
        if result.passed:
            assert "git version" in result.message.lower()

    @patch("shutil.which")
    def test_git_check_when_not_installed(self, mock_which: MagicMock) -> None:
        """Test Git check when Git is not installed."""
        mock_which.return_value = None

        result = _check_git()

        assert not result.passed
        assert "not found" in result.message.lower()


class TestOllamaCheck:
    """Tests for Ollama check."""

    def test_ollama_check_returns_result(self) -> None:
        """Test that Ollama check returns a valid result."""
        result = _check_ollama()

        assert isinstance(result, CheckResult)
        assert result.name == "Ollama"
        assert result.optional

    @patch("shutil.which")
    def test_ollama_not_installed(self, mock_which: MagicMock) -> None:
        """Test Ollama check when not installed."""
        mock_which.return_value = None

        result = _check_ollama()

        assert not result.passed
        assert "not found" in result.message.lower()


class TestDoctorExitCodes:
    """Tests for doctor exit codes."""

    def test_exit_code_success_on_healthy_env(self, runner: CliRunner) -> None:
        """Test exit code 0 when environment is healthy."""
        result = runner.invoke(cli, ["doctor"])

        # On a typical dev machine, required checks should pass
        # If exit code is 0, all required checks passed
        if result.exit_code == 0:
            assert "Environment is healthy" in result.output

    def test_exit_code_indicates_required_checks(self, runner: CliRunner) -> None:
        """Test that exit code reflects required check status."""
        result = runner.invoke(cli, ["doctor"])

        # Exit code should be 0 or 1
        assert result.exit_code in [0, 1]


class TestCheckResultType:
    """Tests for CheckResult named tuple."""

    def test_check_result_creation(self) -> None:
        """Test creating CheckResult."""
        result = CheckResult(
            name="Test",
            passed=True,
            message="Test message",
            optional=False,
        )

        assert result.name == "Test"
        assert result.passed is True
        assert result.message == "Test message"
        assert result.optional is False

    def test_check_result_optional_default(self) -> None:
        """Test CheckResult optional defaults to False."""
        result = CheckResult(
            name="Test",
            passed=True,
            message="Test message",
        )

        assert result.optional is False


class TestDoctorOutput:
    """Tests for doctor output formatting."""

    def test_doctor_shows_summary(self, runner: CliRunner) -> None:
        """Test that doctor shows summary."""
        result = runner.invoke(cli, ["doctor"])

        assert "Summary:" in result.output
        assert "Required:" in result.output
        assert "Optional:" in result.output

    def test_doctor_shows_check_counts(self, runner: CliRunner) -> None:
        """Test that doctor shows check counts."""
        result = runner.invoke(cli, ["doctor"])

        # Should show format like "5/5 checks passed"
        assert "checks passed" in result.output

    def test_doctor_final_status(self, runner: CliRunner) -> None:
        """Test that doctor shows final status."""
        result = runner.invoke(cli, ["doctor"])

        # Should show either healthy or failed message
        assert "Environment is healthy" in result.output or "checks failed" in result.output
