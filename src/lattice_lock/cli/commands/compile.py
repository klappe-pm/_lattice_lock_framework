"""
Lattice Lock CLI Compile Command

Compiles lattice.yaml schemas into enforcement artifacts including
Pydantic models, SQLModel ORM classes, and Gauntlet test contracts.
"""

import sys
import time
from pathlib import Path

import click
from rich.table import Table

from lattice_lock.compile import CompilationResult, compile_lattice
from lattice_lock.cli.utils.console import get_console

console = get_console()


def _print_result(result: CompilationResult, duration: float, verbose: bool = False) -> None:
    """Print compilation result with colorful output."""

    if result.success:
        console.success(f"Compilation successful in {duration:.2f}s")
    else:
        console.error(
            "Compilation Failed",
            "The schema compilation process encountered errors.",
            "Check the error list below and fix schema issues.",
        )

    if result.generated_files:
        table = Table(title="Generated Files", box=None, show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Entity", style="spring_green1")

        for gen_file in result.generated_files:
            table.add_row(
                str(gen_file.path),
                gen_file.file_type,
                gen_file.entity_name or "-",
            )

        console.internal_console.print(table)
        console.internal_console.print()

    if result.warnings:
        console.warning(f"Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            console.internal_console.print(f"  [yellow]- {warning}[/yellow]")

    if result.errors:
        console.internal_console.print(f"\n[bold red]Errors ({len(result.errors)}):[/bold red]")
        for error in result.errors:
            console.internal_console.print(f"  [red]- {error}[/red]")

    if verbose and result.validation_result:
        console.internal_console.print("\n[dim]Validation Details:[/dim]")
        console.internal_console.print(f"  Valid: {result.validation_result.valid}")
        console.internal_console.print(f"  Errors: {len(result.validation_result.errors)}")
        console.internal_console.print(f"  Warnings: {len(result.validation_result.warnings)}")


@click.command()
@click.argument(
    "schema_path",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    default="lattice.yaml",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(resolve_path=True, path_type=Path),
    default=None,
    help="Output directory for generated files (default: same as schema)",
)
@click.option(
    "--pydantic/--no-pydantic",
    default=True,
    help="Generate Pydantic models (default: enabled)",
)
@click.option(
    "--sqlmodel/--no-sqlmodel",
    default=False,
    help="Generate SQLModel ORM classes (default: disabled)",
)
@click.option(
    "--gauntlet/--no-gauntlet",
    default=True,
    help="Generate Gauntlet test contracts (default: enabled)",
)
@click.pass_context
def compile_command(
    ctx: click.Context,
    schema_path: Path,
    output: Path | None,
    pydantic: bool,
    sqlmodel: bool,
    gauntlet: bool,
) -> None:
    """Compile a lattice.yaml schema into enforcement artifacts.

    Generates Pydantic models, SQLModel ORM classes, and Gauntlet test
    contracts from the schema definition.

    SCHEMA_PATH: Path to lattice.yaml file (default: ./lattice.yaml)
    """
    verbose = ctx.obj.get("VERBOSE", False) if ctx.obj else False
    console.set_verbose(verbose)

    if output:
        console.info(f"Output directory: {output}")

    start_time = time.time()

    with console.internal_console.status("[bold cyan]Compiling lattice.yaml...[/]") as status:
        status.update("[bold cyan]Reading and validating schema...[/]")
        # Simulate some steps if logical separation existed,
        # but compile_lattice does it all.

        result = compile_lattice(
            schema_path=schema_path,
            output_dir=output,
            generate_pydantic=pydantic,
            generate_sqlmodel=sqlmodel,
            generate_gauntlet=gauntlet,
        )

        status.update("[bold cyan]Finalizing...[/]")

    end_time = time.time()
    duration = end_time - start_time

    _print_result(result, duration, verbose)

    if not result.success:
        sys.exit(1)
