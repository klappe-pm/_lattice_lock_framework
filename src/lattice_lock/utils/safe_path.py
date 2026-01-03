"""
Secure Path Handling Utilities.

This module provides utilities for secure file system path manipulation,
preventing common vulnerabilities like path traversal.
"""

from pathlib import Path


def resolve_under_root(root_path: str, relative_path: str) -> str:
    """
    Safely resolve a relative path under a root directory.

    Ensures that the resulting path is contained within the root directory.
    Prevents directory traversal attacks (e.g., using '../').

    Args:
        root_path: The base directory that acts as the root.
        relative_path: The relative path to resolve.

    Returns:
        str: The resolved absolute path.

    Raises:
        ValueError: If the resolved path is outside the root directory.
    """
    root = Path(root_path).resolve()
    # Join paths and resolve to eliminate '..' components
    try:
        requested = (root / relative_path).resolve()
    except Exception as e:
        # Path resolution might fail if components are invalid
        raise ValueError(f"Invalid path components: {e}")

    # Check common path prefix
    # Need to be careful with symlinks, but resolve() handles them by default
    # by canonicalizing the path.
    if root not in requested.parents and root != requested:
        raise ValueError(f"Path traversal attempt: {relative_path} is outside {root_path}")

    return str(requested)
