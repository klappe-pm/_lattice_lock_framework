"""
Lattice Lock CLI Compile Command

Compiles lattice.yaml schemas into enforcement artifacts including
Pydantic models, SQLModel ORM classes, and Gauntlet test contracts.
"""

import sys
from pathlib import Path

import click
from lattice_lock.compile import CompilationResult, compile_lattice
from rich.console import Console
from rich.table import Table

console = Console()


def _print_result(result: CompilationResult, verbose: bool = False) -> None:
    """Print compilation result with colorful output."""
    if result.success:
        console.print("[green]Compilation successful![/green]")
    else:
        console.print("[red]Compilation failed![/red]")

    if result.generated_files:
        table = Table(title="Generated Files")
        table.add_column("File", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Entity", style="green")

        for gen_file in result.generated_files:
            table.add_row(
                str(gen_file.path),
                gen_file.file_type,
                gen_file.entity_name or "-",
            )

        console.print(table)

    if result.warnings:
        console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/yellow]")
        for warning in result.warnings:
            console.print(f"  [yellow]- {warning}[/yellow]")

    if result.errors:
        console.print(f"\n[red]Errors ({len(result.errors)}):[/red]")
        for error in result.errors:
            console.print(f"  [red]- {error}[/red]")

    if verbose and result.validation_result:
        console.print("\n[dim]Validation Details:[/dim]")
        console.print(f"  Valid: {result.validation_result.valid}")
        console.print(f"  Errors: {len(result.validation_result.errors)}")
        console.print(f"  Warnings: {len(result.validation_result.warnings)}")


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

    console.print(f"[bold]Compiling schema:[/bold] {schema_path}")

    if output:
        console.print(f"[bold]Output directory:[/bold] {output}")

    console.print()

    result = compile_lattice(
        schema_path=schema_path,
        output_dir=output,
        generate_pydantic=pydantic,
        generate_sqlmodel=sqlmodel,
        generate_gauntlet=gauntlet,
    )

    _print_result(result, verbose)

    if not result.success:
        sys.exit(1)

    console.print()
    console.print(f"[green]Generated {len(result.generated_files)} file(s)[/green]")
