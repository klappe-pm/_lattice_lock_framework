import click
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from lattice_lock.feedback.collector import FeedbackCollector

console = Console()

@click.command()
@click.option('--category', '-c', default='general', help='Category of feedback')
def feedback(category):
    """Submit feedback about Lattice Lock."""
    console.print("[bold blue]Lattice Lock Feedback[/bold blue]")
    console.print("We appreciate your input to improve the framework.\n")
    
    collector = FeedbackCollector()
    
    try:
        rating = IntPrompt.ask("Rate your experience (1-5)", choices=["1", "2", "3", "4", "5"])
        comment = Prompt.ask("Your comments")
        
        entry = collector.submit_feedback(rating, comment, category)
        
        console.print(f"\n[green]Thank you! Feedback saved (ID: {entry['id']})[/green]")
    except Exception as e:
        console.print(f"[red]Error saving feedback: {e}[/red]")
