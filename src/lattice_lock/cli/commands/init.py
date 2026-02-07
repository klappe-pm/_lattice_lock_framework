"""
Lattice Lock CLI Init Command

Scaffolds new projects with compliant directory structures.
"""

import re
from pathlib import Path

import click

from ..templates import render_template


def normalize_project_name(name: str) -> str:
    """Convert project name to snake_case format.

    Args:
        name: Project name to normalize.

    Returns:
        Project name in snake_case format.
    """
    # Replace spaces and hyphens with underscores
    normalized = re.sub(r"[\s-]+", "_", name.strip())
    # Convert to lowercase
    normalized = normalized.lower()
    # Remove any non-alphanumeric/underscore characters
    normalized = re.sub(r"[^a-z0-9_]", "", normalized)
    # Ensure it starts with a letter
    if normalized and not normalized[0].isalpha():
        normalized = "p_" + normalized
    return normalized


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
    ci_provider: str | None = None,
    github_repo: str | None = None,
    with_agents: bool = False,
) -> list[Path]:
    """Create the project directory structure.

    Args:
        project_name: Name of the project.
        project_type: Type of project (agent, service, library).
        output_dir: Base directory to create project in.
        verbose: Whether to print verbose output.
        ci_provider: Optional CI provider ('aws' or 'github'). Defaults to 'github'.
        github_repo: Optional GitHub repository URL.
        with_agents: Whether to include agent scaffolding.

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
        "github_repo": github_repo or "",
    }

    # Create directory structure
    directories = [
        project_dir,
        project_dir / "src" / "shared",
        project_dir / "src" / "services",
        project_dir / "tests" / "unit",
        project_dir / "tests" / "integration",
        project_dir / "tests" / "fixtures",
        project_dir / "docs" / "01_concepts",
        project_dir / "docs" / "03_technical",
        project_dir / "docs" / "04_meta",
        project_dir / "scripts",
        project_dir / ".github" / "workflows",
    ]

    # Add AWS CI directory if aws provider selected
    if ci_provider == "aws":
        directories.append(project_dir / "ci" / "aws")
    elif ci_provider == "gcp":
        directories.append(project_dir / "ci" / "gcp")

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        if verbose:
            click.echo(f"  Created directory: {directory.relative_to(output_dir)}")

    # Create files from base templates
    file_mappings = [
        ("base/lattice.yaml.j2", project_dir / "lattice.yaml"),
        ("base/readme.md.j2", project_dir / "README.md"),
        ("base/gitignore.j2", project_dir / ".gitignore"),
        (
            "ci/github_actions/lattice_lock.yml.j2",
            project_dir / ".github" / "workflows" / "lattice-lock.yml",
        ),
    ]

    # Add type-specific files
    if project_type == "agent":
        file_mappings.append(("agent/agent_definition.yaml.j2", project_dir / "agent.yaml"))
    elif project_type == "service":
        file_mappings.append(
            (
                "service/service_scaffold.py.j2",
                project_dir / "src" / "services" / f"{project_name}.py",
            )
        )
    elif project_type == "library":
        file_mappings.append(
            ("library/lib_init.py.j2", project_dir / "src" / project_name / "__init__.py")
        )
        # Create the library package directory
        (project_dir / "src" / project_name).mkdir(parents=True, exist_ok=True)

    # Add AWS CI templates if aws provider selected
    if ci_provider == "aws":
        file_mappings.extend(
            [
                ("ci/aws/buildspec.yml.j2", project_dir / "ci" / "aws" / "buildspec.yml"),
                ("ci/aws/pipeline.yml.j2", project_dir / "ci" / "aws" / "pipeline.yml"),
                (
                    "ci/aws/codebuild_project.yml.j2",
                    project_dir / "ci" / "aws" / "codebuild-project.yml",
                ),
            ]
        )

    # Add GCP CI templates if gcp provider selected
    if ci_provider == "gcp":
        file_mappings.extend(
            [
                (
                    "ci/gcp/cloudbuild.yaml.j2",
                    project_dir / "ci" / "gcp" / "cloudbuild.yaml",
                ),
                (
                    "ci/gcp/cloudbuild_pr.yaml.j2",
                    project_dir / "ci" / "gcp" / "cloudbuild-pr.yaml",
                ),
                (
                    "ci/gcp/trigger_config.yaml.j2",
                    project_dir / "ci" / "gcp" / "trigger-config.yaml",
                ),
            ]
        )

    # Add agent scaffolding if requested
    if with_agents:
        agent_dirs = [
            project_dir / "agents" / "agent_definitions" / "agents_custom",
            project_dir / "agents" / "agent_diagrams",
            project_dir / "agents" / "agent_workflows",
            project_dir / "agents" / "agents_config",
        ]
        for agent_dir in agent_dirs:
            agent_dir.mkdir(parents=True, exist_ok=True)
            if verbose:
                click.echo(f"  Created directory: {agent_dir.relative_to(output_dir)}")

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

    # Create docs/README.md
    docs_readme = project_dir / "docs" / "README.md"
    docs_content = f"""# Documentation

