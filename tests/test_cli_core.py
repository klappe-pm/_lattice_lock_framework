"""
Tests for the Lattice Lock CLI core functionality.

Tests the CLI entry point, version, help, and verbose flag.
"""

import pytest
from click.testing import CliRunner

from lattice_lock.cli import __version__
from lattice_lock.cli.__main__ import cli, main


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


class TestCLICore:
    """Tests for CLI core functionality."""

    def test_cli_loads_without_error(self, runner: CliRunner) -> None:
        """Test that CLI loads without any import errors."""
        # CLI with --help should load and work
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert result.exception is None

    def test_cli_help(self, runner: CliRunner) -> None:
        """Test that --help shows help text."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Lattice Lock Framework CLI" in result.output
        assert "--version" in result.output
        assert "--verbose" in result.output

    def test_cli_version(self, runner: CliRunner) -> None:
        """Test that --version shows correct version."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output
        assert "lattice-lock" in result.output

    def test_verbose_flag_passed_to_context(self, runner: CliRunner) -> None:
        """Test that verbose flag is passed to context via init command."""
        # Use verbose flag with init --help to verify verbose works
        result = runner.invoke(cli, ["-v", "init", "--help"])
        assert result.exit_code == 0

        # Verify verbose flag is documented
        result = runner.invoke(cli, ["--help"])
        assert "-v, --verbose" in result.output

    def test_verbose_short_flag(self, runner: CliRunner) -> None:
        """Test that -v short flag works for verbose."""
        result = runner.invoke(cli, ["-v", "--help"])
        assert result.exit_code == 0

    def test_main_function_exists(self) -> None:
        """Test that main() entry point function exists and is callable."""
        assert callable(main)

    def test_cli_shows_available_commands(self, runner: CliRunner) -> None:
        """Test that CLI help shows available commands."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "init" in result.output


class TestCLIContext:
    """Tests for CLI context handling."""

    def test_context_via_verbose_init(self, runner: CliRunner, tmp_path) -> None:
        """Test that context works by using verbose with init."""
        # When verbose is passed, init should show more detail
        result = runner.invoke(
            cli,
            [
                "-v",
                "init",
                "test_ctx_project",
                "--output-dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        # Verbose mode shows "Created" messages
        assert "Created" in result.output
