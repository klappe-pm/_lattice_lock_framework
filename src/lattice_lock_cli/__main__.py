"""
Lattice Lock CLI - Command-line interface for the Lattice Lock Framework.

This module provides the main entry point for the CLI.
"""

import click
import logging
from typing import Optional

from lattice_lock import __version__
from lattice_lock_cli.utils.console import get_console

# Import command groups
from lattice_lock_cli.groups.orchestrator import orchestrator_group
from lattice_lock_cli.groups.admin import admin_group

# Import existing commands
from lattice_lock_cli.commands.compile import compile_command
from lattice_lock_cli.commands.doctor import doctor_command
from lattice_lock_cli.commands.feedback import feedback
from lattice_lock_cli.commands.gauntlet import gauntlet_command
from lattice_lock_cli.commands.init import init_command
from lattice_lock_cli.commands.sheriff import sheriff_command
from lattice_lock_cli.commands.validate import validate_command

# Configuration for logger
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("lattice_lock")

@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--json", is_flag=True, help="Output results as JSON")
@click.option(
    "--project-dir",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    default=".",
    help="Target project directory (default: current)",
)
@click.version_option(version=__version__, prog_name="lattice-lock")
@click.pass_context
def cli(ctx, verbose: bool, json: bool, project_dir: str):
    """Lattice Lock Framework CLI - Governance for AI Engineering."""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["JSON"] = json
    ctx.obj["PROJECT_DIR"] = project_dir
    
    if verbose:
        logger.setLevel(logging.DEBUG)
        get_console().print("[info]Verbose mode enabled[/info]")

# Register Core Commands
cli.add_command(init_command, name="init")
cli.add_command(validate_command, name="validate")
cli.add_command(compile_command, name="compile")
cli.add_command(doctor_command, name="doctor")
cli.add_command(feedback, name="feedback")

# Alias commands for better UX
cli.add_command(gauntlet_command, name="test")
cli.add_command(sheriff_command, name="sheriff") # Keep sheriff available directly or via validate? Design says 'validate' runs sheriff.

# Register Groups
cli.add_command(orchestrator_group)
cli.add_command(admin_group)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
