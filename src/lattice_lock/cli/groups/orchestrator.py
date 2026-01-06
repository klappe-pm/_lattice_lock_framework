import asyncio
import logging

import click
from rich.panel import Panel
from rich.table import Table

from lattice_lock import ModelOrchestrator, TaskType
from lattice_lock.cli.utils.console import get_console

try:
    from lattice_lock.agents.prompt_architect.agent import PromptArchitectAgent
    from lattice_lock.agents.prompt_architect.orchestrator import orchestrate_prompt_generation
except ImportError:
    orchestrate_prompt_generation = None
    PromptArchitectAgent = None

logger = logging.getLogger(__name__)


@click.group(name="orchestrator")
def orchestrator_group():
    """Manage AI Model Orchestration."""
    pass


@orchestrator_group.command(name="list")
@click.option("--provider", help="Filter by provider")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
def list_models_command(provider, verbose):
    """List available models in the registry."""
    console = get_console()
    orchestrator = ModelOrchestrator()

    table = Table(title="Available Models", show_header=True)
    table.add_column("Provider", style="cyan")
    table.add_column("Model ID", style="green")
    table.add_column("Context", justify="right", style="yellow")
    table.add_column("Cost (I/O)", justify="right", style="red")

    if verbose:
        table.add_column("Capabilities", style="blue")
        table.add_column("Best For", style="magenta")

    for model_id, model in orchestrator.registry.models.items():
        if provider and model.provider.value != provider:
            continue

        cost_str = f"${model.input_cost:.2f}/${model.output_cost:.2f}"
        row = [model.provider.value, model_id, f"{model.context_window:,}", cost_str]

        if verbose:
            # Capabilities
            caps = []
            if model.supports_vision:
                caps.append("👁️ Vision")
            if model.supports_reasoning:
                caps.append("🧠 Reasoning")
            if model.code_specialized:
                caps.append("💻 Code")
            if model.supports_function_calling:
                caps.append("🔧 Functions")

            # Best use cases
            best_for = []
            for task_type, score in model.task_scores.items():
                if score >= 0.8:
                    best_for.append(task_type.name.replace("_", " ").title())

            row.append(" ".join(caps))
            row.append(", ".join(best_for[:3]))

        table.add_row(*row)

    console.print(table)


