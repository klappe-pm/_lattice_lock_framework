"""
Lattice Lock CLI Validate Command

Runs validators on a Lattice Lock project.
"""

import os
import sys
from pathlib import Path

import click

from lattice_lock_validator import (
    ValidationResult,
    validate_agent_manifest,
    validate_env_file,
    validate_lattice_schema,
    validate_repository_structure,
)


def _print_result(name: str, result: ValidationResult, verbose: bool = False) -> None:
    """Print validation result with colorful output."""
    if result.valid and not result.warnings:
        click.echo(click.style(f"  ✓ {name}: ", fg="green") + "passed")
    elif result.valid and result.warnings:
        click.echo(click.style(f"  ⚠ {name}: ", fg="yellow") + "passed with warnings")
        if verbose:
            for warning in result.warnings:
                msg = warning.message
                if warning.line_number:
                    msg += f" (line {warning.line_number})"
                click.echo(click.style(f"    ⚠ {msg}", fg="yellow"))
    else:
        click.echo(click.style(f"  ✗ {name}: ", fg="red") + "failed")
        for error in result.errors:
            msg = error.message
            if error.line_number:
                msg += f" (line {error.line_number})"
            click.echo(click.style(f"    ✗ {msg}", fg="red"))
        if verbose:
            for warning in result.warnings:
                msg = warning.message
                if warning.line_number:
                    msg += f" (line {warning.line_number})"
                click.echo(click.style(f"    ⚠ {msg}", fg="yellow"))


def _auto_fix_file(file_path: Path, verbose: bool = False) -> int:
    """Apply auto-fixes to a file. Returns number of fixes applied."""
    fixes = 0

    try:
        content = file_path.read_text()
        original = content

        # Fix trailing whitespace
        lines = content.split("\n")
        new_lines = [line.rstrip() for line in lines]
        if lines != new_lines:
            fixes += sum(1 for i in range(len(lines)) if lines[i] != new_lines[i])
            content = "\n".join(new_lines)

        # Fix missing newline at EOF
        if content and not content.endswith("\n"):
            content += "\n"
            fixes += 1

        if content != original:
            file_path.write_text(content)
            if verbose:
                click.echo(click.style(f"    Fixed: {file_path}", fg="cyan"))

        return fixes
    except Exception:
        return 0


def _apply_fixes(path: Path, verbose: bool = False) -> int:
    """Apply auto-fixes to all files in path. Returns total fixes applied."""
    total_fixes = 0

    # Common file extensions to fix
    fix_extensions = {".py", ".yaml", ".yml", ".md", ".txt", ".json", ".toml"}

    if path.is_file():
        if path.suffix in fix_extensions:
            total_fixes += _auto_fix_file(path, verbose)
    elif path.is_dir():
        for root, dirs, files in os.walk(path):
            # Skip common non-source directories
            dirs[:] = [
                d for d in dirs if d not in {".git", "__pycache__", "venv", "node_modules", ".venv"}
            ]

            for filename in files:
                file_path = Path(root) / filename
                if file_path.suffix in fix_extensions:
                    total_fixes += _auto_fix_file(file_path, verbose)

    return total_fixes


def _find_files(path: Path, patterns: list[str]) -> list[Path]:
    """Find files matching patterns in path."""
    files = []
    for pattern in patterns:
        if path.is_dir():
            files.extend(path.glob(f"**/{pattern}"))
        elif path.match(pattern):
            files.append(path)
    return files


@click.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    default=".",
    help="Path to project directory (default: current directory)",
)
@click.option(
    "--fix",
    is_flag=True,
    help="Auto-fix issues where possible (trailing whitespace, missing EOF newline)",
)
@click.option(
    "--schema-only",
    is_flag=True,
    help="Run only schema validation (lattice.yaml)",
)
@click.option(
    "--env-only",
    is_flag=True,
    help="Run only environment file validation (.env)",
)
@click.option(
    "--agents-only",
    is_flag=True,
    help="Run only agent manifest validation",
)
@click.option(
    "--structure-only",
    is_flag=True,
    help="Run only repository structure validation",
)
@click.pass_context
def validate_command(
    ctx: click.Context,
    path: Path,
    fix: bool,
    schema_only: bool,
    env_only: bool,
    agents_only: bool,
    structure_only: bool,
) -> None:
    """Validate a Lattice Lock project.

    Runs all validators by default, or specific validators when flags are provided.
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    # Determine which validators to run
    run_all = not any([schema_only, env_only, agents_only, structure_only])
    run_schema = run_all or schema_only
    run_env = run_all or env_only
    run_agents = run_all or agents_only
    run_structure = run_all or structure_only

    click.echo(f"Validating project at: {path}")
    click.echo()

    # Apply fixes first if requested
    if fix:
        click.echo("Applying auto-fixes...")
        fixes_applied = _apply_fixes(path, verbose)
        if fixes_applied > 0:
            click.echo(click.style(f"  Applied {fixes_applied} fix(es)", fg="cyan"))
        else:
            click.echo("  No fixable issues found")
        click.echo()

    all_results: list[ValidationResult] = []

    # Schema validation
    if run_schema:
        click.echo("Schema Validation:")
        lattice_files = _find_files(path, ["lattice.yaml", "lattice.yml"])
        if not lattice_files:
            click.echo(click.style("  ⚠ No lattice.yaml found", fg="yellow"))
        else:
            for lattice_file in lattice_files:
                result = validate_lattice_schema(str(lattice_file))
                all_results.append(result)
                _print_result(str(lattice_file.relative_to(path)), result, verbose)
        click.echo()

    # Environment validation
    if run_env:
        click.echo("Environment Validation:")
        env_files = _find_files(path, [".env", ".env.example", ".env.template"])
        if not env_files:
            click.echo(click.style("  ⚠ No .env file found", fg="yellow"))
        else:
            for env_file in env_files:
                result = validate_env_file(str(env_file))
                all_results.append(result)
                _print_result(str(env_file.relative_to(path)), result, verbose)
        click.echo()

    # Agent manifest validation
    if run_agents:
        click.echo("Agent Manifest Validation:")
        agent_files = _find_files(path, ["*_definition.yaml", "*_definition.yml", "agent.yaml"])
        if not agent_files:
            click.echo(click.style("  ⚠ No agent definitions found", fg="yellow"))
        else:
            for agent_file in agent_files:
                result = validate_agent_manifest(str(agent_file))
                all_results.append(result)
                _print_result(str(agent_file.relative_to(path)), result, verbose)
        click.echo()

    # Structure validation
    if run_structure:
        click.echo("Structure Validation:")
        result = validate_repository_structure(str(path))
        all_results.append(result)
        _print_result("Repository structure", result, verbose)
        click.echo()

    # Summary
    total_errors = sum(len(r.errors) for r in all_results)
    total_warnings = sum(len(r.warnings) for r in all_results)
    all_valid = all(r.valid for r in all_results) if all_results else True

    click.echo("=" * 50)
    if all_valid and total_warnings == 0:
        click.echo(click.style("✓ All validations passed!", fg="green", bold=True))
        sys.exit(0)
    elif all_valid:
        click.echo(
            click.style(
                f"⚠ Validation passed with {total_warnings} warning(s)", fg="yellow", bold=True
            )
        )
        sys.exit(0)
    else:
        click.echo(
            click.style(
                f"✗ Validation failed: {total_errors} error(s), {total_warnings} warning(s)",
                fg="red",
                bold=True,
            )
        )
        sys.exit(1)
