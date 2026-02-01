"""Test agent settings configuration."""

import os
from pathlib import Path

import pytest


@pytest.mark.quality
@pytest.mark.agent
class TestAgentSettingsConfiguration:
    """Test the agent settings system."""

    def test_settings_file_exists(self):
        """Agent settings file should exist."""
        settings_path = Path("agents/config/agent_settings.yaml")
        assert settings_path.exists(), f"Agent settings file not found at {settings_path}"

    def test_settings_loader_works(self):
        """Settings loader should work without errors."""
        from lattice_lock.agents.settings import load_settings, reset_settings

        reset_settings()
        settings = load_settings()

        assert settings is not None
        assert hasattr(settings, "agents")

    def test_approver_enabled_by_default(self):
        """Approver Agent should be enabled by default."""
        from lattice_lock.agents.settings import load_settings, reset_settings

        reset_settings()
        settings = load_settings()

        assert (
            settings.agents.approver_agent.enabled is True
        ), "Approver Agent should be enabled by default"

    def test_coverage_target_is_90(self):
        """Coverage target should be 90%."""
        from lattice_lock.agents.settings import load_settings, reset_settings

        reset_settings()
        settings = load_settings()

        assert settings.agents.approver_agent.coverage.target == 90, "Coverage target should be 90%"

    def test_env_override_approver_enabled(self):
        """Environment variable should override approver enabled setting."""
        from lattice_lock.agents.settings import load_settings, reset_settings

        reset_settings()

        # Test disabling via environment
        os.environ["LATTICE_APPROVER_ENABLED"] = "false"
        try:
            settings = load_settings()
            assert settings.agents.approver_agent.enabled is False
        finally:
            del os.environ["LATTICE_APPROVER_ENABLED"]
            reset_settings()

    def test_env_override_coverage_target(self):
        """Environment variable should override coverage target."""
        from lattice_lock.agents.settings import load_settings, reset_settings

        reset_settings()

        os.environ["LATTICE_COVERAGE_TARGET"] = "85"
        try:
            settings = load_settings()
            assert settings.agents.approver_agent.coverage.target == 85
        finally:
            del os.environ["LATTICE_COVERAGE_TARGET"]
            reset_settings()

    def test_get_settings_caches(self):
        """get_settings should return cached instance."""
        from lattice_lock.agents.settings import get_settings, reset_settings

        reset_settings()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2, "get_settings should return cached instance"


@pytest.mark.quality
@pytest.mark.agent
@pytest.mark.approver
class TestApproverAgentConfiguration:
    """Test Approver Agent specific configuration."""

    def test_all_subagents_configured(self):
        """All Approver subagents should be configured."""
        from lattice_lock.agents.settings import load_settings, reset_settings

        reset_settings()
        settings = load_settings()
        subagents = settings.agents.approver_agent.subagents

        expected_subagents = [
            "coverage_analyst",
            "documentation_validator",
            "index_manager",
            "test_reviewer",
            "bug_automation_agent",
            "requirements_tracker",
        ]

        for subagent in expected_subagents:
            assert hasattr(subagents, subagent), f"Subagent {subagent} not configured"

    def test_coverage_enforcement_mode(self):
        """Coverage enforcement mode should be valid."""
        from lattice_lock.agents.settings import load_settings, reset_settings

        reset_settings()
        settings = load_settings()

        mode = settings.agents.approver_agent.coverage.enforcement_mode
        valid_modes = ["strict", "warn", "disabled"]

        assert mode in valid_modes, f"Invalid enforcement mode: {mode}"
