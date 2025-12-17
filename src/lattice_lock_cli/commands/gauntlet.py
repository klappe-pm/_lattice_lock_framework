from pathlib import Path

import click
import pytest

from lattice_lock_gauntlet.generator import GauntletGenerator


@click.command()
@click.option(
    "--generate", is_flag=True, help="Generate tests from lattice.yaml without running them."
)
@click.option("--run/--no-run", default=True, help="Run the tests (default: True).")
@click.option("--output", default="tests/gauntlet", help="Directory to output generated tests.")
@click.option("--lattice", default="lattice.yaml", help="Path to lattice.yaml file.")
@click.option("--coverage", is_flag=True, help="Enable coverage reporting.")
@click.option(
    "--format",
    "output_format",
    multiple=True,
    type=click.Choice(["json", "junit", "github"]),
    help="Output format(s). Can be used multiple times.",
)
@click.option(
    "--parallel",
    is_flag=False,
    flag_value="auto",
    help="Run tests in parallel. Optional: specify number of workers (default: auto).",
)
@click.pass_context
def gauntlet_command(
    ctx: click.Context,
    generate: bool,
    run: bool,
    output: str,
    lattice: str,
    coverage: bool,
    output_format: tuple,
    parallel: str,
) -> None:
    """Gauntlet: Generate and run semantic tests from lattice.yaml."""

    if generate:
        click.echo(f"Generating tests from {lattice} into {output}...")
        try:
            generator = GauntletGenerator(lattice_file=lattice, output_dir=output)
            generator.generate()
            click.echo("Generation complete.")
        except Exception as e:
            click.echo(f"Error generating tests: {e}", err=True)
            ctx.exit(1)

        if ctx.get_parameter_source("run").name == "DEFAULT":
            return

    if run:
        if not Path(output).exists():
            click.echo(
                f"Test directory {output} does not exist. Did you mean to use --generate?", err=True
            )
            ctx.exit(1)

        click.echo(f"Running tests in {output}...")
        pytest_args = [output]

        if coverage:
            pytest_args.extend(["--cov", "--cov-report=term-missing"])

        # Handle formats
        enable_json = "json" in output_format
        enable_github = "github" in output_format

        if enable_json or enable_github:
            # We need to register our plugin
            # Since we can't easily pass plugin instances to pytest.main in all versions,
            # we'll use the -p argument if it's installed, or we might need a conftest.
            # But wait, pytest.main(["-p", "my.plugin"]) works if it's importable.
            pytest_args.extend(["-p", "lattice_lock_gauntlet.plugin"])

            # We can pass configuration via environment variables or other means if the plugin needs to know flags
            # But our plugin constructor takes args.
            # A better way for CLI usage is to rely on the plugin reading env vars or just always enabling hooks
            # but checking flags.
            # Let's use environment variables to configure the plugin instance that pytest will instantiate.
            import os

            if enable_json:
                os.environ["GAUNTLET_JSON_REPORT"] = "true"
            if enable_github:
                os.environ["GAUNTLET_GITHUB_REPORT"] = "true"

        if "junit" in output_format:
            pytest_args.append("--junitxml=test-results.xml")

        # Handle parallel
        if parallel:
            # Check if pytest-xdist is installed
            try:
                import xdist  # noqa: F401

                if parallel == "auto":
                    pytest_args.extend(["-n", "auto"])
                else:
                    pytest_args.extend(["-n", parallel])
            except ImportError:
                click.echo(
                    "Warning: pytest-xdist not installed. Parallel execution disabled.", err=True
                )

        # Run pytest
        retcode = pytest.main(pytest_args)
        if retcode != 0:
            ctx.exit(retcode)