This directory contains project documentation for {project_name}.

## Structure

- `01_concepts/` - Conceptual documentation, features, and architecture
- `03_technical/` - Technical documentation, API references, CLI docs
- `04_meta/` - Meta documentation about documentation standards

## Naming Convention

All documentation files must follow `lowercase_with_underscores.md` naming.
"""
    docs_readme.write_text(docs_content)
    created_files.append(docs_readme)
    if verbose:
        click.echo(f"  Created file: {docs_readme.relative_to(output_dir)}")

    # Create subdirectory READMEs
    concepts_readme = project_dir / "docs" / "01_concepts" / "README.md"
    concepts_readme.write_text(f"# Concepts\n\nConceptual documentation for {project_name}.\n")
    created_files.append(concepts_readme)

    technical_readme = project_dir / "docs" / "03_technical" / "README.md"
    technical_readme.write_text(
        f"# Technical Documentation\n\nTechnical references for {project_name}.\n"
    )
    created_files.append(technical_readme)

    meta_readme = project_dir / "docs" / "04_meta" / "README.md"
    meta_readme.write_text(f"# Meta Documentation\n\nDocumentation standards for {project_name}.\n")
    created_files.append(meta_readme)

    # Create scripts/README.md
    scripts_readme = project_dir / "scripts" / "README.md"
    scripts_content = f"""# Scripts

This directory contains utility scripts for {project_name}.

## Naming Convention

All scripts must follow `lowercase_with_underscores` naming:
- ✓ `deploy_app.sh`
- ✓ `run_tests.py`
- ✗ `deployApp.sh`
- ✗ `run-tests.py`

## Common Scripts

- Build scripts
- Deployment automation
- Development utilities
- Database migrations
"""
    scripts_readme.write_text(scripts_content)
    created_files.append(scripts_readme)
    if verbose:
        click.echo(f"  Created file: {scripts_readme.relative_to(output_dir)}")

    # Create agent scaffolding files if requested
    if with_agents:
        agents_readme = project_dir / "agents" / "README.md"
        agents_content = f"""# Agents

This directory contains agent definitions and configurations for {project_name}.

## Structure

- `agent_definitions/` - Agent YAML definitions organized by category
- `agent_diagrams/` - Agent workflow diagrams and visualizations
- `agent_workflows/` - Agent workflow specifications
- `agents_config/` - Agent configuration files

## Creating New Agents

1. Create a new category directory under `agent_definitions/`
2. Add your agent definition YAML file following the pattern: `{{category}}_{{name}}_definition.yaml`
3. Document workflows in `agent_workflows/`
4. Add diagrams to `agent_diagrams/`

## Validation

