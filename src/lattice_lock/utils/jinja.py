"""
Secure Jinja2 utilities.

Provides functions to create secure Jinja2 environments and templates,
enforcing autoescape to prevent XSS.
"""
from typing import Any
import jinja2

def get_secure_environment(**kwargs: Any) -> jinja2.Environment:
    """
    Create a secure Jinja2 Environment with autoescape enabled by default.
    
    Args:
        **kwargs: Arguments to pass to jinja2.Environment constructor.
        
    Returns:
        jinja2.Environment: Configured environment.
    """
    # Enforce autoescape=True if not specified (and not using a specific loader that might handle it, though we prefer explicit)
    # Actually, we should check if autoescape is provided.
    if "autoescape" not in kwargs:
        # Default to True for security
        kwargs["autoescape"] = True
    
    return jinja2.Environment(**kwargs)

def create_template(source: str, **kwargs: Any) -> jinja2.Template:
    """
    Create a secure Jinja2 Template from string source.
    
    Args:
        source: Template source string.
        **kwargs: Arguments to pass to jinja2.Template constructor.
        
    Returns:
        jinja2.Template: Configured template.
    """
    if "autoescape" not in kwargs:
        kwargs["autoescape"] = True
    return jinja2.Template(source, **kwargs)
