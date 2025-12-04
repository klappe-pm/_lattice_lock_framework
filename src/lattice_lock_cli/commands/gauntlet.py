import click
import sys
import pytest
from pathlib import Path
from lattice_lock_gauntlet.generator import GauntletGenerator

@click.command()
@click.option("--generate", is_flag=True, help="Generate tests from lattice.yaml without running them.")
@click.option("--run/--no-run", default=True, help="Run the tests (default: True).")
@click.option("--output", default="tests/gauntlet", help="Directory to output generated tests.")
@click.option("--lattice", default="lattice.yaml", help="Path to lattice.yaml file.")
@click.option("--coverage", is_flag=True, help="Enable coverage reporting.")
@click.pass_context
def gauntlet_command(ctx: click.Context, generate: bool, run: bool, output: str, lattice: str, coverage: bool) -> None:
    """Gauntlet: Generate and run semantic tests from lattice.yaml."""
    
    # Logic:
    # If --generate is passed, we generate.
    # The prompt says "--generate flag to generate tests without running".
    # This implies if --generate is present, run should be False unless explicitly forced?
    # Or maybe it just means "the generate flag exists to do generation".
    # Let's interpret:
    # `gauntlet` -> Run (generate=False, run=True)
    # `gauntlet --generate` -> Generate ONLY (generate=True, run=False?) 
    #   - If I use default=True for run, `gauntlet --generate` will have run=True.
    #   - I need to know if user explicitly disabled run or if I should disable it because of generate.
    
    # Let's check ctx.get_parameter_source for 'run'.
    # But simpler: If generate is True, we disable run unless user explicitly said --run.
    # Actually, standard CLI: `command --generate` usually just does that task.
    
    # Let's use this logic:
    # If generate is True, we generate.
    # If run is True, we run.
    # BUT, if generate is True, we want to default run to False?
    # Let's change the default of run to None (or False) and infer?
    # No, prompt says "run existing tests (default)".
    
    # Let's stick to the flags.
    # If user types `lattice-lock gauntlet --generate`, they get generation AND run (since run defaults to True).
    # If they want ONLY generation, they'd type `lattice-lock gauntlet --generate --no-run`.
    # This satisfies the requirements technically.
    # HOWEVER, "generate tests without running" phrasing suggests --generate might imply no run.
    # Let's implement a check: if generate is True, and run is default (True), we skip run?
    # No, that's magic.
    # Let's just implement the flags as is.
    # Wait, the prompt says: "--generate flag to generate tests without running".
    # This strongly implies that using --generate STOPS execution.
    
    if generate:
        click.echo(f"Generating tests from {lattice} into {output}...")
        try:
            generator = GauntletGenerator(lattice_file=lattice, output_dir=output)
            generator.generate()
            click.echo("Generation complete.")
        except Exception as e:
            click.echo(f"Error generating tests: {e}", err=True)
            ctx.exit(1)
            
        # If generate was specified, we stop here UNLESS --run was explicitly requested?
        # Let's look at the prompt again.
        # "Create... --generate flag to generate tests without running"
        # This sounds like an exclusive mode.
        if ctx.get_parameter_source("run").name == "DEFAULT":
             # User didn't specify --run or --no-run.
             # Since we generated, we assume we're done.
             return

    if run:
        if not Path(output).exists():
            click.echo(f"Test directory {output} does not exist. Did you mean to use --generate?", err=True)
            ctx.exit(1)

        click.echo(f"Running tests in {output}...")
        pytest_args = [output]
        
        if coverage:
            pytest_args.extend(["--cov", "--cov-report=term-missing"])
            
        # Run pytest
        # We use sys.exit to pass the exit code back
        retcode = pytest.main(pytest_args)
        if retcode != 0:
            ctx.exit(retcode)
