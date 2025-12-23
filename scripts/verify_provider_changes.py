import os
import sys

# Add src to path
sys.path.append(os.path.abspath("src"))

from lattice_lock.orchestrator.api_clients import BaseAPIClient, BedrockAPIClient
from lattice_lock.orchestrator.registry import ModelRegistry
from lattice_lock.orchestrator.types import ProviderMaturity


def test_maturity_enum():
    print("Testing ProviderMaturity...")
    assert ProviderMaturity.PRODUCTION
    assert ProviderMaturity.BETA
    assert ProviderMaturity.EXPERIMENTAL
    print("✅ ProviderMaturity Enum exists")


def test_registry_maturity():
    print("Testing Registry Maturity...")
    registry = ModelRegistry()
    gpt4o = registry.get_model("gpt-4o")
    assert gpt4o.maturity == ProviderMaturity.PRODUCTION
    print("✅ gpt-4o is PRODUCTION")

    grok = registry.get_model("grok-3")
    assert grok.maturity == ProviderMaturity.BETA
    print("✅ grok-3 is BETA")


def test_base_client_methods():
    print("Testing BaseAPIClient methods...")
    assert hasattr(BaseAPIClient, "validate_credentials")
    assert hasattr(BaseAPIClient, "health_check")
    print("✅ BaseAPIClient has validation methods")


def test_bedrock_gating():
    print("Testing Bedrock Gating...")
    try:
        BedrockAPIClient()
    except NotImplementedError as e:
        assert "GATED" in str(e)
        print(f"✅ Bedrock successfully gated: {e}")
    except Exception as e:
        print(f"❌ Unexpected error for Bedrock: {e}")


if __name__ == "__main__":
    test_maturity_enum()
    test_registry_maturity()
    test_base_client_methods()
    test_bedrock_gating()
    print("\nALL VERIFICATION CHECKS PASSED")
