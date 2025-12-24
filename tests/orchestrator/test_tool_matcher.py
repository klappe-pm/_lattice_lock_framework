import pytest

from lattice_lock.agents.prompt_architect.subagents.tool_matcher import ToolMatcher
from lattice_lock.agents.prompt_architect.subagents.tool_profiles import Task

# Sample YAML configuration for testing
TEST_YAML = """
tool_profiles:
  devin:
    name: Devin AI
    identifier: devin
    strengths:
      - CI/CD
      - Infrastructure
    preferred_files:
      - pyproject.toml
      - .github/workflows/
  gemini:
    name: Gemini CLI
    identifier: gemini
    strengths:
      - Schema validation
    preferred_files:
      - src/validator/
"""


@pytest.fixture
def test_config(tmp_path):
    config_file = tmp_path / "test_tool_matcher.yaml"
    config_file.write_text(TEST_YAML)
    return str(config_file)


def test_load_profiles(test_config):
    matcher = ToolMatcher(test_config)
    assert "devin" in matcher.profiles
    assert "gemini" in matcher.profiles
    assert matcher.profiles["devin"].name == "Devin AI"


def test_capability_matching(test_config):
    matcher = ToolMatcher(test_config)
    task = Task(id="1", description="Setup CI/CD pipeline", files=[])
    assignments = matcher.match([task])

    assert len(assignments) == 1
    assert assignments[0].tool == "devin"
    assert assignments[0].confidence > 0.0


def test_file_ownership_enforcement(test_config):
    matcher = ToolMatcher(test_config)
    # Task involves a file owned by Gemini
    task = Task(id="2", description="Update validator logic", files=["src/validator/schema.py"])
    assignments = matcher.match([task])

    assert len(assignments) == 1
    assert assignments[0].tool == "gemini"
    assert "Owned files detected" in assignments[0].reasoning


def test_conflict_resolution_priority(test_config):
    matcher = ToolMatcher(test_config)
    # Task has description matching Devin but file owned by Gemini
    # Ownership should take precedence
    task = Task(id="3", description="CI/CD for validator", files=["src/validator/schema.py"])
    assignments = matcher.match([task])

    assert len(assignments) == 1
    assert assignments[0].tool == "gemini"


def test_do_not_touch_list(test_config):
    matcher = ToolMatcher(test_config)
    dnt_devin = matcher.get_do_not_touch_list("devin")

    # Devin should not touch Gemini's files
    assert "src/validator/" in dnt_devin
    # Devin's own files should not be in the list
    assert "pyproject.toml" not in dnt_devin


def test_mixed_ownership_conflict(test_config):
    matcher = ToolMatcher(test_config)
    # Task with files from both (conflict)
    # Current simple logic picks the first one found, but we want to ensure it picks ONE of them
    task = Task(
        id="4",
        description="Refactor everything",
        files=["pyproject.toml", "src/validator/schema.py"],
    )
    assignments = matcher.match([task])

    assert len(assignments) == 1
    assert assignments[0].tool in ["devin", "gemini"]
