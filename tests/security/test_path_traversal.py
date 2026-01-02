
import pytest
from pathlib import Path
from lattice_lock.mcp.tools import _validate_safe_path

def test_safe_paths():
    """Verify safe paths within project root are allowed."""
    # Current directory
    assert _validate_safe_path(".") == Path.cwd()
    # Subdirectory
    assert _validate_safe_path("src") == Path.cwd() / "src"
    # File in subdirectory
    assert _validate_safe_path("src/lattice_lock/__init__.py") == Path.cwd() / "src" / "lattice_lock" / "__init__.py"

def test_path_traversal_detection():
    """Verify paths attempting to escape root are rejected."""
    with pytest.raises(ValueError, match="Path traversal detected"):
        _validate_safe_path("../outside")
    
    with pytest.raises(ValueError, match="Path traversal detected"):
        _validate_safe_path("/etc/passwd")

    with pytest.raises(ValueError, match="Path traversal detected"):
        # Sneaky traversal
        _validate_safe_path("src/../../outside")
