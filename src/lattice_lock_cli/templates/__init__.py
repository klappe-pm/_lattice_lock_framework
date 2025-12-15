"""
Lattice Lock CLI Templates

Template loader and renderer for project scaffolding.
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

# Get the templates directory path
TEMPLATES_DIR = Path(__file__).parent


def get_template_env() -> Environment:
    """Get the Jinja2 environment configured for the templates directory."""
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=("html", "htm", "xml"), default_for_string=False, default=False),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def get_template(name: str) -> Template:
    """Load a template by name.

    Args:
        name: Template path relative to templates directory (e.g., 'base/lattice.yaml.j2')

    Returns:
        Jinja2 Template object
    """
    env = get_template_env()
    return env.get_template(name)


def render_template(name: str, context: dict[str, Any]) -> str:
    """Render a template with the given context.

    Args:
        name: Template path relative to templates directory
        context: Dictionary of variables to pass to the template

    Returns:
        Rendered template as string
    """
    template = get_template(name)
    return template.render(**context)


def get_templates_for_type(project_type: str) -> list[str]:
    """Get list of template files for a project type.

    Args:
        project_type: One of 'agent', 'service', or 'library'

    Returns:
        List of template paths to render for this project type
    """
    # Base templates used by all project types
    base_templates = [
        "base/lattice.yaml.j2",
        "base/readme.md.j2",
        "base/gitignore.j2",
        "ci/github_workflow.yml.j2",
    ]

    # Type-specific templates
    type_templates = {
        "agent": ["agent/agent_definition.yaml.j2"],
        "service": ["service/service_scaffold.py.j2"],
        "library": ["library/lib_init.py.j2"],
    }

    return base_templates + type_templates.get(project_type, [])


__all__ = ["get_template", "render_template", "get_templates_for_type", "TEMPLATES_DIR"]
