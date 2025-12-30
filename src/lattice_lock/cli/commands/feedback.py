"""CLI command for submitting feedback."""

from pathlib import Path

import click
from lattice_lock.feedback.collector import FeedbackCollector
from lattice_lock.feedback.schemas import FeedbackCategory, FeedbackPriority
from lattice_lock.utils.safe_path import resolve_under_root
from rich.console import Console
from rich.prompt import Prompt

console = Console()

# Default storage location
DEFAULT_FEEDBACK_PATH = Path.home() / ".lattice_lock" / "feedback.json"


@click.command()
@click.option(
    "--category",
    "-c",
    type=click.Choice(["bug", "feature", "quality", "metric", "other"]),
    default="other",
    help="Category of feedback",
)
@click.option(
    "--priority",
    "-p",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default="medium",
    help="Priority level",
)
@click.option(
    "--storage", "-s", type=click.Path(), default=None, help="Custom storage path for feedback"
)
def feedback(category: str, priority: str, storage: str):
    """Submit feedback about Lattice Lock."""
    console.print("[bold blue]Lattice Lock Feedback[/bold blue]")
    console.print("We appreciate your input to improve the framework.\n")

    if storage:
        try:
            # Allow absolute paths
            storage_path = resolve_under_root("/", storage)
        except ValueError:
            # Fallback
            storage_path = Path(storage).resolve()
    else:
        storage_path = DEFAULT_FEEDBACK_PATH

    collector = FeedbackCollector(storage_path)

    try:
        content = Prompt.ask("Your feedback")

        if not content.strip():
            console.print("[yellow]Feedback cannot be empty.[/yellow]")
            return

        # Map string to enum
        category_enum = FeedbackCategory(category)
        priority_enum = FeedbackPriority(priority)

        feedback_id = collector.submit(
            content=content, category=category_enum, priority=priority_enum, source="cli"
        )

        console.print(f"\n[green]Thank you! Feedback saved (ID: {feedback_id})[/green]")
    except Exception as e:
        console.print(f"[red]Error saving feedback: {e}[/red]")
