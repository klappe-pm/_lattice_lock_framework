"""
Agent Settings Loader.

Loads configuration from agents/config/agent_settings.yaml with environment
variable overrides. The Approver Agent is ENABLED BY DEFAULT.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class CoverageSettings(BaseModel):
    """Coverage enforcement settings."""

    enabled: bool = True
    target: int = 90
    warning_threshold: int = 85
    critical_threshold: int = 80
    enforcement_mode: str = "strict"  # strict | warn | disabled


class SubagentSettings(BaseModel):
    """Settings for a sub-agent."""

    enabled: bool = True
    auto_spawn: bool = True


class ApproverSubagentSettings(BaseModel):
    """Settings for Approver Agent sub-agents."""

    coverage_analyst: SubagentSettings = Field(default_factory=SubagentSettings)
    documentation_validator: SubagentSettings = Field(default_factory=SubagentSettings)
    index_manager: SubagentSettings = Field(default_factory=SubagentSettings)
    test_reviewer: SubagentSettings = Field(default_factory=SubagentSettings)
    bug_automation_agent: SubagentSettings = Field(default_factory=SubagentSettings)
    requirements_tracker: SubagentSettings = Field(
        default_factory=lambda: SubagentSettings(auto_spawn=False)
    )


class ApproverAgentSettings(BaseModel):
    """Settings for the Approver Agent - ENABLED BY DEFAULT."""

    enabled: bool = True  # ON BY DEFAULT
    auto_approve_quality_gates: bool = True
    block_merge_on_failure: bool = True
    coverage: CoverageSettings = Field(default_factory=CoverageSettings)
    subagents: ApproverSubagentSettings = Field(default_factory=ApproverSubagentSettings)


class BugAutomationAgentSettings(BaseModel):
    """Settings for the Bug Automation Agent."""

    enabled: bool = True
    standalone_mode: bool = False
    auto_create_issues: bool = True
    sla_monitoring: bool = True
    escalation_enabled: bool = True


class AgentsConfig(BaseModel):
    """Configuration for all agents."""

    approver_agent: ApproverAgentSettings = Field(default_factory=ApproverAgentSettings)
    bug_automation_agent: BugAutomationAgentSettings = Field(
        default_factory=BugAutomationAgentSettings
    )


class QualityGatesConfig(BaseModel):
    """Quality gates configuration."""

    pre_commit_lint: bool = True
    pre_commit_format: bool = True
    pre_commit_type_check: bool = True
    ci_unit_tests: bool = True
    ci_integration_tests: bool = True
    ci_coverage_check: bool = True
    ci_security_scan: bool = True
    merge_require_approver: bool = True
    merge_require_passing_tests: bool = True
    merge_require_coverage: bool = True


class TestingConfig(BaseModel):
    """Testing configuration."""

    coverage_line: int = 90
    coverage_branch: int = 85
    coverage_function: int = 95
    parallel_execution: bool = True
    timeout_per_test: int = 60


class GlobalSettings(BaseModel):
    """Global agent settings."""

    default_timeout: int = 300
    max_delegation_depth: int = 3
    metrics_enabled: bool = True
    log_level: str = "INFO"
    parallel_execution: bool = True


class AgentSettings(BaseModel):
    """Root settings model."""

    global_settings: GlobalSettings = Field(default_factory=GlobalSettings, alias="global")
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    quality_gates: QualityGatesConfig = Field(default_factory=QualityGatesConfig)
    testing: TestingConfig = Field(default_factory=TestingConfig)

    class Config:
        populate_by_name = True


# Global settings instance
_settings: AgentSettings | None = None


def _find_settings_file() -> Path | None:
    """Find the agent settings file."""
    candidates = [
        Path("agents/config/agent_settings.yaml"),
        Path("../agents/config/agent_settings.yaml"),
        Path(__file__).parent.parent.parent.parent.parent / "agents/config/agent_settings.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _apply_env_overrides(settings: AgentSettings) -> AgentSettings:
    """Apply environment variable overrides."""
    # Approver agent enabled
    if env_val := os.getenv("LATTICE_APPROVER_ENABLED"):
        settings.agents.approver_agent.enabled = env_val.lower() not in (
            "false",
            "0",
            "no",
        )

    # Coverage target
    if target := os.getenv("LATTICE_COVERAGE_TARGET"):
        try:
            settings.agents.approver_agent.coverage.target = int(target)
            settings.testing.coverage_line = int(target)
        except ValueError:
            pass

    # Coverage enforcement mode
    if mode := os.getenv("LATTICE_COVERAGE_MODE"):
        if mode in ("strict", "warn", "disabled"):
            settings.agents.approver_agent.coverage.enforcement_mode = mode

    # Auto create bugs
    if auto_bugs := os.getenv("LATTICE_AUTO_CREATE_BUGS"):
        settings.agents.bug_automation_agent.auto_create_issues = auto_bugs.lower() in (
            "true",
            "1",
            "yes",
        )

    # Metrics enabled
    if metrics := os.getenv("LATTICE_METRICS_ENABLED"):
        settings.global_settings.metrics_enabled = metrics.lower() in (
            "true",
            "1",
            "yes",
        )

    return settings


def load_settings(config_path: Path | None = None) -> AgentSettings:
    """
    Load settings from YAML with environment overrides.

    Args:
        config_path: Optional path to settings file. If None, searches default locations.

    Returns:
        AgentSettings instance with all configuration.
    """
    if config_path is None:
        config_path = _find_settings_file()

    settings_data: dict[str, Any] = {}

    if config_path and config_path.exists():
        with open(config_path) as f:
            raw_data = yaml.safe_load(f) or {}
            settings_data = raw_data.get("settings", {})

    settings = AgentSettings(**settings_data)
    settings = _apply_env_overrides(settings)

    return settings


def get_settings() -> AgentSettings:
    """
    Get the cached settings instance.

    Returns:
        AgentSettings instance (creates one if not exists).
    """
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def reset_settings() -> None:
    """Reset settings cache. Useful for testing."""
    global _settings
    _settings = None


def is_approver_enabled() -> bool:
    """Check if the Approver Agent is enabled."""
    return get_settings().agents.approver_agent.enabled


def get_coverage_target() -> int:
    """Get the current coverage target percentage."""
    return get_settings().agents.approver_agent.coverage.target
