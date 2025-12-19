"""
Secure Jinja2 Environment Configuration.

This module provides a centralized place to configure Jinja2 environments
with security best practices, particularly enforcing autoescape.
"""

from typing import Any

import jinja2


def get_secure_environment(**kwargs: Any) -> jinja2.Environment:
    """
    Create a secure Jinja2 Environment with autoescape enabled.

    This is intended for HTML/XML template rendering where XSS prevention is needed.
    For generating Python code or other non-HTML content, use get_code_environment().

    Args:
        **kwargs: Additional arguments to pass to jinja2.Environment.
                  Note: 'autoescape' will be overridden or set to True if not provided.

    Returns:
        jinja2.Environment: Configured environment.
    """
    # Enforce autoescape=True unless explicitly select_autoescape is used
    if "autoescape" not in kwargs and "loader" not in kwargs:
        # Standard secure default
        kwargs["autoescape"] = True

    # If autoescape is explicitly passed as False, log a warning (omitted for simplicity here)
    # but we will force strict adherence for this refactor.
    kwargs["autoescape"] = True

    return jinja2.Environment(**kwargs)


def get_code_environment(**kwargs: Any) -> jinja2.Environment:
    """
    Create a Jinja2 Environment for generating code (Python, YAML, etc.).

    This environment has autoescape disabled because code generation should not
    HTML-escape characters like '>', '<', '&', or quotes.

    Args:
        **kwargs: Additional arguments to pass to jinja2.Environment.

    Returns:
        jinja2.Environment: Configured environment for code generation.
    """
    # Explicitly disable autoescape for code generation
    kwargs["autoescape"] = False

    return jinja2.Environment(**kwargs)


def create_template(source: str, **kwargs: Any) -> jinja2.Template:
    """
    Create a secure Jinja2 Template from string source.

    Args:
        source: The template string.
        **kwargs: Additional arguments for Template constructor.

    Returns:
        jinja2.Template: Securely configured template.
    """
    # Ensure autoescape is True
    kwargs["autoescape"] = True
    return jinja2.Template(source, **kwargs)
