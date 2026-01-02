import asyncio
import json
import logging

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from lattice_lock.orchestrator.chain import ChainOrchestrator

logger = logging.getLogger(__name__)


@click.group(name="chain")
def chain_group():
    """Manage and execute model pipelines."""
    pass


@chain_group.command(name="run")
@click.argument("pipeline_yaml", type=click.Path(exists=True))
@click.option("--input", "-i", multiple=True, help="Input as key=value pairs")
@click.option("--input-json", "-j", help="Path to a JSON file containing inputs")
def run_command(pipeline_yaml: str, input: list[str], input_json: str | None):
    """Execute a new pipeline run."""
    inputs = _parse_inputs(input, input_json)
    asyncio.run(_chain_async(pipeline_yaml, inputs))


@chain_group.command(name="resume")
@click.option("--id", "pipeline_id", help="Pipeline ID to resume")
@click.option(
    "--yaml",
    "pipeline_yaml",
    type=click.Path(exists=True),
    help="Original pipeline YAML (optional if ID known)",
)
@click.option("--input", "-i", multiple=True, help="New input overrides as key=value pairs")
def resume_command(pipeline_id: str | None, pipeline_yaml: str | None, input: list[str]):
    """Resume a failed or paused pipeline."""
    if not pipeline_id and not pipeline_yaml:
        raise click.UsageError("Must provide --id or --yaml to resume.")

    inputs = _parse_inputs(input, None)
    asyncio.run(_chain_async(pipeline_yaml, inputs, resume=True, pipeline_id=pipeline_id))


@chain_group.command(name="history")
@click.option("--limit", default=10, help="Number of runs to show")
def history_command(limit: int):
    """Show pipeline execution history."""
    console = Console()
    console.print(f"[bold]Pipeline History (Last {limit})[/bold]")

    # Stub implementation - persistent storage not yet connected
    table = Table()
    table.add_column("Run ID", style="cyan")
    table.add_column("Pipeline", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Started", style="blue")

    # Mock data
    table.add_row("run_chk92...", "research_flow.yaml", "COMPLETED", "2024-01-01 12:00:00")
    table.add_row("run_8j29s...", "deploy_prod.yaml", "FAILED", "2024-01-01 14:30:00")

    console.print(table)


def _parse_inputs(input_list: list[str], input_json: str | None) -> dict:
    inputs = {}
    for item in input_list:
        if "=" in item:
            key, value = item.split("=", 1)
            inputs[key] = value

    if input_json:
        with open(input_json) as f:
            inputs.update(json.load(f))
    return inputs


async def _chain_async(
    pipeline_yaml: str | None, inputs: dict, resume: bool = False, pipeline_id: str | None = None
):
    console = Console()

    try:
        orchestrator = ChainOrchestrator()

        pipeline = None
        start_step = None

        if resume:
            console.print(
                f"\n[bold cyan]Resuming Pipeline: {pipeline_id or 'Unknown ID'}[/bold cyan]"
            )
            if pipeline_yaml:
                pipeline = orchestrator.from_yaml(pipeline_yaml)
            else:
                console.print(
                    "[yellow]Warning: Resuming without YAML. Assuming specific ID recovery supported by backend.[/yellow]"
                )
                # In real implementation, persistence would load the definition
                return
        else:
            if not pipeline_yaml:
                console.print("[red]Error: Pipeline YAML required for new run.[/red]")
                return
            pipeline = orchestrator.from_yaml(pipeline_yaml)
            console.print(f"\n[bold cyan]Executing Pipeline: {pipeline.name}[/bold cyan]")
            console.print(f"[dim]Loaded from {pipeline_yaml}[/dim]\n")

        if inputs:
            console.print("[bold]Initial Inputs:[/bold]")
            for k, v in inputs.items():
                console.print(f"  - {k}: {v}")
            console.print()

        result = await orchestrator.run_pipeline(
            pipeline, inputs, start_from_step=start_step, pipeline_id=pipeline_id
        )

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
            console.print(
                Panel(step_result["content"], title=f"Result: {step_name}", border_style="blue")
            )

    except Exception as e:
        console.print(f"[red]Pipeline Failed:[/red] {str(e)}")
        logger.exception("Chain command failed")
