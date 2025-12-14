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


from lattice_lock_cli.commands.doctor import doctor_command
from lattice_lock_cli.commands.gauntlet import gauntlet_command

# Import commands from commands module
from lattice_lock_cli.commands.init import init_command
from lattice_lock_cli.commands.sheriff import sheriff_command
from lattice_lock_cli.commands.validate import validate_command

# Register commands with the CLI
cli.add_command(init_command, name="init")
cli.add_command(validate_command, name="validate")
cli.add_command(doctor_command, name="doctor")
cli.add_command(gauntlet_command, name="gauntlet")
cli.add_command(sheriff_command, name="sheriff")


@cli.command()
def test():
    """Run Gauntlet semantic tests."""
    console.print("[magenta]Running Gauntlet...[/]")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
