#!/usr/bin/env python3
"""
DEPRECATED: Orchestrator CLI
"""
import sys
from rich.console import Console

console = Console()

if __name__ == "__main__":
    console.print("[bold red]DEPRECATED:[/bold red] This script has been deprecated.")
    console.print("Please use the [green]lattice-lock orchestrator[/green] command group instead.")
    console.print("\nExamples:")
    console.print("  lattice-lock orchestrator list")
    console.print("  lattice-lock orchestrator analyze 'prompt'")
    console.print("  lattice-lock orchestrator generate-prompts")
    sys.exit(1)
