import logging

from lattice_lock.orchestrator.core import ModelOrchestrator
from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)


def handle_cost(console: Console, detailed: bool = False):
    """Handle cost command implementation."""
    try:
        # Initialize orchestrator to access cost tracker
        orchestrator = ModelOrchestrator()
        tracker = orchestrator.cost_tracker

        # Get data
        session_cost = tracker.get_session_cost()
        report = tracker.get_report(days=30)

        # Session Summary
        console.print(f"\n[bold blue]Session Cost:[/bold blue] [green]${session_cost:.6f}[/green]")
        console.print(
            f"[bold blue]Total Cost (30d):[/bold blue] [green]${report['total_cost']:.6f}[/green]\n"
        )

        if detailed:
            # Provider Breakdown
            p_table = Table(title="Cost by Provider (30d)")
            p_table.add_column("Provider", style="cyan")
            p_table.add_column("Cost", style="green", justify="right")

            for provider, cost in report.get("by_provider", {}).items():
                p_table.add_row(provider.title(), f"${cost:.6f}")

            console.print(p_table)
            console.print("")

            # Model Breakdown
            m_table = Table(title="Cost by Model (30d)")
            m_table.add_column("Model ID", style="magenta")
            m_table.add_column("Cost", style="green", justify="right")

            # Sort by cost descending
            sorted_models = sorted(
                report.get("by_model", {}).items(), key=lambda x: x[1], reverse=True
            )

            for model_id, cost in sorted_models:
                m_table.add_row(model_id, f"${cost:.6f}")

            console.print(m_table)

            # Show DB location
            console.print(f"\n[dim]Database path: {tracker.storage.db_path}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error fetching cost data:[/bold red] {e}")
