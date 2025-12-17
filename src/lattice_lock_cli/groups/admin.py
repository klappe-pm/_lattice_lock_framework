import logging

import click
from lattice_lock_cli.utils.console import get_console

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
    # Placeholder for dashboard launch
    console.print(f"[success]Dashboard running at http://localhost:{port}[/success]")
