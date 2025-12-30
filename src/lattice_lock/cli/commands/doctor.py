"""
Lattice Lock CLI Doctor Command

Checks environment health for Lattice Lock projects.
"""

import os
import shutil
import subprocess
import sys
from importlib.metadata import version
from typing import NamedTuple

import click


class CheckResult(NamedTuple):
    """Result of a health check."""

    name: str
    passed: bool
    message: str
    optional: bool = False


def _check_python_version() -> CheckResult:
    """Check Python version is >= 3.10."""
    major, minor = sys.version_info[:2]
    version_str = f"{major}.{minor}.{sys.version_info[2]}"

    if major >= 3 and minor >= 10:
        return CheckResult(
            name="Python Version",
            passed=True,
            message=f"Python {version_str} (>= 3.10 required)",
        )
    else:
        return CheckResult(
            name="Python Version",
            passed=False,
            message=f"Python {version_str} is below minimum 3.10",
        )


def _check_required_dependencies() -> list[CheckResult]:
    """Check that required dependencies are installed."""
    results = []

    # Core dependencies that lattice-lock needs
    required_deps = [
        ("click", "CLI framework"),
        ("jinja2", "Template engine"),
        ("pyyaml", "YAML parser"),
    ]

    # Optional dependencies
    optional_deps = [
        ("pytest", "Testing framework"),
        ("ruff", "Linting"),
        ("mypy", "Type checking"),
    ]

    for dep_name, description in required_deps:
        try:
            dep_version = version(dep_name)
            results.append(
                CheckResult(
                    name=f"Dependency: {dep_name}",
                    passed=True,
                    message=f"{description} v{dep_version}",
                )
            )
        except Exception:
            results.append(
                CheckResult(
                    name=f"Dependency: {dep_name}",
                    passed=False,
                    message=f"{description} - NOT INSTALLED",
                )
            )

    for dep_name, description in optional_deps:
        try:
            dep_version = version(dep_name)
            results.append(
                CheckResult(
                    name=f"Dependency: {dep_name}",
                    passed=True,
                    message=f"{description} v{dep_version}",
                    optional=True,
                )
            )
        except Exception:
            results.append(
                CheckResult(
                    name=f"Dependency: {dep_name}",
                    passed=False,
                    message=f"{description} - not installed (optional)",
                    optional=True,
                )
            )

    return results


def _check_environment_variables() -> list[CheckResult]:
    """Check that recommended environment variables are configured."""
    results = []

    # Check for common environment variables
    env_checks = [
        ("LATTICE_LOCK_CONFIG", "Lattice Lock configuration path", True),
        ("ORCHESTRATOR_STRATEGY", "AI orchestration strategy", True),
        ("LOG_LEVEL", "Logging verbosity", True),
        ("OPENAI_API_KEY", "OpenAI API key", True),
        ("ANTHROPIC_API_KEY", "Anthropic API key", True),
    ]

    for env_var, description, optional in env_checks:
        value = os.environ.get(env_var)
        if value:
            # Mask sensitive values
            if "KEY" in env_var or "SECRET" in env_var or "TOKEN" in env_var:
                display_value = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
            else:
                display_value = value[:30] + "..." if len(value) > 30 else value
            results.append(
                CheckResult(
                    name=f"Env: {env_var}",
                    passed=True,
                    message=f"{description} = {display_value}",
                    optional=optional,
                )
            )
        else:
            results.append(
                CheckResult(
                    name=f"Env: {env_var}",
                    passed=False,
                    message=f"{description} - not set",
                    optional=optional,
                )
            )

    return results


