import click
import os
import json
import sys
from pathlib import Path
from typing import List, Optional

# Assuming lattice_lock_sheriff is correctly set up in the project
from lattice_lock_sheriff.sheriff import validate_path, Violation
from lattice_lock_sheriff.config import SheriffConfig

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
    "--json",
    "json_output",
    is_flag=True,
    help="Output results in JSON format."
)
@click.pass_context
def sheriff_command(
    ctx: click.Context,
    path: Path,
    lattice: Path,
    fix: bool,
    ignore: List[str],
    json_output: bool,
) -> None:
    """
    Validates Python files for import discipline and type hint compliance using Sheriff.
    """
    
    if fix:
        click.echo(click.style("Warning: --fix is not yet implemented.", fg="yellow"))

    # Manual existence check for the 'path' argument
    path_obj = Path(path)
    if not path_obj.exists():
        if json_output:
            click.echo(json.dumps({"error": f"Path '{path}' does not exist."}))
        else:
            click.echo(click.style(f"Error: Path '{path}' does not exist.", fg="red"))
        sys.exit(1)

    actual_lattice_path = lattice

    # Load Sheriff configuration
    try:
        sheriff_config = SheriffConfig.from_yaml(str(actual_lattice_path))
    except Exception as e:
        if json_output:
            click.echo(json.dumps({"error": f"Failed to load lattice.yaml: {e}"}))
        else:
            click.echo(click.style(f"Error: Failed to load lattice.yaml: {e}", fg="red"))
        sys.exit(1)

    violations = validate_path(path_obj, sheriff_config, list(ignore))

    if json_output:
        violations_data = []
        for v in violations:
            violation_dict = v.__dict__.copy()
            violation_dict["file"] = str(violation_dict["file"])
            violations_data.append(violation_dict)
        click.echo(json.dumps({"violations": violations_data, "count": len(violations)}))
        sys.exit(1 if violations else 0)
    else:
        if not violations:
            click.echo(click.style(f"\nSheriff found no violations in {path_obj}", fg="green"))
            sys.exit(0)
        else:
            click.echo(click.style(f"\nSheriff found {len(violations)} violations in {path_obj}:", fg="red", bold=True))
            for v in violations:
                click.echo(
                    f"  {click.style(str(v.file), fg='cyan')}:"
                    f"{click.style(str(v.line), fg='yellow')}:{click.style(str(v.column), fg='yellow')} - "
                    f"{click.style(v.rule, fg='magenta')} - {v.message}"
                )
                if v.code:
                    click.echo(f"    Code: {v.code}")
            click.echo(click.style(f"\nSummary: {len(violations)} violations found.", fg="red", bold=True))
            sys.exit(1)

# Note: The fix functionality is a placeholder.
# Auto-correction would require modifying the AST and then unparsing it back to source.
# This is a complex task and is beyond the initial scope for this CLI wrapper,
# but the `--fix` flag is included as per the prompt.
