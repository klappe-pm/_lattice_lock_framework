import yaml
from pathlib import Path
import pytest

def get_agent_definition(agent_name: str) -> dict:
    """Helper to load agent definition."""
    repo_root = Path(__file__).parents[2]
    def_path = repo_root / "docs" / "agents" / "agent_definitions" / agent_name / f"{agent_name}_definition.yaml"
    if not def_path.exists():
        pytest.fail(f"Definition not found: {def_path}")
    
    with open(def_path) as f:
        return yaml.safe_load(f)

def test_product_agent_definition_exists():
    """Test that product_agent definition exists and is valid YAML."""
    data = get_agent_definition("product_agent")
    assert data is not None
    assert "agent" in data

def test_product_agent_identity():
    """Test product_agent identity configuration."""
    data = get_agent_definition("product_agent")
    identity = data["agent"]["identity"]
    
    assert identity["name"] == "product_agent"
    assert "Product" in identity["role"]
    assert identity["status"] in ["alpha", "beta", "active", "deprecated"]

def test_product_agent_directives():
    """Test product_agent has primary goal."""
    data = get_agent_definition("product_agent")
    directive = data["agent"]["directive"]
    
    assert "primary_goal" in directive
    assert len(directive["primary_goal"]) > 10
