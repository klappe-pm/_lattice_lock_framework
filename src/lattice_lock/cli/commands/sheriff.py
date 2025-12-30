"""Sheriff CLI command for AST-based validation with CI integration.

Provides:
- Multiple output formats (text, json, github, junit)
- File-based caching for performance
- CI/CD pipeline integration
- Audit trail for ignored violations
"""

import json
import os
import sys
from pathlib import Path

import click
from lattice_lock.sheriff.cache import SheriffCache, get_config_hash
from lattice_lock.sheriff.config import SheriffConfig
from lattice_lock.sheriff.formatters import OutputFormatter, get_formatter
from lattice_lock.sheriff.rules import Violation
from lattice_lock.sheriff.sheriff import validate_file_with_audit, validate_path_with_audit


@click.command("sheriff")
@click.argument("path", type=str)
@click.option(
    "--lattice",
    type=click.Path(file_okay=True, dir_okay=False, readable=True, path_type=Path),
    default="lattice.yaml",
    help="Path to the lattice.yaml configuration file. Auto-detected if not provided.",
)
@click.option(
    "--fix",
    is_flag=True,
    help="Attempt to auto-correct violations where possible (not implemented yet).",
)
@click.option(
    "--ignore",
    multiple=True,
    help="Glob patterns for files or directories to ignore (e.g., '**/ignore_me.py', '*/temp_dir/*').",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "github", "junit"], case_sensitive=False),
    default="text",
    help="Output format. 'text' for human-readable, 'json' for machine-readable, "
    "'github' for GitHub Actions annotations, 'junit' for JUnit XML reports.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    hidden=True,
    help="[DEPRECATED] Use --format json instead. Output results in JSON format.",
)
@click.option(
    "--cache/--no-cache",
    "use_cache",
    default=True,
    help="Enable/disable file caching. Cache skips unchanged files based on content hash.",
)
@click.option(
    "--cache-dir",
    type=click.Path(path_type=Path),
    default=".sheriff_cache",
    help="Directory to store cache files.",
)
@click.option("--clear-cache", is_flag=True, help="Clear the cache before running validation.")
@click.pass_context
def sheriff_command(
    ctx: click.Context,
    path: str,
    lattice: Path,
    fix: bool,
    ignore: list[str],
    output_format: str,
    json_output: bool,
    use_cache: bool,
    cache_dir: Path,
    clear_cache: bool,
) -> None:
    """
    Validates Python files for import discipline and type hint compliance using Sheriff.

    Supports multiple output formats for CI integration:

    \b
    --format text    Human-readable terminal output (default)
    --format json    Machine-readable JSON output
    --format github  GitHub Actions annotations
    \b
    --format junit   JUnit XML reports for CI tools

    Caching is enabled by default to improve CI performance. Use --no-cache to
    force a full scan, or --clear-cache to reset the cache before scanning.
    """
    # Handle deprecated --json flag
    if json_output:
        output_format = "json"

    if fix:
        click.echo(click.style("Warning: --fix is not yet implemented.", fg="yellow"), err=True)

    # Manual existence check for the 'path' argument
    path_obj = Path(path)
    if not path_obj.exists():
        _handle_error(output_format, f"Path '{path}' does not exist.")
        sys.exit(1)

    actual_lattice_path = lattice

    # If --lattice was not explicitly provided, try to auto-detect
    if lattice == Path("lattice.yaml"):  # This indicates the default value
        current_dir = Path.cwd()
        found_lattice = None
        for parent in [current_dir] + list(current_dir.parents):
            potential_lattice = parent / "lattice.yaml"
            if potential_lattice.exists():
                found_lattice = potential_lattice
                break

        if found_lattice:
            actual_lattice_path = found_lattice
        else:
            if not (
                output_format == "json" or output_format == "junit" or output_format == "github"
            ):  # Only warn if not machine-readable output
                click.echo(
                    click.style(
                        "Warning: lattice.yaml not found. Using default Sheriff configuration.",
                        fg="yellow",
                    ),
                    err=True,
                )
            # SheriffConfig.from_yaml will handle the non-existent file by returning a default config

    # Load Sheriff configuration
    try:
        sheriff_config = SheriffConfig.from_yaml(str(actual_lattice_path))
    except Exception as e:
        _handle_error(output_format, f"Failed to load lattice.yaml: {e}")
        sys.exit(1)

    # Initialize cache
    cache: SheriffCache | None = None
    if use_cache:
        config_hash = get_config_hash(sheriff_config)
        cache = SheriffCache(cache_dir=cache_dir, config_hash=config_hash)

        if clear_cache:
            cache.clear()
        else:
            cache.load()

    # Run validation with caching and audit
    violations, ignored_violations = _validate_with_cache(
        path_obj, sheriff_config, list(ignore), cache
    )

    # Save cache if used
    if cache:
        cache.save()

    # Output results based on format
    formatter: OutputFormatter = get_formatter(output_format)

    if output_format == "json":
        # JsonFormatter should handle both violations and ignored violations
        all_results = {
            "violations": [v.__dict__ for v in violations],
            "ignored_violations": [v.__dict__ for v in ignored_violations],
            "count": len(violations),
            "ignored_count": len(ignored_violations),
            "target": str(path_obj),
            "success": len(violations) == 0,
        }
        click.echo(json.dumps(all_results, indent=2))
    elif output_format == "text":
        click.echo(formatter.format(violations, path_obj))
        if ignored_violations:
            click.echo(
                click.style(
                    f"\nSheriff audited {len(ignored_violations)} ignored violations in {path_obj}:",
                    fg="yellow",
                    bold=True,
                ),
                err=True,
            )
            for v in ignored_violations:
                click.echo(
                    f"  {click.style(str(v.filename), fg='cyan')}:"
                    f"{click.style(str(v.line_number), fg='yellow')} - "
                    f"{click.style(v.rule_id, fg='magenta')} - {v.message} (IGNORED)",
                    err=True,
                )
    else:  # github and junit output formats
        click.echo(formatter.format(violations, path_obj))
        # For these formats, ignored violations are usually not part of the primary output
        # but could be logged separately if an audit log is desired.
        if ignored_violations:
            click.echo(
                click.style(
                    f"Note: {len(ignored_violations)} ignored violations were found but not included in "
                    f"the {output_format} output format.",
                    fg="yellow",
                ),
                err=True,
            )

    exit_code = formatter.get_exit_code(violations)
    sys.exit(exit_code)


