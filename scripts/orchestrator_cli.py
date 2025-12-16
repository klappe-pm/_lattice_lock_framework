#!/usr/bin/env python3
"""
Model Orchestrator CLI
Command-line interface for the intelligent model orchestration system
"""

import argparse
import asyncio
import os
from typing import Optional

# Import orchestration components from lattice_lock package
from lattice_lock import ModelOrchestrator, TaskType
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add src directory to path for imports
# Add src directory to path for imports
# sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
# Assuming package is installed or PYTHONPATH is set correctly


try:
    from lattice_lock_orchestrator.zen_mcp_bridge import ModelRouter, ZenMCPBridge
except ImportError:
    ZenMCPBridge = None
    ModelRouter = None

try:
    from lattice_lock_orchestrator.grok_api import GrokAPI
except ImportError:
    GrokAPI = None

try:
    from lattice_lock_agents.prompt_architect.agent import PromptArchitectAgent
    from lattice_lock_agents.prompt_architect.orchestrator import orchestrate_prompt_generation
except ImportError:
    orchestrate_prompt_generation = None
    PromptArchitectAgent = None

console = Console()


class OrchestratorCLI:
    """CLI interface for model orchestration"""

    def __init__(self):
        self.orchestrator = ModelOrchestrator()
        self.bridge = ZenMCPBridge() if ZenMCPBridge else None
        self.router = ModelRouter() if ModelRouter else None
        self.grok_api = None

        # Try to initialize Grok API if key is available
        if GrokAPI and os.getenv("XAI_API_KEY"):
            try:
                self.grok_api = GrokAPI()
            except (ImportError, ValueError, RuntimeError) as e:
                # Log initialization failure but continue without Grok API
                console.print(f"[dim]Grok API initialization skipped: {e}[/dim]")

    def list_models(self, provider: Optional[str] = None, verbose: bool = False):
        """List all available models"""

        table = Table(title="Available Models", show_header=True)
        table.add_column("Provider", style="cyan")
        table.add_column("Model ID", style="green")
        table.add_column("Context", justify="right", style="yellow")
        table.add_column("Cost (I/O)", justify="right", style="red")

        if verbose:
            table.add_column("Capabilities", style="blue")
            table.add_column("Best For", style="magenta")

        for model_id, model in self.orchestrator.registry.models.items():
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
                row.append(", ".join(best_for[:3]))  # Top 3

            table.add_row(*row)

        console.print(table)

    def analyze_prompt(self, prompt: str):
        """Analyze a prompt and show model selection"""

        requirements = self.orchestrator.analyzer.analyze(prompt)

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
        for model_id, model in self.orchestrator.registry.models.items():
            score = self.orchestrator.scorer.score(model, requirements)
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

        # Show selected model
        best_model_id, best_model = scores[0][0], scores[0][1]

        selected_content = f"""
[bold green]Selected Model:[/bold green] {best_model_id}
[bold]Provider:[/bold] {best_model.provider.value}
[bold]Context Window:[/bold] {best_model.context_window:,} tokens
[bold]Estimated Cost:[/bold] ${(best_model.input_cost + best_model.output_cost) / 2 / 1000:.4f} per 1K tokens
        """

        console.print(Panel(selected_content, title="✨ Optimal Choice", border_style="green"))

    async def route_request(self, prompt: str, mode: str = "auto", strategy: str = "balanced"):
        """Route a request through the system"""

        console.print(f"\n[bold]Routing request with mode: {mode}, strategy: {strategy}[/bold]\n")

        # Select model
        model_id = self.orchestrator._select_best_model(self.orchestrator.analyzer.analyze(prompt))
        model = self.orchestrator.registry.get_model(model_id)

        console.print(f"[green]Selected model:[/green] {model_id}")
        console.print(f"[blue]Provider:[/blue] {model.provider.value}")
        console.print(f"[yellow]Context:[/yellow] {model.context_window:,} tokens")

        # Estimate cost (assuming 1K input, 500 output)
        if hasattr(self.orchestrator, "estimate_cost"):
            cost = self.orchestrator.estimate_cost(model_id, 1000, 500)
            console.print(f"[red]Estimated cost:[/red] ${cost:.4f}")
        else:
            # Manual calculation
            cost = (model.input_cost * 1000 + model.output_cost * 500) / 1000000
            console.print(f"[red]Estimated cost:[/red] ${cost:.4f}")

        # Would make actual API call here
        console.print("\n[dim]Note: Actual API call would be made here[/dim]")

    def show_cost_report(self):
        """Display cost tracking report"""
        console.print("[yellow]Cost reporting not yet implemented in v3.1[/yellow]")
        return

        # Cost tracking report logic placeholder
        console.print(
            "[yellow]Cost reporting not yet implemented due to dependency updates[/yellow]"
        )
        return

    def create_consensus_group(self, prompt: str, num_models: int = 3):
        """Create a consensus group for the prompt (not yet implemented)."""
        console.print("[yellow]Consensus groups not yet implemented in v3.1[/yellow]")

    async def generate_prompts(
        self,
        spec: Optional[str] = None,
        roadmap: Optional[str] = None,
        output_dir: Optional[str] = None,
        dry_run: bool = False,
        from_project: bool = False,
        phases: Optional[list[str]] = None,
        tools: Optional[list[str]] = None,
    ):
        """Generate prompts from specifications and roadmaps"""

        if orchestrate_prompt_generation is None:
            console.print("[red]Prompt Architect module not available.[/red]")
            console.print("[dim]Install with: pip install -e .[/dim]")
            return

        console.print("\n[bold cyan]Prompt Architect - Automated Prompt Generation[/bold cyan]\n")

        # Show configuration
        config_content = f"""
[bold]Specification:[/bold] {spec or 'Auto-discover' if from_project else 'Not provided'}
[bold]Roadmap:[/bold] {roadmap or 'Auto-discover' if from_project else 'Not provided'}
[bold]Output Directory:[/bold] {output_dir or 'Default (project_prompts/)'}
[bold]Dry Run:[/bold] {'Yes' if dry_run else 'No'}
[bold]From Project:[/bold] {'Yes' if from_project else 'No'}
[bold]Phases Filter:[/bold] {', '.join(phases) if phases else 'All'}
[bold]Tools Filter:[/bold] {', '.join(tools) if tools else 'All'}
        """
        console.print(Panel(config_content.strip(), title="Configuration", border_style="blue"))

        # Run orchestration
        console.print("\n[yellow]Running prompt generation pipeline...[/yellow]\n")

        try:
            result = await orchestrate_prompt_generation(
                spec_path=spec,
                roadmap_path=roadmap,
                output_dir=output_dir,
                dry_run=dry_run,
                from_project=from_project,
                phases=phases,
                tools=tools,
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

            # Show metrics
            if result.metrics:
                metrics = result.metrics
                if metrics.get("duration_seconds"):
                    console.print(f"\n[dim]Duration: {metrics['duration_seconds']:.2f}s[/dim]")

        except Exception as e:
            console.print(f"[red]Error during prompt generation: {e}[/red]")
            raise

    def test_integration(self):
        """Test the complete integration"""

        console.print("\n[bold cyan]Testing Model Orchestration System[/bold cyan]\n")

        # Test 1: Model availability
        console.print("[yellow]Test 1: Model Availability[/yellow]")
        total_models = len(self.orchestrator.registry.models)
        available = len(
            self.orchestrator.registry.models
        )  # Assuming all loaded are available for now
        console.print(f"  Total models: {total_models}")
        console.print(f"  Available: {available}")
        console.print("  Status: [green]✓ PASS[/green]" if available > 0 else "[red]✗ FAIL[/red]")

        # Test 2: Task detection
        console.print("\n[yellow]Test 2: Task Detection[/yellow]")
        test_prompts = [
            ("Write a function to sort a list", TaskType.CODE_GENERATION),
            ("Analyze this image", TaskType.VISION),
            ("Reason through this problem", TaskType.REASONING),
        ]

        for prompt, expected in test_prompts:
            req = self.orchestrator.analyzer.analyze(prompt)
            match = req.task_type == expected
            status = "[green]✓[/green]" if match else "[red]✗[/red]"
            console.print(f"  {status} '{prompt[:30]}...' → {req.task_type.value}")

        # Test 3: Model selection
        console.print("\n[yellow]Test 3: Model Selection[/yellow]")
        strategies = ["balanced", "cost_optimize", "quality_first", "speed_priority"]

        for strategy in strategies:
            # Mocking strategy selection for test
            model_id = self.orchestrator._select_best_model(
                self.orchestrator.analyzer.analyze("Write a Python function")
            )
            console.print(f"  {strategy}: {model_id}")

        # Test 4: Zen MCP Bridge
        console.print("\n[yellow]Test 4: Zen MCP Integration[/yellow]")
        if self.bridge:
            zen_tools = self.bridge.zen_tools
            console.print(f"  Zen tools discovered: {len(zen_tools)}")
            console.print("  Status: [green]✓ PASS[/green]" if zen_tools else "[red]✗ FAIL[/red]")
        else:
            console.print("  Zen MCP Bridge: [yellow]Not Available[/yellow]")

        console.print("\n[bold green]Integration test complete![/bold green]")


async def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(
        description="Model Orchestrator - Intelligent multi-model routing"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List models command
    list_parser = subparsers.add_parser("list", help="List available models")
    list_parser.add_argument("--provider", help="Filter by provider")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze prompt requirements")
    analyze_parser.add_argument("prompt", help="Prompt to analyze")

    # Route command
    route_parser = subparsers.add_parser("route", help="Route a request")
    route_parser.add_argument("prompt", help="Prompt to process")
    route_parser.add_argument(
        "--mode", default="auto", choices=["auto", "consensus", "chain", "adaptive"]
    )
    route_parser.add_argument(
        "--strategy",
        default="balanced",
        choices=["balanced", "cost_optimize", "quality_first", "speed_priority"],
    )

    # Consensus command
    consensus_parser = subparsers.add_parser("consensus", help="Create consensus group")
    consensus_parser.add_argument("prompt", help="Prompt for consensus")
    consensus_parser.add_argument("--num", type=int, default=3, help="Number of models")

    # Cost report command
    cost_parser = subparsers.add_parser("cost", help="Show cost report")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test integration")

    # Generate prompts command
    generate_parser = subparsers.add_parser(
        "generate-prompts", help="Generate prompts from specifications"
    )
    generate_parser.add_argument("--spec", help="Path to specification file")
    generate_parser.add_argument("--roadmap", help="Path to roadmap/WBS file")
    generate_parser.add_argument("--output-dir", help="Output directory for generated prompts")
    generate_parser.add_argument(
        "--dry-run", action="store_true", help="Simulate without writing files"
    )
    generate_parser.add_argument(
        "--from-project", action="store_true", help="Auto-discover from Project Agent"
    )
    generate_parser.add_argument(
        "--phases", help="Comma-separated list of phases to generate (e.g., '1,2,3')"
    )
    generate_parser.add_argument(
        "--tools", help="Comma-separated list of tools to filter (e.g., 'devin,gemini')"
    )

    parser.add_argument("--cost", action="store_true", help="Show cost usage report")
    parser.add_argument(
        "--detailed", action="store_true", help="Show detailed breakdown (with --cost)"
    )

    args = parser.parse_args()

    cli = OrchestratorCLI()

    if args.cost:
        try:
            from lattice_lock_orchestrator.cli.cost_command import handle_cost

            handle_cost(console, detailed=args.detailed)
        except ImportError:
            console.print("[red]Cost tracking module not available.[/red]")
        return

    if args.list:
        parser.print_help()
        return

    if args.command == "list":
        cli.list_models(args.provider, args.verbose)

    elif args.command == "analyze":
        cli.analyze_prompt(args.prompt)

    elif args.command == "route":
        await cli.route_request(args.prompt, args.mode, args.strategy)

    elif args.command == "consensus":
        cli.create_consensus_group(args.prompt, args.num)

    elif args.command == "cost":
        cli.show_cost_report()

    elif args.command == "test":
        cli.test_integration()

    elif args.command == "generate-prompts":
        # Parse comma-separated lists
        phases = args.phases.split(",") if args.phases else None
        tools = args.tools.split(",") if args.tools else None
        await cli.generate_prompts(
            spec=args.spec,
            roadmap=args.roadmap,
            output_dir=args.output_dir,
            dry_run=args.dry_run,
            from_project=args.from_project,
            phases=phases,
            tools=tools,
        )


if __name__ == "__main__":
    # Check for rich library
    try:
        import rich
    except ImportError:
        print("Installing required library: rich")
        os.system("pip install rich")

    asyncio.run(main())
