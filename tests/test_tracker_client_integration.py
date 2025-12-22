import json
import logging

import pytest

from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.skip(
    reason="project_prompts functionality has been removed - implementation folder no longer exists"
)


@pytest.fixture
def temp_repo_root(tmp_path):
    """Create a temporary repository root with necessary structure."""
    prompts_dir = tmp_path / "project_prompts"
    prompts_dir.mkdir()

    # Create initial state file
    state = {
        "metadata": {"last_updated": "2024-01-01 00:00:00", "total_prompts": 0},
        "prompts": [],
        "tool_definitions": {"devin": "Devin AI", "gemini": "Gemini 1.5 Pro"},
        "phase_definitions": {"1": "Foundation"},
    }

    with open(prompts_dir / "project_prompts_state.json", "w") as f:
        json.dump(state, f)

    return tmp_path


def test_tracker_client_add_get_prompt(temp_repo_root):
    """Test adding and retrieving a prompt."""
    client = TrackerClient(repo_root=temp_repo_root, use_cli=False)

    # Add prompt
    result = client.add_prompt(
        prompt_id="1.1.1", title="Test Prompt", tool="devin", file_path="phase1/1.1.1_test.md"
    )

    assert result["status"] == "added"
    assert result["id"] == "1.1.1"

    # Get prompt
    prompt = client.get_prompt("1.1.1")
    assert prompt is not None
    assert prompt["title"] == "Test Prompt"
    assert prompt["tool"] == "devin"
    assert prompt["phase"] == "1"
    assert prompt["epic"] == "1.1"


def test_tracker_client_update_prompt(temp_repo_root):
    """Test updating a prompt status."""
    client = TrackerClient(repo_root=temp_repo_root, use_cli=False)

    # Add initial prompt
    client.add_prompt(
        prompt_id="1.1.1", title="Test Prompt", tool="devin", file_path="phase1/1.1.1_test.md"
    )

    # Update status
    result = client.update_prompt(
        prompt_id="1.1.1", done=True, merged=True, pr_url="http://github.com/pr/1"
    )

    assert result["status"] == "updated"

    # Verify update
    prompt = client.get_prompt("1.1.1")
    assert prompt["done"] is True
    assert prompt["merged"] is True
    assert prompt["pr_url"] == "http://github.com/pr/1"
    assert prompt["end_time"] is not None


def test_tracker_client_list_prompts(temp_repo_root):
    """Test listing and filtering prompts."""
    client = TrackerClient(repo_root=temp_repo_root, use_cli=False)

    client.add_prompt("1.1.1", "Task 1", "devin", "p1/1.md")
    client.add_prompt("1.1.2", "Task 2", "gemini", "p1/2.md")
    client.add_prompt("2.1.1", "Task 3", "devin", "p2/1.md")

    # No filter
    all_prompts = client.list_prompts()
    assert len(all_prompts) == 3

    # Tool filter
    devin_prompts = client.list_prompts(tool="devin")
    assert len(devin_prompts) == 2

    # Phase filter
    phase2_prompts = client.list_prompts(phase="2")
    assert len(phase2_prompts) == 1

    # Pending filter (defaultall pending)
    pending_prompts = client.list_prompts(status="pending")
    assert len(pending_prompts) == 3


def test_tracker_client_regenerate_markdown(temp_repo_root):
    """Test markdown tracker generation."""
    client = TrackerClient(repo_root=temp_repo_root, use_cli=False)
    client.add_prompt("1.1.1", "Task 1", "devin", "p1/1.md")

    # Convert manually since internal method called by add_prompt might fail if markdown not writable?
    # Actually add_prompt calls regenerate.

    tracker_file = temp_repo_root / "project_prompts" / "project_prompts_tracker.md"
    assert tracker_file.exists()

    content = tracker_file.read_text()
    assert "# Lattice Lock Framework - Project Prompts Tracker" in content
    assert "| 1.1.1 | Task 1 |" in content