def _validate_with_cache(
    path: Path, config: SheriffConfig, ignore_patterns: list[str], cache: SheriffCache | None
) -> tuple[list[Violation], list[Violation]]:
    """Validate files with caching support.

    Args:
        path: Path to validate (file or directory)
        config: Sheriff configuration
        ignore_patterns: Glob patterns to ignore
        cache: Optional cache instance

    Returns:
        Tuple of (violations, ignored_violations)
    """
    if cache is None:
        # No cache, use standard validation
        return validate_path_with_audit(path, config, ignore_patterns)

    violations: list[Violation] = []
    ignored_violations: list[Violation] = []

    if path.is_file():
        v, iv = _validate_file_with_cache(
            path, config, cache
        )  # ignore_patterns handled by ast_visitor
        violations.extend(v)
        ignored_violations.extend(iv)
    elif path.is_dir():
        # Walk directory and validate each file with caching
        for root, _, files in os.walk(path):
            current_dir = Path(root)

            # Apply directory-level ignore patterns
            ignored_by_dir = False
            for pattern in ignore_patterns:
                relative_dir = current_dir.relative_to(path) if current_dir != path else Path(".")
                if relative_dir.match(pattern):
                    ignored_by_dir = True
                    break
            if ignored_by_dir:
                continue

            for file in files:
                file_path = current_dir / file
                if file_path.suffix == ".py":
                    # Apply file-level ignore patterns
                    ignored_by_file = False
                    for pattern in ignore_patterns:
                        if file_path.match(pattern):
                            ignored_by_file = True
                            break
                    if ignored_by_file:
                        continue

                    v, iv = _validate_file_with_cache(
                        file_path, config, cache
                    )  # ignore_patterns handled by ast_visitor
                    violations.extend(v)
                    ignored_violations.extend(iv)

    return violations, ignored_violations


def _validate_file_with_cache(
    file_path: Path, config: SheriffConfig, cache: SheriffCache
) -> tuple[list[Violation], list[Violation]]:
    """Validate a single file with caching.

    Args:
        file_path: Path to the Python file
        config: Sheriff configuration
        cache: Cache instance

    Returns:
        Tuple of (violations, ignored_violations)
    """
    # Check cache first
    cached_data = cache.get_cached_violations(file_path)
    if cached_data is not None:
        # Reconstruct Violation objects from cached data
        violations = []
        ignored_violations = []
        for v_data in cached_data:
            # The Violation from rules.py needs filename
            violation = Violation(
                rule_id=v_data["rule_id"],
                message=v_data["message"],
                line_number=v_data["line_number"],
                filename=Path(v_data["filename"]),  # Now always expect filename
            )
            if v_data.get("ignored", False):
                ignored_violations.append(violation)
            else:
                violations.append(violation)
        return violations, ignored_violations

    # Not cached, validate and cache result
    # The SheriffVisitor (via validate_file_with_audit) handles ignore_patterns internally
    violations, ignored_violations = validate_file_with_audit(file_path, config)

    # Cache the results (include ignored flag)
    violations_data = []
    for v in violations:
        violations_data.append(
            {
                "rule_id": v.rule_id,
                "message": v.message,
                "line_number": v.line_number,
                "filename": str(v.filename),
                "ignored": False,
            }
        )
    for v in ignored_violations:
        violations_data.append(
            {
                "rule_id": v.rule_id,
                "message": v.message,
                "line_number": v.line_number,
                "filename": str(v.filename),
                "ignored": True,
            }
        )
    cache.set_violations(file_path, violations_data)

    return violations, ignored_violations


def _handle_error(output_format: str, message: str) -> None:
    """Output an error message in the appropriate format.

    Args:
        output_format: The output format being used
        message: The error message
    """
    formatter: OutputFormatter = get_formatter(output_format)
    click.echo(formatter.format_error(message), err=True)  # Send error output to stderr
