"""
Lattice Lock CLI - Command-line interface for the Lattice Lock Framework.

This module provides the main entry point for the CLI.
"""

import logging

import click

from lattice_lock import __version__

# Import existing commands
from lattice_lock.cli.commands.ask import ask_command
from lattice_lock.cli.commands.chain import chain_group
from lattice_lock.cli.commands.compile import compile_command
from lattice_lock.cli.commands.doctor import doctor_command
from lattice_lock.cli.commands.feedback import feedback
from lattice_lock.cli.commands.gauntlet import gauntlet_command
from lattice_lock.cli.commands.handoff import handoff_group
from lattice_lock.cli.commands.init import init_command
from lattice_lock.cli.commands.mcp import mcp_command
from lattice_lock.cli.commands.sheriff import sheriff_command
from lattice_lock.cli.commands.validate import validate_command
from lattice_lock.cli.groups.admin import admin_group

# Import command groups
from lattice_lock.cli.groups.orchestrator import orchestrator_group
from lattice_lock.cli.utils.console import get_console
from lattice_lock.logging_config import get_logger, set_trace_id, setup_logging

# Initialize centralized logging with simple format for CLI
setup_logging(level=logging.INFO, simple_format=True)
logger = get_logger("cli")


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
    # Generate trace ID for this CLI invocation
    trace_id = set_trace_id()

    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["JSON"] = json
    ctx.obj["PROJECT_DIR"] = project_dir
    ctx.obj["TRACE_ID"] = trace_id

    if verbose:
        setup_logging(level=logging.DEBUG, simple_format=True)
        get_console().print("[info]Verbose mode enabled[/info]")


# Register Core Commands
cli.add_command(init_command, name="init")
cli.add_command(ask_command, name="ask")
cli.add_command(chain_group)
cli.add_command(validate_command, name="validate")
cli.add_command(compile_command, name="compile")
cli.add_command(doctor_command, name="doctor")
cli.add_command(feedback, name="feedback")
cli.add_command(mcp_command, name="mcp")

# Alias commands for better UX
cli.add_command(gauntlet_command, name="test")
cli.add_command(gauntlet_command, name="gauntlet")  # Alias for backward compatibility
cli.add_command(
    sheriff_command, name="sheriff"
)  # Keep sheriff available directly or via validate? Design says 'validate' runs sheriff.

# Register Groups
cli.add_command(orchestrator_group)
cli.add_command(admin_group)
cli.add_command(handoff_group, name="handoff")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