Run `lattice-lock validate` to ensure agent definitions are properly formatted.
"""
        agents_readme.write_text(agents_content)
        created_files.append(agents_readme)
        if verbose:
            click.echo(f"  Created file: {agents_readme.relative_to(output_dir)}")

        # Create example agent definition
        example_agent = (
            project_dir
            / "agents"
            / "agent_definitions"
            / "agents_custom"
            / "agents_custom_example_agent_definition.yaml"
        )
        agent_yaml_content = f"""# Example Agent Definition for {project_name}
agent:
  identity:
    name: custom_example_agent
    version: 1.0.0
    description: Example agent for {project_name} - customize as needed
    role: Custom Agent
    status: beta
    tags:
    - custom
    - example

directive:
  primary_goal: Assist with project-specific tasks following governance rules
  constraints:
  - Must follow project conventions
  - Must validate inputs  
  - Must provide clear error messages

responsibilities:
- name: task_assistance
  description: Assist with project tasks and workflows
- name: governance_enforcement
  description: Ensure governance rules are followed
- name: guidance_provision
  description: Provide clear, actionable guidance to users

scope:
  can_access:
  - /src
  - /docs
  - /tests
  can_modify:
  - /docs
  cannot_access:
  - /.env
  - /secrets
"""
        example_agent.write_text(agent_yaml_content)
        created_files.append(example_agent)
        if verbose:
            click.echo(f"  Created file: {example_agent.relative_to(output_dir)}")

    return created_files


@click.command()
@click.argument("project_name", required=False)
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
    default=None,
    help="Output directory for the project",
)
@click.option(
    "--ci",
    type=click.Choice(["github", "aws", "gcp"]),
    default="github",
    help="CI/CD provider (github, aws, or gcp)",
)
@click.option(
    "--github-repo",
    "-g",
    type=str,
    default=None,
    help="GitHub repository URL (e.g., https://github.com/user/repo)",
)
@click.option(
    "--with-agents",
    is_flag=True,
    default=False,
    help="Include agent scaffolding (agent_definitions, workflows, etc.)",
)
@click.pass_context
def init_command(
    ctx: click.Context,
    project_name: str | None,
    template: str,
    output_dir: Path | None,
    ci: str,
    github_repo: str | None,
    with_agents: bool,
) -> None:
    """Initialize a new Lattice Lock project.

    PROJECT_NAME should be in snake_case format (e.g., my_project).
    If not provided, you will be prompted for it.
    """
    verbose = ctx.obj.get("VERBOSE", False) if ctx.obj else False

    # Interactive prompts if arguments not provided
    if not project_name:
        project_name = click.prompt(
            "Project name (snake_case)",
            type=str,
        )

    if output_dir is None:
        default_path = Path.cwd()
        output_dir_str = click.prompt(
            "Project directory path",
            default=str(default_path),
            type=str,
        )
        output_dir = Path(output_dir_str).expanduser().resolve()

    if not github_repo:
        github_repo = click.prompt(
            "GitHub repository URL (optional, press Enter to skip)",
            default="",
            show_default=False,
            type=str,
        )
        if not github_repo:
            github_repo = None

    # Auto-format project name to snake_case
    original_name = project_name
    project_name = normalize_project_name(project_name)

    if original_name != project_name:
        click.echo(f"Project name formatted: '{original_name}' → '{project_name}'")

    # Validate project name (should always pass after normalization)
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
            ci_provider=ci if ci != "github" else None,
            github_repo=github_repo,
            with_agents=with_agents,
        )

        click.echo()
        click.echo(click.style("Project created successfully!", fg="green", bold=True))
        click.echo()
        click.echo(f"Created {len(created_files)} files in {project_dir}")
        click.echo()
        click.echo("Next steps:")
        click.echo(f"  cd {project_name}")
        click.echo("  python -m venv .venv")
        click.echo("  source .venv/bin/activate")
        click.echo("  pip install lattice-lock")
        click.echo("  lattice-lock validate")

    except Exception as e:
        raise click.ClickException(f"Failed to create project: {e}")
