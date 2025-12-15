import os
from pathlib import Path
from typing import Union

def resolve_under_root(path: Union[str, Path], root: Union[str, Path] = None) -> Path:
    """
    Securely resolve a path aimed at a root directory, preventing traversal out of it.
    
    Args:
        path: The path to resolve.
        root: The root directory to confine the path to. Defaults to current working directory.
        
    Returns:
        The resolved absolute path.
        
    Raises:
        ValueError: If the resolved path is outside the root directory.
    """
    if root is None:
        root = Path.cwd()
    else:
        root = Path(root).resolve()
        
    # Join path to root (handles absolute paths by ignoring root if path is absolute, 
    # but we want to ensure it's under root, so we should be careful)
    # If path is allowed to be absolute but must be under root, we check after resolve.
    # If path is relative, we join.
    
    requested_path = Path(path)
    if not requested_path.is_absolute():
        requested_path = root / requested_path
        
    resolved_path = requested_path.resolve()
    
    if not str(resolved_path).startswith(str(root)):
        raise ValueError(f"Path traversal detected: {path} is outside of {root}")
        
    return resolved_path
