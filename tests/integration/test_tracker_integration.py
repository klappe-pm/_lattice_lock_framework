"""
Integration tests for Prompt Tracker integration with Prompt Architect Agent.

Tests the interaction between:
- scripts/prompt_tracker.py CLI commands
- TrackerClient Python API
- PromptGenerator state management
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


# Get repo root
REPO_ROOT = Path(__file__).parent.parent.parent
TRACKER_SCRIPT = REPO_ROOT / "scripts" / "prompt_tracker.py"


@pytest.fixture
def temp_state_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with tracker state files."""
    prompts_dir = tmp_path / "project_prompts"
    prompts_dir.mkdir(parents=True)

    # Create phase directories
    (prompts_dir / "phase1_foundation").mkdir()
    (prompts_dir / "phase5_prompt_automation").mkdir()

    # Create sample prompt files
    (prompts_dir / "phase1_foundation" / "1.1.1_devin_test.md").write_text("# Test Prompt 1.1.1")
    (prompts_dir / "phase5_prompt_automation" / "5.4.1_claude_app_test.md").write_text("# Test Prompt 5.4.1")

    # Create state file with sample data
    state = {
        "metadata": {
            "project": "Test Project",
            "version": "1.0.0",
            "created": "2025-12-01",
            "last_updated": "2025-12-01 00:00:00",
            "total_prompts": 2
        },
        "prompts": [
            {
                "id": "1.1.1",
                "phase": "1",
                "epic": "1.1",
                "title": "Test prompt 1",
                "tool": "devin",
                "file": "phase1_foundation/1.1.1_devin_test.md",
                "picked_up": False,
                "done": False,
                "merged": False,
                "model_used": None,
                "start_time": None,
                "end_time": None,
                "duration_minutes": None,
                "pr_url": None
            },
            {
                "id": "5.4.1",
                "phase": "5",
                "epic": "5.4",
                "title": "Tracker integration",
                "tool": "claude_app",
                "file": "phase5_prompt_automation/5.4.1_claude_app_test.md",
                "picked_up": False,
                "done": False,
                "merged": False,
                "model_used": None,
                "start_time": None,
                "end_time": None,
                "duration_minutes": None,
                "pr_url": None
            }
        ],
        "tool_definitions": {
            "devin": "Devin AI",
            "gemini": "Gemini CLI",
            "codex": "Codex CLI",
            "claude_cli": "Claude Code CLI",
            "claude_app": "Claude Code App",
            "claude_docs": "Claude Code Website"
        },
        "phase_definitions": {
            "1": "Foundation",
            "5": "Prompt Automation"
        }
    }

    state_file = prompts_dir / "project_prompts_state.json"
    state_file.write_text(json.dumps(state, indent=2))

    return tmp_path


@pytest.fixture
def tracker_client(temp_state_dir: Path):
    """Create a TrackerClient instance for testing."""
    from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient
    return TrackerClient(repo_root=temp_state_dir)


class TestTrackerCLI:
    """Tests for prompt_tracker.py CLI commands."""

    def test_add_prompt_command(self, temp_state_dir: Path):
        """Test add-prompt CLI command."""
        # Create a modified script path for testing
        # We need to patch the paths in the script or use the TrackerClient directly

        # For now, test via TrackerClient which mimics CLI behavior
        from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

        client = TrackerClient(repo_root=temp_state_dir)

        # Create the prompt file first
        prompt_file = temp_state_dir / "project_prompts" / "phase1_foundation" / "1.1.3_gemini_new.md"
        prompt_file.write_text("# New Prompt")

        # Add the prompt
        result = client.add_prompt(
            prompt_id="1.1.3",
            title="New test prompt",
            tool="gemini",
            file_path="phase1_foundation/1.1.3_gemini_new.md"
        )

        assert result["status"] == "added"
        assert result["id"] == "1.1.3"
        assert result["tool"] == "gemini"

        # Verify it was added to state
        prompt = client.get_prompt("1.1.3")
        assert prompt is not None
        assert prompt["title"] == "New test prompt"

    def test_add_prompt_duplicate_fails(self, tracker_client):
        """Test that adding a duplicate prompt fails."""
        with pytest.raises(ValueError, match="already exists"):
            tracker_client.add_prompt(
                prompt_id="1.1.1",  # Already exists
                title="Duplicate",
                tool="devin",
                file_path="phase1_foundation/duplicate.md"
            )

    def test_add_prompt_invalid_tool(self, tracker_client):
        """Test that adding with invalid tool fails."""
        with pytest.raises(ValueError, match="Invalid tool"):
            tracker_client.add_prompt(
                prompt_id="1.1.4",
                title="Bad tool",
                tool="invalid_tool",
                file_path="phase1_foundation/bad.md"
            )

    def test_add_prompt_invalid_id_format(self, tracker_client):
        """Test that adding with invalid ID format fails."""
        with pytest.raises(ValueError, match="Invalid prompt ID format"):
            tracker_client.add_prompt(
                prompt_id="invalid",
                title="Bad ID",
                tool="devin",
                file_path="phase1_foundation/bad.md"
            )


