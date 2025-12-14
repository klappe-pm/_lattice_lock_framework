"""
Lattice Lock CLI - Command-line interface for the Lattice Lock Framework.

This module provides the main entry point for the CLI.
"""

import click
from lattice_lock import __version__
from rich.console import Console

console = Console()


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.version_option(version=__version__, prog_name="lattice-lock")
@click.pass_context
def cli(ctx, verbose):
    """Lattice Lock Framework CLI - Governance for AI Engineering."""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    if verbose:
        console.log("[bold blue]Verbose mode enabled[/]")


@cli.command()
@click.argument("name")
@click.option("--output-dir", "-o", default=".", help="Output directory for the project")
@click.option(
    "--template",
    "-t",
    type=click.Choice(["agent", "service", "library"]),
    default="service",
    help="Project template type",
)
@click.pass_context
def init(ctx, name, output_dir, template):
    """Initialize a new project with NAME."""
    from pathlib import Path

    verbose = ctx.obj.get("VERBOSE", False)
    output_path = Path(output_dir)

    if verbose:
        console.print(f"[blue]Creating project '{name}' in {output_dir}[/]")

    # Import here to avoid circular imports
    from lattice_lock_cli.commands.init import create_project_structure, validate_project_name

    # Validate project name
    if not validate_project_name(name):
        console.print(
            f"[red]Invalid project name '{name}'. "
            "Name must be snake_case (lowercase letters, numbers, underscores) "
            "and start with a letter.[/]"
        )
        raise SystemExit(1)

    # Check if directory already exists
    project_dir = output_path / name
    if project_dir.exists():
        console.print(
            f"[red]Directory '{project_dir}' already exists. "
            "Please choose a different name or remove the existing directory.[/]"
        )
        raise SystemExit(1)

    try:
        created_files = create_project_structure(
            project_name=name,
            project_type=template,
            output_dir=output_path,
            verbose=verbose,
        )
        console.print(f"[green]Created project '{name}' with {len(created_files)} files![/]")
    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/]")
        raise SystemExit(1)


@cli.command()
def validate():
    """Run Sheriff AST validation."""
    console.print("[yellow]Running Sheriff...[/]")


@cli.command()
def test():
    """Run Gauntlet semantic tests."""
    console.print("[magenta]Running Gauntlet...[/]")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
