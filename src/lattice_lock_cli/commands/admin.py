"""
Lattice Lock CLI Admin Command

Command to start the Admin API server for project monitoring and management.
"""

import click


@click.command()
@click.option(
    "--host",
    "-h",
    default="127.0.0.1",
    show_default=True,
    help="Host to bind the server to",
)
@click.option(
    "--port",
    "-p",
    default=8080,
    show_default=True,
    type=int,
    help="Port to listen on",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development",
)
@click.option(
    "--cors-origins",
    multiple=True,
    help="Allowed CORS origins (can be specified multiple times)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode with verbose logging",
)
@click.pass_context
def admin_command(
    ctx: click.Context,
    host: str,
    port: int,
    reload: bool,
    cors_origins: tuple[str, ...],
    debug: bool,
) -> None:
    """Start the Admin API server.

    The Admin API provides REST endpoints for monitoring and managing
    Lattice Lock projects. It supports project registration, health
    monitoring, error tracking, and rollback management.

    Examples:

        # Start on default port (8080)
        lattice-lock admin

        # Start on custom port
        lattice-lock admin --port 9000

        # Start in development mode with auto-reload
        lattice-lock admin --reload --debug

        # Allow specific CORS origins
        lattice-lock admin --cors-origins http://localhost:3000

    API Documentation:

        Once running, visit http://HOST:PORT/docs for interactive API docs.
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    # Use verbose flag if debug not explicitly set
    if verbose and not debug:
        debug = True

    click.echo(click.style("Lattice Lock Admin API", fg="cyan", bold=True))
    click.echo()
    click.echo(f"Starting server on {host}:{port}")

    if reload:
        click.echo(click.style("  Auto-reload enabled", fg="yellow"))
    if debug:
        click.echo(click.style("  Debug mode enabled", fg="yellow"))

    click.echo()
    click.echo("API Documentation: " + click.style(f"http://{host}:{port}/docs", fg="green"))
    click.echo("Health Check: " + click.style(f"http://{host}:{port}/api/v1/health", fg="green"))
    click.echo()
    click.echo("Press Ctrl+C to stop the server")
    click.echo()

    # Convert cors_origins tuple to list or None
    origins = list(cors_origins) if cors_origins else None

    try:
        from lattice_lock.admin import run_server

        run_server(
            host=host,
            port=port,
            reload=reload,
            cors_origins=origins,
            debug=debug,
        )
    except ImportError as e:
        click.echo(
            click.style("Error: ", fg="red") + "FastAPI and uvicorn are required for the Admin API."
        )
        click.echo("Install them with: pip install fastapi uvicorn")
        click.echo()
        click.echo(f"Details: {e}")
        raise SystemExit(1)
    except KeyboardInterrupt:
        click.echo()
        click.echo(click.style("Server stopped", fg="yellow"))
