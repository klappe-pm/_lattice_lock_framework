"""
Integration tests for Prompt Tracker integration with Prompt Architect Agent.

Tests the interaction between:
- scripts/prompt_tracker.py CLI commands
- TrackerClient Python API
- PromptGenerator state management
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure src is in path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from lattice_lock_agents.prompt_architect.tracker_client import TrackerClient


class TestTrackerIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Setup repo root structure mock
        self.prompts_dir = self.test_path / "project_prompts"
        self.prompts_dir.mkdir(parents=True)

        # Create phase directories
        (self.prompts_dir / "phase1_foundation").mkdir()
        (self.prompts_dir / "phase5_prompt_automation").mkdir()

        # Create sample prompt files
        (self.prompts_dir / "phase1_foundation" / "1.1.1_devin_test.md").write_text(
            "# Test Prompt 1.1.1"
        )
        (self.prompts_dir / "phase5_prompt_automation" / "5.4.1_claude_app_test.md").write_text(
            "# Test Prompt 5.4.1"
        )

        # Create state file with sample data
        self.state = {
            "metadata": {
                "project": "Test Project",
                "version": "1.0.0",
                "created": "2025-12-01",
                "last_updated": "2025-12-01 00:00:00",
                "total_prompts": 2,
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
                    "pr_url": None,
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
                    "pr_url": None,
                },
            ],
            "tool_definitions": {
                "devin": "Devin AI",
                "gemini": "Gemini CLI",
                "codex": "Codex CLI",
                "claude_cli": "Claude Code CLI",
                "claude_app": "Claude Code App",
                "claude_docs": "Claude Code Website",
            },
            "phase_definitions": {"1": "Foundation", "5": "Prompt Automation"},
        }

        self.state_file = self.prompts_dir / "project_prompts_state.json"

        # Create Dummy Tracker script for CLI tests if needed,
        # but here we mostly test Client logic which can use direct mode or mock CLI.
        # Since we are testing TrackerClient logic primarily, we will focus on direct mode
        # or rely on the fact that TrackerClient defaults to direct mode unless use_cli=True.
        # The existing tests used TrackerClient(..., use_cli=False) implicitly or explicitly?
        # Looking at original code: TrackerClient(repo_root=temp_state_dir). Default use_cli=False.

        # We need to write the state file
        self._write_state()

        # Initialize client
        self.client = TrackerClient(repo_root=self.test_path, use_cli=False)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _write_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def test_add_prompt_command(self):
        """Test add-prompt CLI command (via TrackerClient)."""
        # Create the prompt file first
        prompt_file = self.prompts_dir / "phase1_foundation" / "1.1.3_gemini_new.md"
        prompt_file.write_text("# New Prompt")

        # Add the prompt
        result = self.client.add_prompt(
            prompt_id="1.1.3",
            title="New test prompt",
            tool="gemini",
            file_path="phase1_foundation/1.1.3_gemini_new.md",
        )

        self.assertEqual(result["status"], "added")
        self.assertEqual(result["id"], "1.1.3")
        self.assertEqual(result["tool"], "gemini")

        # Verify it was added to state
        prompt = self.client.get_prompt("1.1.3")
        self.assertIsNotNone(prompt)
        self.assertEqual(prompt["title"], "New test prompt")

    def test_add_prompt_duplicate_fails(self):
        """Test that adding a duplicate prompt fails."""
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.client.add_prompt(
                prompt_id="1.1.1",  # Already exists
                title="Duplicate",
                tool="devin",
                file_path="phase1_foundation/duplicate.md",
            )

    def test_add_prompt_invalid_tool(self):
        """Test that adding with invalid tool fails."""
        with self.assertRaisesRegex(ValueError, "Invalid tool"):
            self.client.add_prompt(
                prompt_id="1.1.4",
                title="Bad tool",
                tool="invalid_tool",
                file_path="phase1_foundation/bad.md",
            )

    def test_add_prompt_invalid_id_format(self):
        """Test that adding with invalid ID format fails."""
        with self.assertRaisesRegex(ValueError, "Invalid prompt ID format"):
            self.client.add_prompt(
                prompt_id="invalid",
                title="Bad ID",
                tool="devin",
                file_path="phase1_foundation/bad.md",
            )

    def test_get_prompt(self):
        """Test getting a prompt by ID."""
        prompt = self.client.get_prompt("1.1.1")
        self.assertIsNotNone(prompt)
        self.assertEqual(prompt["id"], "1.1.1")
        self.assertEqual(prompt["title"], "Test prompt 1")
        self.assertEqual(prompt["tool"], "devin")

    def test_get_prompt_not_found(self):
        """Test getting a nonexistent prompt returns None."""
        prompt = self.client.get_prompt("99.99.99")
        self.assertIsNone(prompt)

    def test_get_next_prompt(self):
        """Test getting the next available prompt for a tool."""
        prompt = self.client.get_next_prompt("devin")
        self.assertIsNotNone(prompt)
        self.assertEqual(prompt["tool"], "devin")
        self.assertFalse(prompt["picked_up"])

    def test_get_next_prompt_none_available(self):
        """Test getting next prompt when none available."""
        # There's no gemini prompt in the test data, so this should return None
        prompt = self.client.get_next_prompt("gemini")
        self.assertIsNone(prompt)

    def test_update_prompt(self):
        """Test updating a prompt's status."""
        result = self.client.update_prompt("1.1.1", done=True)
        self.assertEqual(result["status"], "updated")
        self.assertTrue(result["done"])

        # Verify the update
        prompt = self.client.get_prompt("1.1.1")
        self.assertTrue(prompt["done"])

    def test_update_prompt_merged(self):
        """Test marking a prompt as merged."""
        result = self.client.update_prompt(
            "1.1.1", done=True, merged=True, pr_url="https://github.com/test/pr/1"
        )

        self.assertTrue(result["merged"])

        prompt = self.client.get_prompt("1.1.1")
        self.assertTrue(prompt["merged"])
        self.assertEqual(prompt["pr_url"], "https://github.com/test/pr/1")
        self.assertIsNotNone(prompt["end_time"])

    def test_list_prompts_no_filter(self):
        """Test listing all prompts."""
        prompts = self.client.list_prompts()
        self.assertEqual(len(prompts), 2)

    def test_list_prompts_by_tool(self):
        """Test listing prompts filtered by tool."""
        prompts = self.client.list_prompts(tool="devin")
        self.assertEqual(len(prompts), 1)
        self.assertEqual(prompts[0]["tool"], "devin")

    def test_list_prompts_by_phase(self):
        """Test listing prompts filtered by phase."""
        prompts = self.client.list_prompts(phase="1")
        self.assertEqual(len(prompts), 1)
        self.assertEqual(prompts[0]["phase"], "1")

    def test_list_prompts_by_status(self):
        """Test listing prompts filtered by status."""
        # All prompts are pending initially
        pending = self.client.list_prompts(status="pending")
        self.assertEqual(len(pending), 2)

        # Mark one as done


if __name__ == "__main__":
    unittest.main()
