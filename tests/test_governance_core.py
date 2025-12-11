import sys
import os
import pytest
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath("src"))

from lattice_lock.core.compiler import compile_lattice

def test_compiler_pipeline():
    """Test the full compilation pipeline with the example file."""
    base_dir = Path(os.getcwd())
    source_path = base_dir / "examples" / "lattice.yaml"
    output_dir = base_dir / "src" / "generated"
    test_dir = base_dir / "tests" / "gauntlet"
    
    # Ensure dirs exist
    output_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nCompiling {source_path}...")
    result = compile_lattice(str(source_path), str(output_dir), str(test_dir))
    
    # Output errors/warnings for debug
    for err in result.errors:
        print(f"ERROR: {err}")
    for warn in result.warnings:
        print(f"WARN: {warn}")
        
    assert result.success, "Compilation failed"
    # Basic validation of result
    assert result.errors == []
    print("Compilation successful!")

if __name__ == "__main__":
    # Allow running as a script
    try:
        test_compiler_pipeline()
        print("✅ Governance Core Test PASSED")
    except AssertionError as e:
        print(f"❌ Governance Core Test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)
