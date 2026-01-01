from pathlib import Path
from unittest.mock import patch

import pytest

from lattice_lock.agents.prompt_architect.agent import PromptArchitectAgent


class TestPromptArchitectAgent:
    """Tests for the PromptArchitectAgent class."""

    @pytest.fixture
    def agent(self):
        """Fixture to provide a PromptArchitectAgent instance."""
        # Mock repo_root to avoid file system lookups during init if possible,
        # but the agent does some auto-detection.
        # We can pass a dummy path or use the real one if consistent.
        # For unit tests, mocking load_definition is safer.
        with patch(
            "lattice_lock.agents.prompt_architect.agent.PromptArchitectAgent._load_definition"
        ) as mock_load:
            mock_load.return_value = {
                "agent": {
                    "identity": {"name": "test_agent", "version": "1.0.0"},
                    "configuration": {"max_steps": 50},
                }
            }
            agent = PromptArchitectAgent(repo_root=Path("/tmp/test_repo"))
            return agent

    def test_initialization(self, agent):
        """Test that the agent initializes correctly."""
        assert isinstance(agent, PromptArchitectAgent)
        assert agent.config.name == "test_agent"
        assert agent.config.max_steps == 50

    def test_default_config(self):
        """Test initialization with default config when loading fails."""
        with patch(
            "lattice_lock.agents.prompt_architect.agent.PromptArchitectAgent._load_definition"
        ) as mock_load:
            mock_load.return_value = {}
            agent = PromptArchitectAgent(repo_root=Path("/tmp/test_repo"))

            assert agent.config.name == "prompt_architect_agent"
            assert agent.config.version == "1.0.0"
            assert agent.config.max_steps == 100

    def test_subagent_initialization(self, agent):
        """Test strict lazy loading of subagents."""
        assert agent._spec_analyzer is None
        assert agent._roadmap_parser is None
        assert agent._tool_matcher is None
        assert agent._prompt_generator is None

        # We verify they are created on access
        # Note: We mock the subagent classes to avoid their complex init logic
        with patch("lattice_lock.agents.prompt_architect.agent.SpecAnalyzer"):
            assert agent.spec_analyzer is not None

        with patch("lattice_lock.agents.prompt_architect.agent.RoadmapParser"):
            assert agent.roadmap_parser is not None

    def test_guardrails(self, agent):
        """Test guardrail validation logic."""
        # Mock definition to have some scope constraints
        agent.definition = {"scope": {"cannot_modify": ["/protected"]}}

        assert agent.validate_guardrails("modify", "src/main.py") is True
        assert agent.validate_guardrails("modify", "protected/secret.key") is False
        assert agent.validate_guardrails("modify", "credentials.json") is False
