"""
Lattice Lock CLI Templates

Template loader and renderer for project scaffolding.
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template
from lattice_lock.utils.jinja import get_secure_environment

# Get the templates directory path
TEMPLATES_DIR = Path(__file__).parent


def get_template_env() -> Environment:
    """Get the Jinja2 environment configured for the templates directory."""
    return get_secure_environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        # get_secure_environment sets autoescape=True by default.
        # If we need specific extensions, we can pass autoescape=select_autoescape(...)
        # but the secure wrapper might enforce True.
        # Let's check get_secure_environment signature from previous view_file.
        # It takes **kwargs and sets autoescape=True if missing.
        # If we pass autoescape, it might be overridden?
        # get_secure_environment implementation:
        # if "autoescape" not in kwargs: kwargs["autoescape"] = True
        # kwargs["autoescape"] = True <--- It FORCES True at the end!
        # So passing select_autoescape might be ignored or overwritten.
        # Let's trust the secure env wrapper.
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
