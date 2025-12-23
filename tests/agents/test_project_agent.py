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

def test_project_agent_definition_exists():
    """Test that project_agent definition exists and is valid YAML."""
    data = get_agent_definition("project_agent")
    assert data is not None
    assert "agent" in data

def test_project_agent_identity():
    """Test project_agent identity configuration."""
    data = get_agent_definition("project_agent")
    identity = data["agent"]["identity"]
    
    assert identity["name"] == "project_agent"
    assert "Project" in identity["role"]

def test_project_agent_scope():
    """Test project_agent scope configuration."""
    data = get_agent_definition("project_agent")
    scope = data["agent"]["scope"]
    
    assert "can_access" in scope
    assert "can_modify" in scope
