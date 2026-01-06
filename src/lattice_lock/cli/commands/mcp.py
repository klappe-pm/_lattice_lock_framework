"""
MCP Server Command.
"""

import asyncio

import click

from lattice_lock.cli.utils.console import get_console


@click.command()
@click.option(
    "--transport", "-t", type=click.Choice(["stdio", "sse"]), default="stdio", help="Transport mode"
)
def mcp_command(transport: str):
    """Start the Model Context Protocol (MCP) server."""
    console = get_console()

    if transport == "sse":
        console.print("[red]SSE transport not yet implemented for this PR.[/red]")
        return

    # Lazy import to avoid hard dependency if feature is disabled/missing
    try:
        from lattice_lock.mcp.server import LatticeMCPServer
    except ImportError:
        console.print(
            "[red]MCP dependencies not found. Install with 'pip install lattice-lock[mcp]'[/red]"
        )
        return

    console.print("[bold green]Starting Lattice MCP Server (stdio)...[/bold green]", style="dim")

    # Run server
    server = LatticeMCPServer()
    asyncio.run(server.run_stdio())
