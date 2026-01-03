import logging

import click
from rich.table import Table

from lattice_lock.cli.utils.console import get_console
from lattice_lock.config.feature_flags import Feature, is_feature_enabled

logger = logging.getLogger(__name__)


@click.group(name="admin")
def admin_group():
    """Administrative tools and dashboard."""
    pass


@admin_group.command(name="dashboard")
@click.option("--port", default=8000, help="Port to run the dashboard on.")
def run_dashboard(port):
    """Launch the local admin dashboard."""
    console = get_console()
    console.print(f"[info]Starting admin dashboard on port {port}...[/info]")

    try:
        import uvicorn

        from lattice_lock.admin.api import create_app

        app = create_app()
        console.print(f"[success]Dashboard running at http://localhost:{port}[/success]")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except ImportError:
        console.print(
            "[error]Missing dependencies. Install with: pip install uvicorn fastapi[/error]"
        )
    except Exception as e:
        console.print(f"[error]Failed to start dashboard: {e}[/error]")


@admin_group.command(name="features")
def features_command():
    """List active feature flags and presets."""
    console = get_console()

    # 1. Show Feature Preset (Env var)
    import os

    preset = os.getenv("LATTICE_FEATURE_PRESET", "standard")
    console.print(f"Current Preset: [bold cyan]{preset}[/bold cyan]\n")

    # 2. Show Table
    table = Table(title="Feature Flags Status")
    table.add_column("Feature", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Reason", style="dim")

    for feature in Feature:
        enabled = is_feature_enabled(feature)
        status_str = "[green]ENABLED[/green]" if enabled else "[red]DISABLED[/red]"

        # Determine strict reason (env var override vs preset)
        disabled_list = os.getenv("LATTICE_DISABLED_FEATURES", "").split(",")
        if feature.value in disabled_list:
            reason = "Explicitly Disabled (Env)"
        else:
            reason = f"Preset ({preset})"

        table.add_row(feature.value, status_str, reason)

    console.print(table)


# Register subcommands
from lattice_lock.cli.commands.admin import admin_command

admin_group.add_command(admin_command, name="serve")