class TestTrackerClientAPI:
    """Tests for TrackerClient Python API."""

    def test_get_prompt(self, tracker_client):
        """Test getting a prompt by ID."""
        prompt = tracker_client.get_prompt("1.1.1")
        assert prompt is not None
        assert prompt["id"] == "1.1.1"
        assert prompt["title"] == "Test prompt 1"
        assert prompt["tool"] == "devin"

    def test_get_prompt_not_found(self, tracker_client):
        """Test getting a nonexistent prompt returns None."""
        prompt = tracker_client.get_prompt("99.99.99")
        assert prompt is None

    def test_get_next_prompt(self, tracker_client):
        """Test getting the next available prompt for a tool."""
        prompt = tracker_client.get_next_prompt("devin")
        assert prompt is not None
        assert prompt["tool"] == "devin"
        assert prompt["picked_up"] is False

    def test_get_next_prompt_none_available(self, temp_state_dir: Path):
        """Test getting next prompt when none available."""
        from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

        client = TrackerClient(repo_root=temp_state_dir)

        # Pick up the only gemini prompt manually
        state = client._load_state()
        # There's no gemini prompt in the test data, so this should return None
        prompt = client.get_next_prompt("gemini")
        assert prompt is None

    def test_update_prompt(self, tracker_client):
        """Test updating a prompt's status."""
        result = tracker_client.update_prompt("1.1.1", done=True)
        assert result["status"] == "updated"
        assert result["done"] is True

        # Verify the update
        prompt = tracker_client.get_prompt("1.1.1")
        assert prompt["done"] is True

    def test_update_prompt_merged(self, tracker_client):
        """Test marking a prompt as merged."""
        result = tracker_client.update_prompt(
            "1.1.1",
            done=True,
            merged=True,
            pr_url="https://github.com/test/pr/1"
        )

        assert result["merged"] is True

        prompt = tracker_client.get_prompt("1.1.1")
        assert prompt["merged"] is True
        assert prompt["pr_url"] == "https://github.com/test/pr/1"
        assert prompt["end_time"] is not None

    def test_list_prompts_no_filter(self, tracker_client):
        """Test listing all prompts."""
        prompts = tracker_client.list_prompts()
        assert len(prompts) == 2

    def test_list_prompts_by_tool(self, tracker_client):
        """Test listing prompts filtered by tool."""
        prompts = tracker_client.list_prompts(tool="devin")
        assert len(prompts) == 1
        assert prompts[0]["tool"] == "devin"

    def test_list_prompts_by_phase(self, tracker_client):
        """Test listing prompts filtered by phase."""
        prompts = tracker_client.list_prompts(phase="1")
        assert len(prompts) == 1
        assert prompts[0]["phase"] == "1"

    def test_list_prompts_by_status(self, tracker_client):
        """Test listing prompts filtered by status."""
        # All prompts are pending initially
        pending = tracker_client.list_prompts(status="pending")
        assert len(pending) == 2

        # Mark one as done
        tracker_client.update_prompt("1.1.1", done=True, merged=True)

        merged = tracker_client.list_prompts(status="merged")
        assert len(merged) == 1


