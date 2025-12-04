"""Sheriff CLI command for AST-based validation with CI integration.

Provides:
- Multiple output formats (text, json, github, junit)
- File-based caching for performance
- CI/CD pipeline integration
- Audit trail for ignored violations
"""

import click
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from lattice_lock_sheriff.sheriff import (
    validate_path_with_audit,
    validate_file_with_audit,
    Violation,
)
from lattice_lock_sheriff.config import SheriffConfig
from lattice_lock_sheriff.formatters import get_formatter
from lattice_lock_sheriff.cache import SheriffCache, get_config_hash


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
    help="Attempt to auto-correct violations where possible (not implemented yet)."
)
@click.option(
    "--ignore",
    multiple=True,
    help="Glob patterns for files or directories to ignore (e.g., '**/ignore_me.py', '*/temp_dir/*')."
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "github", "junit"], case_sensitive=False),
    default="text",
    help="Output format. 'text' for human-readable, 'json' for machine-readable, "
         "'github' for GitHub Actions annotations, 'junit' for JUnit XML reports."
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    hidden=True,
    help="[DEPRECATED] Use --format json instead. Output results in JSON format."
)
@click.option(
    "--cache/--no-cache",
    "use_cache",
    default=True,
    help="Enable/disable file caching. Cache skips unchanged files based on content hash."
)
@click.option(
    "--cache-dir",
    type=click.Path(path_type=Path),
    default=".sheriff_cache",
    help="Directory to store cache files."
)
@click.option(
    "--clear-cache",
    is_flag=True,
    help="Clear the cache before running validation."
)
@click.pass_context
def sheriff_command(
    ctx: click.Context,
    path: str,
    lattice: Path,
    fix: bool,
    ignore: List[str],
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

    # Load Sheriff configuration
    try:
        sheriff_config = SheriffConfig.from_yaml(str(lattice))
    except Exception as e:
        _handle_error(output_format, f"Failed to load lattice.yaml: {e}")
        sys.exit(1)

    # Initialize cache
    cache: Optional[SheriffCache] = None
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
    if output_format in ("github", "junit"):
        # Use formatters for GitHub and JUnit
        formatter = get_formatter(output_format)
        output = formatter.format(violations, path_obj)
        click.echo(output)
        exit_code = formatter.get_exit_code(violations)
    elif output_format == "json":
        # JSON with audit information
        _print_json_output(violations, ignored_violations, path_obj)
        exit_code = 1 if violations else 0
    else:
        # Text format with colors and audit
        _print_text_output(violations, ignored_violations, path_obj)
        exit_code = 1 if violations else 0

    sys.exit(exit_code)


def _validate_with_cache(
    path: Path,
    config: SheriffConfig,
    ignore_patterns: List[str],
    cache: Optional[SheriffCache]
) -> Tuple[List[Violation], List[Violation]]:
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

    violations: List[Violation] = []
    ignored_violations: List[Violation] = []

    if path.is_file():
        v, iv = _validate_file_with_cache(path, config, ignore_patterns, cache)
        violations.extend(v)
        ignored_violations.extend(iv)
    elif path.is_dir():
        # Walk directory and validate each file with caching
        import os
        for root, _, files in os.walk(path):
            current_dir = Path(root)

            # Apply directory-level ignore patterns
            ignored_by_dir = False
            for pattern in ignore_patterns:
                relative_dir = current_dir.relative_to(path) if current_dir != path else Path('.')
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
                        file_path, config, ignore_patterns, cache
                    )
                    violations.extend(v)
                    ignored_violations.extend(iv)

    return violations, ignored_violations


