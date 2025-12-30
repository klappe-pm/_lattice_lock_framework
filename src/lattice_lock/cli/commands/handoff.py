import click
import json
import logging
from rich.console import Console
from rich.table import Table
from pathlib import Path

from lattice_lock.context.serialization import ContextHandoff

logger = logging.getLogger(__name__)

@click.group(name="handoff")
def handoff_group():
    """Manage context handoffs between tools or sessions."""
    pass

@handoff_group.command(name="save")
@click.argument("name")
@click.option("--messages", "-m", help="Path to a JSON file containing messages")
@click.option("--input-dir", "-d", default=".", help="Project directory")
def handoff_save(name, messages, input_dir):
    """Save the current context to a handoff file."""
    console = Console()
    try:
        handler = ContextHandoff(project_dir=input_dir)
        
        # In a real scenario, this might be called from another command 
        # or it might read from a temp file used in the current session.
        if not messages:
            console.print("[red]Error:[/red] No messages provided. Use --messages <path/to/json>")
            return
            
        with open(messages, 'r') as f:
            messages_data = json.load(f)
            
        file_path = handler.save(name, messages_data)
        console.print(f"[green]Handoff '{name}' saved to {file_path}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to save handoff:[/red] {str(e)}")

@handoff_group.command(name="list")
@click.option("--input-dir", "-d", default=".", help="Project directory")
def handoff_list(input_dir):
    """List all available handoffs."""
    console = Console()
    handler = ContextHandoff(project_dir=input_dir)
    handoffs = handler.list_handoffs()
    
    if not handoffs:
        console.print("[yellow]No handoffs found.[/yellow]")
        return
        
    table = Table(title="Available Context Handoffs")
    table.add_column("Handoff Name", style="cyan")
    
    for h in handoffs:
        table.add_row(h)
        
    console.print(table)

@handoff_group.command(name="show")
@click.argument("name")
@click.option("--input-dir", "-d", default=".", help="Project directory")
def handoff_show(name, input_dir):
    """Show the contents of a handoff."""
    console = Console()
    try:
        handler = ContextHandoff(project_dir=input_dir)
        data = handler.load(name)
        
        console.print(f"[bold cyan]Handoff: {name}[/bold cyan]")
        console.print(f"[dim]Timestamp: {data['timestamp']}[/dim]\n")
        
        for i, msg in enumerate(data["messages"]):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            console.print(f"[bold]{role.upper()}:[/bold]")
            console.print(content)
            console.print("-" * 20)
            
    except Exception as e:
        console.print(f"[red]Error loading handoff:[/red] {str(e)}")