@orchestrator_group.command(name="analyze")
@click.argument("prompt")
def analyze_prompt_command(prompt):
    """Analyze a prompt and show model selection."""
    console = get_console()
    orchestrator = ModelOrchestrator()

    requirements = orchestrator.analyzer.analyze(prompt)

    # Create requirements panel
    req_content = f"""
Task Type: [bold cyan]{requirements.task_type.name}[/bold cyan]
Min Context: [yellow]{requirements.min_context:,} tokens[/yellow]
Requires Vision: [blue]{'Yes' if requirements.require_vision else 'No'}[/blue]
Requires Reasoning: [green]{'Yes' if requirements.task_type == TaskType.REASONING else 'No'}[/green]
Requires Functions: [magenta]{'Yes' if requirements.require_functions else 'No'}[/magenta]
    """

    console.print(Panel(req_content, title="Task Analysis", border_style="blue"))

    # Score models
    scores = []
    for model_id, model in orchestrator.registry.models.items():
        score = orchestrator.scorer.score(model, requirements)
        if score > 0:
            scores.append((model_id, model, score))

    # Sort by score
    scores.sort(key=lambda x: x[2], reverse=True)

    # Show top 5 recommendations
    table = Table(title="Model Recommendations", show_header=True)
    table.add_column("Rank", justify="center", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Score", justify="right", style="yellow")
    table.add_column("Cost/1K", justify="right", style="red")
    table.add_column("Reason", style="blue")

    for i, (model_id, model, score) in enumerate(scores[:5], 1):
        # Calculate cost per 1K tokens (average of input/output)
        avg_cost = (model.input_cost + model.output_cost) / 2 / 1000

        # Determine main reason for selection
        reasons = []
        if requirements.require_vision and model.supports_vision:
            reasons.append("Vision support")
        if requirements.task_type == TaskType.REASONING and model.supports_reasoning:
            reasons.append("Strong reasoning")
        if model.task_scores.get(requirements.task_type, 0) >= 0.8:
            reasons.append(f"Excellent for {requirements.task_type.name}")
        if model.context_window >= requirements.min_context * 2:
            reasons.append("Large context")
        if avg_cost < 0.01:
            reasons.append("Cost-effective")

        table.add_row(
            str(i),
            model_id,
            f"{score:.2%}",
            f"${avg_cost:.4f}",
            reasons[0] if reasons else "General fit",
        )

    console.print(table)

    if scores:
        # Show selected model
        best_model_id, best_model = scores[0][0], scores[0][1]

        selected_content = f"""
[bold green]Selected Model:[/bold green] {best_model_id}
[bold]Provider:[/bold] {best_model.provider.value}
[bold]Context Window:[/bold] {best_model.context_window:,} tokens
[bold]Estimated Cost:[/bold] ${(best_model.input_cost + best_model.output_cost) / 2 / 1000:.4f} per 1K tokens
        """

        console.print(Panel(selected_content, title="✨ Optimal Choice", border_style="green"))


@orchestrator_group.command(name="route")
@click.argument("prompt")
@click.option(
    "--mode",
    default="auto",
    type=click.Choice(["auto", "consensus", "chain", "adaptive"]),
    help="Routing mode",
)
@click.option(
    "--strategy",
    default="balanced",
    type=click.Choice(["balanced", "cost_optimize", "quality_first", "speed_priority"]),
    help="Selection strategy",
)
def route_command(prompt, mode, strategy):
    """Route a request through the system."""
    asyncio.run(_route_async(prompt, mode, strategy))


async def _route_async(prompt, mode, strategy):
    console = get_console()
    orchestrator = ModelOrchestrator()

    console.print(f"\n[bold]Routing request with mode: {mode}, strategy: {strategy}[/bold]\n")

    # Select model
    model_id = orchestrator._select_best_model(orchestrator.analyzer.analyze(prompt))
    model = orchestrator.registry.get_model(model_id)

    console.print(f"[green]Selected model:[/green] {model_id}")
    console.print(f"[blue]Provider:[/blue] {model.provider.value}")
    console.print(f"[yellow]Context:[/yellow] {model.context_window:,} tokens")

    # Estimate cost (assuming 1K input, 500 output)
    if hasattr(orchestrator, "estimate_cost"):
        cost = orchestrator.estimate_cost(model_id, 1000, 500)
        console.print(f"[red]Estimated cost:[/red] ${cost:.4f}")
    else:
        # Manual calculation
        cost = (model.input_cost * 1000 + model.output_cost * 500) / 1000000
        console.print(f"[red]Estimated cost:[/red] ${cost:.4f}")

    # Would make actual API call here
    console.print("\n[dim]Note: Actual API call would be made here[/dim]")


@orchestrator_group.command(name="consensus")
@click.argument("prompt")
@click.option("--num", default=3, type=int, help="Number of models to consult")
@click.option("--synthesizer", help="Specific model to use for synthesis")
def consensus_command(prompt, num, synthesizer):
    """Create a consensus group for the prompt."""
    asyncio.run(_consensus_async(prompt, num, synthesizer))


async def _consensus_async(prompt, num, synthesizer):
    from lattice_lock.orchestrator import ConsensusOrchestrator

    console = get_console()
    orchestrator = ConsensusOrchestrator()

    console.print(f"\n[bold cyan]Starting Consensus Flow ({num} models)[/bold cyan]\n")

    try:
        result = await orchestrator.run_consensus(
            prompt, num_models=num, synthesizer_model_id=synthesizer
        )

        console.print("[bold green]Synthesis Result:[/bold green]")
        console.print(
            Panel(
                result["synthesis"],
                title=f"Synthesized by {result['synthesizer_model']}",
                border_style="green",
            )
        )

        console.print("\n[bold]Individual Model Contributions:[/bold]")
        table = Table(show_header=True)
        table.add_column("Model", style="cyan")
        table.add_column("Cost", justify="right", style="yellow")

        for resp in result["individual_responses"]:
            cost = resp["usage"].cost if hasattr(resp["usage"], "cost") else 0.0
            table.add_row(resp["model"], f"${cost:.4f}")

        console.print(table)
        console.print(f"\n[bold]Total Consensus Cost:[/bold] ${result['total_cost']:.4f}\n")

    except Exception as e:
        console.print(f"[red]Consensus Failed:[/red] {str(e)}")


@orchestrator_group.command(name="cost")
@click.option("--detailed", is_flag=True, help="Show detailed breakdown")
def cost_command(detailed):
    """Show cost usage report."""
    console = get_console()
    try:
        from lattice_lock.orchestrator.cli.cost_command import handle_cost

        handle_cost(console, detailed=detailed)
    except ImportError:
        console.print("[red]Cost tracking module not available.[/red]")


@orchestrator_group.command(name="generate-prompts")
@click.option("--spec", help="Path to specification file")
@click.option("--roadmap", help="Path to roadmap/WBS file")
@click.option("--output-dir", help="Output directory for generated prompts")
@click.option("--dry-run", is_flag=True, help="Simulate without writing files")
@click.option("--from-project", is_flag=True, help="Auto-discover from Project Agent")
@click.option("--phases", help="Comma-separated list of phases to generate")
@click.option("--tools", help="Comma-separated list of tools to filter")
def generate_prompts_command(spec, roadmap, output_dir, dry_run, from_project, phases, tools):
    """Generate prompts from specifications and roadmaps."""
    asyncio.run(
        _generate_prompts_async(spec, roadmap, output_dir, dry_run, from_project, phases, tools)
    )


async def _generate_prompts_async(spec, roadmap, output_dir, dry_run, from_project, phases, tools):
    console = get_console()

    if orchestrate_prompt_generation is None:
        console.print("[red]Prompt Architect module not available.[/red]")
        console.print("[dim]Install with: pip install -e .[/dim]")
        return

    phase_list = phases.split(",") if phases else None
    tool_list = tools.split(",") if tools else None

    console.print("\n[bold cyan]Prompt Architect - Automated Prompt Generation[/bold cyan]\n")

    # Show configuration
    config_content = f"""
[bold]Specification:[/bold] {spec or 'Auto-discover' if from_project else 'Not provided'}
[bold]Roadmap:[/bold] {roadmap or 'Auto-discover' if from_project else 'Not provided'}
[bold]Output Directory:[/bold] {output_dir or 'Default (project_prompts/)'}
[bold]Dry Run:[/bold] {'Yes' if dry_run else 'No'}
[bold]From Project:[/bold] {'Yes' if from_project else 'No'}
[bold]Phases Filter:[/bold] {', '.join(phase_list) if phase_list else 'All'}
[bold]Tools Filter:[/bold] {', '.join(tool_list) if tool_list else 'All'}
    """
    console.print(Panel(config_content.strip(), title="Configuration", border_style="blue"))

    console.print("\n[yellow]Running prompt generation pipeline...[/yellow]\n")

    try:
        result = await orchestrate_prompt_generation(
            spec_path=spec,
            roadmap_path=roadmap,
            output_dir=output_dir,
            dry_run=dry_run,
            from_project=from_project,
            phases=phase_list,
            tools=tool_list,
        )

        # Display results
        status_color = {
            "success": "green",
            "partial": "yellow",
            "failure": "red",
        }.get(result.status, "white")

        result_content = f"""
[bold]Status:[/bold] [{status_color}]{result.status.upper()}[/{status_color}]
[bold]Prompts Generated:[/bold] {result.prompts_generated}
[bold]Prompts Updated:[/bold] {result.prompts_updated}
[bold]Phases Covered:[/bold] {', '.join(result.phases_covered) if result.phases_covered else 'None'}
        """
        console.print(Panel(result_content.strip(), title="Results", border_style=status_color))

        # Show tool distribution
        if result.tool_distribution:
            table = Table(title="Tool Distribution", show_header=True)
            table.add_column("Tool", style="cyan")
            table.add_column("Prompts", justify="right", style="green")

            for tool, count in sorted(result.tool_distribution.items()):
                table.add_row(tool, str(count))

            console.print(table)

        # Show errors if any
        if result.errors:
            console.print("\n[bold red]Errors:[/bold red]")
            for error in result.errors:
                console.print(f"  [red]- {error}[/red]")

    except Exception as e:
        console.print(f"[red]Error during prompt generation: {e}[/red]")
        raise
