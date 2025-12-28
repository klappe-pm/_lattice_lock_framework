import asyncio
import json
import logging
import os
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from lattice_lock.orchestrator.chain import ChainOrchestrator

logger = logging.getLogger(__name__)

@click.command()
@click.argument("pipeline_yaml", type=click.Path(exists=True))
@click.option("--input", "-i", multiple=True, help="Input as key=value pairs")
@click.option("--input-json", "-j", help="Path to a JSON file containing inputs")
@click.pass_context
def chain_command(ctx, pipeline_yaml: str, input: list[str], input_json: Optional[str]):
    """Execute a multi-step model pipeline defined in YAML.
    
    Lattice Lock chains allow you to define sequential tasks where the output of
    one model becomes the input to another.
    """
    inputs = {}
    
    # Process multiple --input flags
    for item in input:
        if "=" in item:
            key, value = item.split("=", 1)
            inputs[key] = value
            
    # Load JSON inputs if provided
    if input_json:
        with open(input_json, 'r') as f:
            inputs.update(json.load(f))
            
    asyncio.run(_chain_async(pipeline_yaml, inputs))

async def _chain_async(pipeline_yaml: str, inputs: dict):
    console = Console()
    
    try:
        orchestrator = ChainOrchestrator()
        pipeline = orchestrator.from_yaml(pipeline_yaml)
        
        console.print(f"\n[bold cyan]Executing Pipeline: {pipeline.name}[/bold cyan]")
        console.print(f"[dim]Loaded from {pipeline_yaml}[/dim]\n")
        
        if inputs:
            console.print("[bold]Initial Inputs:[/bold]")
            for k, v in inputs.items():
                console.print(f"  - {k}: {v}")
            console.print()

        result = await orchestrator.run_pipeline(pipeline, inputs)
        
        console.print("[bold green]Pipeline Completed Successfully![/bold green]\n")
        
        # Show summary table
        table = Table(title="Pipeline Execution Summary")
        table.add_column("Step", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Cost", justify="right", style="yellow")
        
        total_cost = 0.0
        for step_name, step_result in result["step_results"].items():
            cost = step_result["usage"].cost if hasattr(step_result["usage"], "cost") else 0.0
            total_cost += cost
            table.add_row(step_name, step_result["model"], f"${cost:.4f}")
            
        console.print(table)
        console.print(f"\n[bold]Total Pipeline Cost:[/bold] ${total_cost:.4f}\n")
        
        # Display final outputs
        for step_name, step_result in result["step_results"].items():
            console.print(Panel(step_result["content"], title=f"Result: {step_name}", border_style="blue"))
            
    except Exception as e:
        console.print(f"[red]Pipeline Failed:[/red] {str(e)}")
        logger.exception("Chain command failed")
