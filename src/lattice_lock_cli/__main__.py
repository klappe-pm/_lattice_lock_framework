"""
Lattice Lock CLI Entry Point

Main entry point for the lattice-lock command-line interface.
"""

import click

from . import __version__


@click.group()
@click.version_option(version=__version__, prog_name="lattice-lock")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """Lattice Lock Framework CLI

    A governance-first framework for AI-assisted software development.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


# Import and register commands
from .commands.init import init_command
from .commands.validate import validate_command
from .commands.doctor import doctor_command
from .commands.sheriff import sheriff_command
from .commands.gauntlet import gauntlet_command

cli.add_command(init_command, name="init")
cli.add_command(validate_command, name="validate")
cli.add_command(doctor_command, name="doctor")
cli.add_command(sheriff_command, name="sheriff")
cli.add_command(gauntlet_command, name="gauntlet")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
