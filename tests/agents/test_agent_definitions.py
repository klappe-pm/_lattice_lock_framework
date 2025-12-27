from pathlib import Path

import pytest
import yaml


def get_agent_definition(agent_name: str) -> dict:
    """Helper to load agent definition."""
    repo_root = Path(__file__).parents[2]
    def_path = (
        repo_root
        / "docs"
        / "agents"
        / "agent_definitions"
        / agent_name
        / f"{agent_name}_definition.yaml"
    )
    if not def_path.exists():
        pytest.fail(f"Definition not found: {def_path}")

    with open(def_path) as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize(
    "agent_name, expected_role_snippet",
    [
        ("engineering_agent", "Engineering"),
        ("project_agent", "Project"),
        ("product_agent", "Product"),
        ("research_agent", "Research"),
        ("business_review_agent", "Business Intelligence"),
    ],
)
def test_agent_definition_validity(agent_name, expected_role_snippet):
    """Test that agent definitions exist and have correct identity."""
    data = get_agent_definition(agent_name)
    assert data is not None
    assert "agent" in data

    identity = data["agent"]["identity"]
    assert identity["name"] == agent_name
    assert expected_role_snippet in identity["role"]


def test_engineering_agent_delegation():
    """Specific test for engineering_agent delegation."""
    data = get_agent_definition("engineering_agent")
    delegation = data["agent"]["delegation"]
    assert delegation["enabled"] is True
    assert len(delegation["allowed_subagents"]) > 0


def test_project_agent_scope():
    """Specific test for project_agent scope."""
    data = get_agent_definition("project_agent")
    scope = data["agent"]["scope"]
    assert "can_access" in scope
    assert "can_modify" in scope
