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

def test_engineering_agent_definition_exists():
    """Test that engineering_agent definition exists and is valid YAML."""
    data = get_agent_definition("engineering_agent")
    assert data is not None
    assert "agent" in data

def test_engineering_agent_identity():
    """Test engineering_agent identity configuration."""
    data = get_agent_definition("engineering_agent")
    identity = data["agent"]["identity"]
    
    assert identity["name"] == "engineering_agent"
    assert "Engineering" in identity["role"]

def test_engineering_agent_delegation():
    """Test engineering_agent delegation structure."""
    data = get_agent_definition("engineering_agent")
    delegation = data["agent"]["delegation"]
    
    assert delegation["enabled"] is True
    assert len(delegation["allowed_subagents"]) > 0