def _check_ollama() -> CheckResult:
    """Check if Ollama is available (optional)."""
    ollama_path = shutil.which("ollama")

    if not ollama_path:
        return CheckResult(
            name="Ollama",
            passed=False,
            message="Ollama CLI not found in PATH (optional)",
            optional=True,
        )

    # Try to check if Ollama server is running
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            models = [
                line.split()[0] for line in result.stdout.strip().split("\n")[1:] if line.strip()
            ]
            model_count = len(models)
            return CheckResult(
                name="Ollama",
                passed=True,
                message=f"Ollama running with {model_count} model(s) available",
                optional=True,
            )
        else:
            return CheckResult(
                name="Ollama",
                passed=False,
                message="Ollama installed but server not running",
                optional=True,
            )
    except subprocess.TimeoutExpired:
        return CheckResult(
            name="Ollama",
            passed=False,
            message="Ollama installed but server timed out",
            optional=True,
        )
    except Exception as e:
        return CheckResult(
            name="Ollama",
            passed=False,
            message=f"Ollama check failed: {str(e)}",
            optional=True,
        )


def _check_git() -> CheckResult:
    """Check if Git is available."""
    git_path = shutil.which("git")

    if not git_path:
        return CheckResult(
            name="Git",
            passed=False,
            message="Git not found in PATH",
        )

    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version_str = result.stdout.strip()
            return CheckResult(
                name="Git",
                passed=True,
                message=version_str,
            )
    except subprocess.TimeoutExpired:
        return CheckResult(
            name="Git",
            passed=False,
            message="Git version check timed out",
        )
    except Exception as e:
        return CheckResult(
            name="Git",
            passed=False,
            message=f"Git version check failed: {str(e)}",
        )

    return CheckResult(
        name="Git",
        passed=False,
        message="Git found but version check failed",
    )


def _print_result(result: CheckResult) -> None:
    """Print a check result with colorful output."""
    if result.passed:
        icon = click.style("✓", fg="green")
        name_style = "green" if not result.optional else "cyan"
    else:
        if result.optional:
            icon = click.style("○", fg="yellow")
            name_style = "yellow"
        else:
            icon = click.style("✗", fg="red")
            name_style = "red"

    click.echo(f"  {icon} {click.style(result.name, fg=name_style)}: {result.message}")


@click.command()
@click.pass_context
def doctor_command(ctx: click.Context) -> None:
    """Check environment health for Lattice Lock.

    Verifies Python version, dependencies, environment variables,
    and optional tools like Ollama.
    """
    _verbose = ctx.obj.get("verbose", False) if ctx.obj else False  # Reserved for verbose output

    click.echo(click.style("Lattice Lock Environment Health Check", bold=True))
    click.echo("=" * 50)
    click.echo()

    all_results: list[CheckResult] = []

    # Python version
    click.echo(click.style("System:", bold=True))
    result = _check_python_version()
    all_results.append(result)
    _print_result(result)

    # Git
    result = _check_git()
    all_results.append(result)
    _print_result(result)
    click.echo()

    # Dependencies
    click.echo(click.style("Dependencies:", bold=True))
    for result in _check_required_dependencies():
        all_results.append(result)
        _print_result(result)
    click.echo()

    # Environment variables
    click.echo(click.style("Environment Variables:", bold=True))
    for result in _check_environment_variables():
        all_results.append(result)
        _print_result(result)
    click.echo()

    # Ollama (optional)
    click.echo(click.style("AI Tools:", bold=True))
    result = _check_ollama()
    all_results.append(result)
    _print_result(result)
    click.echo()

    # Summary
    required_checks = [r for r in all_results if not r.optional]
    optional_checks = [r for r in all_results if r.optional]

    required_passed = sum(1 for r in required_checks if r.passed)
    required_total = len(required_checks)
    optional_passed = sum(1 for r in optional_checks if r.passed)
    optional_total = len(optional_checks)

    click.echo("=" * 50)
    click.echo(click.style("Summary:", bold=True))
    click.echo(f"  Required: {required_passed}/{required_total} checks passed")
    click.echo(f"  Optional: {optional_passed}/{optional_total} checks passed")
    click.echo()

    all_required_passed = all(r.passed for r in required_checks)

    if all_required_passed:
        click.echo(click.style("✓ Environment is healthy!", fg="green", bold=True))
        sys.exit(0)
    else:
        click.echo(
            click.style(
                "✗ Some required checks failed. Please fix the issues above.", fg="red", bold=True
            )
        )
        sys.exit(1)
