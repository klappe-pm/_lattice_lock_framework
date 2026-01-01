import asyncio
import logging

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from lattice_lock import ModelOrchestrator, TaskType

logger = logging.getLogger(__name__)


@click.command()
@click.argument("prompt")
@click.option(
    "--model", "-m", help="Force a specific model ID (e.g., 'gpt-4o', 'claude-3-5-sonnet')"
)
@click.option(
    "--task-type",
    "-t",
    type=click.Choice([t.name for t in TaskType], case_sensitive=False),
    help="Override automatic task analysis",
)
@click.option("--compare", is_flag=True, help="Compare results from multiple high-ranking models")
@click.pass_context
def ask_command(ctx, prompt: str, model: str | None, task_type: str | None, compare: bool):
    """Universal query: Ask any question and get routed to the best model.

    Lattice Lock analyzes your prompt, selects the optimal model based on performance/cost,
    and returns the result.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    asyncio.run(_ask_async(prompt, model, task_type, compare, verbose))


async def _ask_async(
    prompt: str, model_id: str | None, task_type_str: str | None, compare: bool, verbose: bool
):
    console = Console()
    orchestrator = ModelOrchestrator()

    task_type = TaskType[task_type_str.upper()] if task_type_str else None

    if compare:
        await _handle_compare(orchestrator, prompt, task_type, console, verbose)
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description="Analyzing and routing...", total=None)

        try:
            response = await orchestrator.route_request(
                prompt=prompt, model_id=model_id, task_type=task_type
            )
            progress.stop()

            # Display metadata if verbose
            if verbose:
                meta_table = Table(box=None, padding=(0, 2))
                meta_table.add_column("Property", style="dim")
                meta_table.add_column("Value")
                meta_table.add_row("Model", response.model)
                meta_table.add_row("Provider", response.provider)

                if hasattr(response.usage, "prompt_tokens"):
                    meta_table.add_row(
                        "Tokens",
                        f"I: {response.usage.prompt_tokens} / O: {response.usage.completion_tokens}",
                    )
                    meta_table.add_row("Cost", f"${response.usage.cost:.4f}")

                console.print(Panel(meta_table, title="Metadata", border_style="dim"))

            console.print(
                Panel(response.content, title=f"Response ({response.model})", border_style="green")
            )

        except Exception as e:
            progress.stop()
            console.print(f"[red]Error:[/red] {str(e)}")
            if verbose:
                logger.exception("Ask command failed")


async def _handle_compare(
    orchestrator: ModelOrchestrator,
    prompt: str,
    task_type: TaskType | None,
    console: Console,
    verbose: bool,
):
    """Handle the --compare flag by running multiple models in parallel."""
    # 1. Analyze task to get requirements
    requirements = await orchestrator.analyzer.analyze_async(prompt)
    if task_type:
        requirements.task_type = task_type

    # 2. Get top 3 models
    # This is currently not a public method in selector, so we might need to expose it or mock it
    # For now, let's use a heuristic: get recommendations and pick top 3
    all_models = []
    for m_id, m_cap in orchestrator.registry.models.items():
        score = orchestrator.scorer.score(m_cap, requirements)
        if score > 0:
            all_models.append((m_id, m_cap, score))

    all_models.sort(key=lambda x: x[2], reverse=True)
    top_models = all_models[:3]

    if not top_models:
        console.print("[red]No suitable models found for comparison.[/red]")
        return

    console.print(
        f"[bold]Comparing {len(top_models)} models for task: {requirements.task_type.name}[/bold]\n"
    )

    # 3. Execute in parallel
    tasks = []
    for m_id, m_cap, _ in top_models:
        tasks.append(orchestrator.route_request(prompt, model_id=m_id, task_type=task_type))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        p_task = progress.add_task(
            description="Awaiting responses from all models...", total=len(tasks)
        )
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        progress.update(p_task, completed=len(tasks))

    # 4. Display side-by-side or sequentially with distinct panels
    for i, response in enumerate(responses):
        m_id = top_models[i][0]
        if isinstance(response, Exception):
            console.print(
                Panel(
                    f"[red]Failed:[/red] {str(response)}",
                    title=f"Model: {m_id}",
                    border_style="red",
                )
            )
        else:
            cost_str = f"${response.usage.cost:.4f}" if hasattr(response.usage, "cost") else "N/A"
            console.print(
                Panel(
                    response.content,
                    title=f"Model: {response.model} ({cost_str})",
                    border_style="blue",
                )
            )
