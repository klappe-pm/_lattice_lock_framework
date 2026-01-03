"""
Lattice Lock CLI Config Commands

Commands for managing YAML configuration files with inheritance.
"""

import json
from pathlib import Path

import click
from rich.syntax import Syntax
from rich.tree import Tree

from lattice_lock.cli.utils.console import get_console

console = get_console()


def _get_compiler(base_path: str = None):
    """Lazy import to avoid circular dependencies."""
    from lattice_lock.config.compiler import YAMLCompiler
    return YAMLCompiler(base_path=base_path)


@click.group()
def config_command():
    """Manage YAML configuration files with inheritance."""
    pass


@config_command.command("compile")
@click.argument("config_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(resolve_path=True, path_type=Path), default=None)
@click.option("--base-path", "-b", type=click.Path(exists=True, resolve_path=True, path_type=Path), default=None)
@click.option("--pretty/--minified", default=True)
@click.pass_context
def compile_config(ctx: click.Context, config_path: Path, output: Path | None, base_path: Path | None, pretty: bool):
    """Compile a YAML config file with inheritance to JSON."""
    verbose = ctx.obj.get("VERBOSE", False) if ctx.obj else False
    console.set_verbose(verbose)
    
    try:
        compiler = _get_compiler(str(base_path) if base_path else str(config_path.parent))
        result = compiler.compile(str(config_path))
        
        indent = 2 if pretty else None
        json_output = json.dumps(result, indent=indent, default=str)
        
        if output:
            output.write_text(json_output)
            console.success(f"Compiled config written to {output}")
        else:
            syntax = Syntax(json_output, "json", theme="monokai", line_numbers=True)
            console.internal_console.print(syntax)
    except Exception as e:
        console.error("Compilation Failed", str(e))
        raise click.Abort()


@config_command.command("validate")
@click.argument("config_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@click.option("--base-path", "-b", type=click.Path(exists=True, resolve_path=True, path_type=Path), default=None)
@click.pass_context
def validate_config(ctx: click.Context, config_path: Path, base_path: Path | None):
    """Validate a YAML config file for inheritance errors."""
    verbose = ctx.obj.get("VERBOSE", False) if ctx.obj else False
    console.set_verbose(verbose)
    
    try:
        compiler = _get_compiler(str(base_path) if base_path else str(config_path.parent))
        result = compiler.compile(str(config_path))
        
        frontmatter = result.get('_meta', {}).get('frontmatter', {})
        console.success(f"Configuration is valid: {config_path}")
        console.info(f"  Extends: {frontmatter.get('extends', 'None')}")
        console.info(f"  Mixins: {len(frontmatter.get('mixins', []))}")
        console.info(f"  Variables: {len(frontmatter.get('vars', {}))}")
    except FileNotFoundError as e:
        console.error("Missing File", str(e))
        raise click.Abort()
    except ValueError as e:
        console.error("Validation Failed", str(e))
        raise click.Abort()


@config_command.command("inspect")
@click.argument("config_path", type=click.Path(exists=True, resolve_path=True, path_type=Path))
@click.option("--show-inheritance", "-i", is_flag=True)
@click.option("--base-path", "-b", type=click.Path(exists=True, resolve_path=True, path_type=Path), default=None)
@click.pass_context
def inspect_config(ctx: click.Context, config_path: Path, show_inheritance: bool, base_path: Path | None):
    """Inspect a YAML config file and show its structure."""
    verbose = ctx.obj.get("VERBOSE", False) if ctx.obj else False
    console.set_verbose(verbose)
    
    try:
        compiler = _get_compiler(str(base_path) if base_path else str(config_path.parent))
        result = compiler.compile(str(config_path))
        
        meta = result.get('_meta', {})
        frontmatter = meta.get('frontmatter', {})
        
        console.info(f"Configuration: {config_path}")
        console.internal_console.print()
        console.internal_console.print("[bold]Metadata:[/bold]")
        console.internal_console.print(f"  Source: {meta.get('source', 'N/A')}")
        console.internal_console.print(f"  Version: {meta.get('version', 'N/A')}")
        
        if show_inheritance:
            console.internal_console.print()
            console.internal_console.print("[bold]Inheritance Chain:[/bold]")
            tree = Tree(f"[cyan]{config_path.name}[/cyan]")
            if frontmatter.get('extends'):
                tree.add(f"[green]extends:[/green] {frontmatter['extends']}")
            if frontmatter.get('mixins'):
                mixins_node = tree.add("[green]mixins:[/green]")
                for mixin in frontmatter['mixins']:
                    mixins_node.add(f"[dim]{mixin}[/dim]")
            console.internal_console.print(tree)
        
        if frontmatter.get('vars'):
            console.internal_console.print()
            console.internal_console.print("[bold]Variables:[/bold]")
            for key, value in frontmatter['vars'].items():
                console.internal_console.print(f"  {key}: {value}")
    except Exception as e:
        console.error("Inspection Failed", str(e))
        raise click.Abort()
