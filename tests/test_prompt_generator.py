import unittest
import os
import json
import shutil
import tempfile
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from lattice_lock_agents.prompt_architect.subagents.prompt_generator import PromptGenerator, GeneratedPrompt
from lattice_lock_agents.prompt_architect.subagents.tool_profiles import ToolAssignment

class TestPromptGenerator(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.prompts_dir = os.path.join(self.test_dir, "project_prompts")
        os.makedirs(self.prompts_dir)

        # Mock config
        self.config_path = os.path.join(self.test_dir, "config.yaml")
        with open(self.config_path, 'w') as f:
            f.write("agent:\n  model_selection:\n    default_provider: local\n    default_model: test-model")

        # Mock template
        self.template_dir = os.path.join(os.path.dirname(__file__), "../src/lattice_lock_agents/prompt_architect/subagents/templates")
        # We'll patch the template path in the instance

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("lattice_lock_agents.prompt_architect.subagents.prompt_generator.get_api_client")
    async def test_generate_prompt(self, mock_get_client):
        # Setup mock client
        mock_client = AsyncMock()
        mock_client.chat_completion.return_value = MagicMock(content="1. Step one\n2. Step two")
        mock_get_client.return_value = mock_client

        # Initialize generator
        generator = PromptGenerator(config_path=self.config_path)
        generator.prompts_dir = self.prompts_dir
        generator.state_file = os.path.join(self.prompts_dir, "project_prompts_state.json")

        # Create dummy assignment
        assignment = ToolAssignment(
            task_id="1.2.3",
            tool="Codex",
            confidence=0.9,
            files_owned=["src/test.py"],
            reasoning="Test reasoning"
        )

        context_data = {
            "task_title": "Test Task",
            "task_description": "Do something",
            "epic_name": "Test Epic",
            "phase_name": "Test Phase",
            "context": "Test Context",
            "goal": "Test Goal"
        }

        # Generate
        prompt = await generator.generate(assignment, context_data)

        # Verify
        self.assertIsInstance(prompt, GeneratedPrompt)
        self.assertEqual(prompt.prompt_id, "1.2.3")
        self.assertIn("Test Task", prompt.content)
        self.assertIn("Test Context", prompt.content)
        self.assertIn("1. Step one", prompt.content)

        # Verify file creation
        self.assertTrue(os.path.exists(prompt.file_path))
        with open(prompt.file_path, 'r') as f:
            content = f.read()
            self.assertIn("# Prompt 1.2.3 - Test Task", content)

        # Verify state update
        self.assertTrue(os.path.exists(generator.state_file))
        with open(generator.state_file, 'r') as f:
            state = json.load(f)
            self.assertIn("1.2.3", state)
            self.assertEqual(state["1.2.3"]["file_path"], prompt.file_path)

    @patch("lattice_lock_agents.prompt_architect.subagents.prompt_generator.get_api_client")
    async def test_generate_steps_llm_call(self, mock_get_client):
        mock_client = AsyncMock()
        mock_client.chat_completion.return_value = MagicMock(content="1. Step A\n2. Step B")
        mock_get_client.return_value = mock_client

        generator = PromptGenerator(config_path=self.config_path)

        assignment = ToolAssignment(
            task_id="1.1.1",
            tool="TestTool",
            confidence=1.0
        )
        context = {"task_title": "Task", "task_description": "Desc"}

        steps = await generator._generate_steps(assignment, context)

        self.assertIn("1. Step A", steps)
        mock_client.chat_completion.assert_called_once()

if __name__ == "__main__":
    unittest.main()