def _validate_file_with_cache(
    file_path: Path,
    config: SheriffConfig,
    ignore_patterns: List[str],
    cache: SheriffCache
) -> Tuple[List[Violation], List[Violation]]:
    """Validate a single file with caching.

    Args:
        file_path: Path to the Python file
        config: Sheriff configuration
        ignore_patterns: Glob patterns to ignore
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
        for v in cached_data:
            violation = Violation(
                file=Path(v["file"]),
                line=v["line"],
                column=v["column"],
                message=v["message"],
                rule=v["rule"],
                code=v.get("code")
            )
            if v.get("ignored", False):
                ignored_violations.append(violation)
            else:
                violations.append(violation)
        return violations, ignored_violations

    # Not cached, validate and cache result
    violations, ignored_violations = validate_file_with_audit(file_path, config, ignore_patterns)

    # Cache the results (include ignored flag)
    violations_data = []
    for v in violations:
        violations_data.append({
            "file": str(v.file),
            "line": v.line,
            "column": v.column,
            "message": v.message,
            "rule": v.rule,
            "code": v.code,
            "ignored": False
        })
    for v in ignored_violations:
        violations_data.append({
            "file": str(v.file),
            "line": v.line,
            "column": v.column,
            "message": v.message,
            "rule": v.rule,
            "code": v.code,
            "ignored": True
        })
    cache.set_violations(file_path, violations_data)

    return violations, ignored_violations


def _handle_error(output_format: str, message: str) -> None:
    """Output an error message in the appropriate format.

    Args:
        output_format: The output format being used
        message: The error message
    """
    if output_format == "json":
        click.echo(json.dumps({"error": message, "success": False}))
    elif output_format == "github":
        click.echo(f"::error::{message}")
    elif output_format == "junit":
        # Output minimal JUnit XML with error
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Sheriff Validation" tests="1" failures="1" errors="1">
  <testsuite name="Sheriff" tests="1" failures="1" errors="1">
    <testcase name="Configuration" classname="sheriff">
      <error message="{message}" type="ConfigurationError">{message}</error>
    </testcase>
  </testsuite>
</testsuites>'''
        click.echo(xml)
    else:
        click.echo(click.style(f"Error: {message}", fg="red"), err=True)


def _print_json_output(
    violations: List[Violation],
    ignored_violations: List[Violation],
    target_path: Path
) -> None:
    """Print JSON output with audit information.

    Args:
        violations: List of violations
        ignored_violations: List of ignored violations
        target_path: The path that was validated
    """
    violations_data = []
    for v in violations:
        violation_dict = v.__dict__.copy()
        violation_dict["file"] = str(violation_dict["file"])
        violations_data.append(violation_dict)

    ignored_data = []
    for v in ignored_violations:
        violation_dict = v.__dict__.copy()
        violation_dict["file"] = str(violation_dict["file"])
        ignored_data.append(violation_dict)

    click.echo(json.dumps({
        "violations": violations_data,
        "ignored_violations": ignored_data,
        "count": len(violations),
        "ignored_count": len(ignored_violations),
        "target": str(target_path),
        "success": len(violations) == 0
    }))


def _print_text_output(
    violations: List[Violation],
    ignored_violations: List[Violation],
    target_path: Path
) -> None:
    """Print human-readable colored text output with audit.

    Args:
        violations: List of violations
        ignored_violations: List of ignored violations
        target_path: The path that was validated
    """
    if not violations and not ignored_violations:
        click.echo(click.style(f"\nSheriff found no violations in {target_path}", fg="green"))
        return

    if violations:
        click.echo(click.style(
            f"\nSheriff found {len(violations)} violations in {target_path}:",
            fg="red", bold=True
        ))
        for v in violations:
            click.echo(
                f"  {click.style(str(v.file), fg='cyan')}:"
                f"{click.style(str(v.line), fg='yellow')}:{click.style(str(v.column), fg='yellow')} - "
                f"{click.style(v.rule, fg='magenta')} - {v.message}"
            )
            if v.code:
                click.echo(f"    Code: {v.code}")

    if ignored_violations:
        click.echo(click.style(
            f"\nSheriff audited {len(ignored_violations)} ignored violations in {target_path}:",
            fg="yellow", bold=True
        ))
        for v in ignored_violations:
            click.echo(
                f"  {click.style(str(v.file), fg='cyan')}:"
                f"{click.style(str(v.line), fg='yellow')}:{click.style(str(v.column), fg='yellow')} - "
                f"{click.style(v.rule, fg='magenta')} - {v.message} (IGNORED)"
            )

    if violations:
        click.echo(click.style(
            f"\nSummary: {len(violations)} violations found.",
            fg="red", bold=True
        ))
    else:
        click.echo(click.style(
            f"\nSummary: 0 violations found ({len(ignored_violations)} ignored).",
            fg="green", bold=True
        ))


# Note: The fix functionality is a placeholder.
# Auto-correction would require modifying the AST and then unparsing it back to source.
# This is a complex task and is beyond the initial scope for this CLI wrapper,
# but the `--fix` flag is included as per the prompt.
