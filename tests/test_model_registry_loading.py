import os
import sys

# Add src to path
sys.path.append(os.path.abspath("src"))

from lattice_lock_orchestrator.registry import ModelRegistry
from lattice_lock_orchestrator.types import ModelStatus, ProviderMaturity


def test_registry_load_yaml():
    """Test loading from the actual registry.yaml file."""
    print("\nTesting YAML loading...")

    # Point to the real file we just created
    registry_path = os.path.abspath("docs/models/registry.yaml")
    registry = ModelRegistry(registry_path=registry_path)

    # Check if loaded
    assert "gpt-4o" in registry.models
    model = registry.get_model("gpt-4o")

    assert model.name == "gpt-4o"
    assert model.status == ModelStatus.ACTIVE
    assert model.maturity == ProviderMaturity.PRODUCTION
    assert model.supports_vision is True
    assert model.supports_function_calling is True

    print("✅ YAML loading verified (gpt-4o)")


def test_registry_fallback():
    """Test fallback to defaults when YAML is missing."""
    print("\nTesting Fallback logic...")

    # Point to non-existent file
    registry = ModelRegistry(registry_path="non_existent.yaml")

    # Should still have models from defaults
    assert "grok-3" in registry.models
    # Defaults don't have explicit status in the hardcoded methods unless we updated them?
    # Actually we didn't update the hardcoded methods to set status, so it should default or be missing if not passed.
    # checking types.py: status: ModelStatus = ModelStatus.ACTIVE (default value)
    model = registry.get_model("grok-3")
    assert model.status == ModelStatus.ACTIVE  # Default value from dataclass

    print("✅ Fallback logic verified")


if __name__ == "__main__":
    try:
        test_registry_load_yaml()
        test_registry_fallback()
        print("\nALL REGISTRY TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ Registry Test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
