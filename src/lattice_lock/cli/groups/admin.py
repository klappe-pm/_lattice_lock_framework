import logging

import click

from lattice_lock.cli.utils.console import get_console

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
        console.print("[error]Missing dependencies. Install with: pip install uvicorn fastapi[/error]")
    except Exception as e:
        console.print(f"[error]Failed to start dashboard: {e}[/error]")


# Register subcommands
from lattice_lock.cli.commands.admin import admin_command

admin_group.add_command(admin_command, name="serve")