class TestStateSynchronization:
    """Tests for state synchronization between agent and tracker."""

    def test_add_prompt_regenerates_markdown(self, temp_state_dir: Path):
        """Test that adding a prompt regenerates the markdown tracker."""
        from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

        client = TrackerClient(repo_root=temp_state_dir)

        # Create prompt file
        prompt_file = temp_state_dir / "project_prompts" / "phase1_foundation" / "1.1.5_codex_new.md"
        prompt_file.write_text("# New Prompt")

        # Add the prompt
        client.add_prompt(
            prompt_id="1.1.5",
            title="Regeneration test",
            tool="codex",
            file_path="phase1_foundation/1.1.5_codex_new.md"
        )

        # Check that markdown file was regenerated
        tracker_md = temp_state_dir / "project_prompts" / "project_prompts_tracker.md"
        assert tracker_md.exists()

        content = tracker_md.read_text()
        assert "1.1.5" in content
        assert "Regeneration test" in content
        assert "Codex CLI" in content

    def test_validate_state_valid(self, tracker_client):
        """Test state validation with valid state."""
        result = tracker_client.validate_state()
        assert result["status"] == "valid"
        assert result["valid_count"] == 2
        assert result["issue_count"] == 0

    def test_validate_state_missing_file(self, temp_state_dir: Path):
        """Test state validation detects missing files."""
        from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

        # Delete a prompt file
        prompt_file = temp_state_dir / "project_prompts" / "phase1_foundation" / "1.1.1_devin_test.md"
        prompt_file.unlink()

        client = TrackerClient(repo_root=temp_state_dir)
        result = client.validate_state()

        assert result["status"] == "invalid"
        assert result["issue_count"] == 1
        assert result["issues"][0]["issue"] == "file_not_found"
        assert result["issues"][0]["id"] == "1.1.1"

    def test_validate_state_orphan_files(self, temp_state_dir: Path):
        """Test state validation detects orphan files."""
        from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

        # Create an orphan file not in state
        orphan_file = temp_state_dir / "project_prompts" / "phase1_foundation" / "orphan_prompt.md"
        orphan_file.write_text("# Orphan")

        client = TrackerClient(repo_root=temp_state_dir)
        result = client.validate_state(check_orphans=True)

        assert result["status"] == "invalid"
        has_orphan_issue = any(
            issue.get("issue") == "orphan_file"
            for issue in result.get("issues", [])
        )
        assert has_orphan_issue


class TestBatchOperations:
    """Tests for batch prompt operations."""

    def test_batch_add_prompts(self, temp_state_dir: Path):
        """Test adding multiple prompts at once."""
        from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

        client = TrackerClient(repo_root=temp_state_dir)

        # Create prompt files
        (temp_state_dir / "project_prompts" / "phase1_foundation" / "1.1.4_gemini_batch1.md").write_text("# Batch 1")
        (temp_state_dir / "project_prompts" / "phase1_foundation" / "1.1.5_codex_batch2.md").write_text("# Batch 2")

        new_prompts = [
            {"id": "1.1.4", "title": "Batch prompt 1", "tool": "gemini", "file": "phase1_foundation/1.1.4_gemini_batch1.md"},
            {"id": "1.1.5", "title": "Batch prompt 2", "tool": "codex", "file": "phase1_foundation/1.1.5_codex_batch2.md"},
        ]

        result = client.batch_add(new_prompts)

        assert result["status"] == "batch_complete"
        assert result["added_count"] == 2
        assert "1.1.4" in result["added"]
        assert "1.1.5" in result["added"]

    def test_batch_add_skips_duplicates(self, temp_state_dir: Path):
        """Test that batch add skips existing prompts."""
        from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

        client = TrackerClient(repo_root=temp_state_dir)

        # Create file for new prompt
        (temp_state_dir / "project_prompts" / "phase1_foundation" / "1.1.6_devin_new.md").write_text("# New")

        new_prompts = [
            {"id": "1.1.1", "title": "Duplicate", "tool": "devin", "file": "phase1_foundation/dup.md"},  # Duplicate
            {"id": "1.1.6", "title": "New one", "tool": "devin", "file": "phase1_foundation/1.1.6_devin_new.md"},  # New
        ]

        result = client.batch_add(new_prompts)

        assert result["added_count"] == 1
        assert result["skipped_count"] == 1
        assert "1.1.6" in result["added"]
        assert any(s.get("id") == "1.1.1" for s in result["skipped"])


class TestPromptOrdering:
    """Tests for prompt ordering and insertion."""

    def test_prompts_maintain_order(self, temp_state_dir: Path):
        """Test that prompts are maintained in sorted order."""
        from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient

        client = TrackerClient(repo_root=temp_state_dir)

        # Add prompts out of order
        (temp_state_dir / "project_prompts" / "phase1_foundation" / "1.2.1_gemini.md").write_text("# 1.2.1")
        (temp_state_dir / "project_prompts" / "phase1_foundation" / "1.1.2_codex.md").write_text("# 1.1.2")

        client.add_prompt("1.2.1", "Later prompt", "gemini", "phase1_foundation/1.2.1_gemini.md")
        client.add_prompt("1.1.2", "Earlier prompt", "codex", "phase1_foundation/1.1.2_codex.md")

        # List all prompts and verify order
        prompts = client.list_prompts()
        ids = [p["id"] for p in prompts]

        # Should be in numeric order
        expected_order = sorted(ids, key=lambda x: [int(n) for n in x.split(".")])
        assert ids == expected_order
