"""
Lattice Lock CLI Init Command

Scaffolds new projects with compliant directory structures.
"""

import re
from pathlib import Path
from typing import Optional

import click

from ..templates import render_template


def validate_project_name(name: str) -> bool:
    """Validate project name follows snake_case convention.

    Args:
        name: Project name to validate.

    Returns:
        True if valid, False otherwise.
    """
    # Must be snake_case: lowercase letters, numbers, underscores
    # Must start with a letter
    pattern = r"^[a-z][a-z0-9_]*$"
    return bool(re.match(pattern, name))


def create_project_structure(
    project_name: str,
    project_type: str,
    output_dir: Path,
    verbose: bool = False,
) -> list[Path]:
    """Create the project directory structure.

    Args:
        project_name: Name of the project.
        project_type: Type of project (agent, service, library).
        output_dir: Base directory to create project in.
        verbose: Whether to print verbose output.

    Returns:
        List of created file paths.
    """
    project_dir = output_dir / project_name
    created_files: list[Path] = []

    # Template context
    context = {
        "project_name": project_name,
        "project_type": project_type,
        "description": f"A {project_type} project managed by Lattice Lock Framework",
    }

    # Create directory structure
    directories = [
        project_dir,
        project_dir / "src" / "shared",
        project_dir / "src" / "services",
        project_dir / "tests",
        project_dir / ".github" / "workflows",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        if verbose:
            click.echo(f"  Created directory: {directory.relative_to(output_dir)}")

    # Create files from base templates
    file_mappings = [
        ("base/lattice.yaml.j2", project_dir / "lattice.yaml"),
        ("base/readme.md.j2", project_dir / "README.md"),
        ("base/gitignore.j2", project_dir / ".gitignore"),
        ("ci/github_workflow.yml.j2", project_dir / ".github" / "workflows" / "lattice-lock.yml"),
    ]

    # Add type-specific files
    if project_type == "agent":
        file_mappings.append(
            ("agent/agent_definition.yaml.j2", project_dir / "agent.yaml")
        )
    elif project_type == "service":
        file_mappings.append(
            ("service/service_scaffold.py.j2", project_dir / "src" / "services" / f"{project_name}.py")
        )
    elif project_type == "library":
        file_mappings.append(
            ("library/lib_init.py.j2", project_dir / "src" / project_name / "__init__.py")
        )
        # Create the library package directory
        (project_dir / "src" / project_name).mkdir(parents=True, exist_ok=True)

    # Render and write templates
    for template_name, output_path in file_mappings:
        content = render_template(template_name, context)
        output_path.write_text(content)
        created_files.append(output_path)
        if verbose:
            click.echo(f"  Created file: {output_path.relative_to(output_dir)}")

    # Create placeholder test file
    test_file = project_dir / "tests" / "test_contracts.py"
    test_content = f'''"""
Contract tests for {project_name}.

These tests validate that the project adheres to Lattice Lock contracts.
"""

import pytest


def test_placeholder() -> None:
    """Placeholder test - replace with actual contract tests."""
    assert True


def test_project_name_valid() -> None:
    """Verify project name follows conventions."""
    project_name = "{project_name}"
    assert project_name.islower()
    assert " " not in project_name
'''
    test_file.write_text(test_content)
    created_files.append(test_file)
    if verbose:
        click.echo(f"  Created file: {test_file.relative_to(output_dir)}")

    # Create src/__init__.py
    src_init = project_dir / "src" / "__init__.py"
    src_init.write_text(f'"""{project_name} source package."""\n')
    created_files.append(src_init)

    # Create shared/__init__.py
    shared_init = project_dir / "src" / "shared" / "__init__.py"
    shared_init.write_text('"""Shared utilities and types."""\n')
    created_files.append(shared_init)

    # Create services/__init__.py
    services_init = project_dir / "src" / "services" / "__init__.py"
    services_init.write_text('"""Service implementations."""\n')
    created_files.append(services_init)

    return created_files


@click.command()
@click.argument("project_name")
@click.option(
    "--template",
    "-t",
    type=click.Choice(["agent", "service", "library"]),
    default="service",
    help="Project template type",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, resolve_path=True, path_type=Path),
    default=".",
    help="Output directory for the project",
)
@click.pass_context
def init_command(
    ctx: click.Context,
    project_name: str,
    template: str,
    output_dir: Path,
) -> None:
    """Initialize a new Lattice Lock project.

    PROJECT_NAME should be in snake_case format (e.g., my_project).
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    # Validate project name
    if not validate_project_name(project_name):
        raise click.ClickException(
            f"Invalid project name '{project_name}'. "
            "Name must be snake_case (lowercase letters, numbers, underscores) "
            "and start with a letter."
        )

    # Check if directory already exists
    project_dir = output_dir / project_name
    if project_dir.exists():
        raise click.ClickException(
            f"Directory '{project_dir}' already exists. "
            "Please choose a different name or remove the existing directory."
        )

    # Create the project
    click.echo(f"Creating {template} project '{project_name}'...")

    try:
        created_files = create_project_structure(
            project_name=project_name,
            project_type=template,
            output_dir=output_dir,
            verbose=verbose,
        )

        click.echo()
        click.echo(click.style("Project created successfully!", fg="green", bold=True))
        click.echo()
        click.echo(f"Created {len(created_files)} files in {project_dir}")
        click.echo()
        click.echo("Next steps:")
        click.echo(f"  cd {project_name}")
        click.echo("  python -m venv venv")
        click.echo("  source venv/bin/activate")
        click.echo("  pip install lattice-lock")
        click.echo("  lattice-lock validate")

    except Exception as e:
        raise click.ClickException(f"Failed to create project: {e}")
