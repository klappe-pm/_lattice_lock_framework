"""
Lattice Lock Error Remediation

Maps error types to remediation steps and documentation links.
Provides actionable guidance for resolving errors.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from lattice_lock.errors.types import (
    AgentError,
    ConfigurationError,
    GauntletFailureError,
    LatticeRuntimeError,
    NetworkError,
    SchemaValidationError,
    SheriffViolationError,
)

DOCS_BASE_URL = "https://docs.lattice-lock.dev"


@dataclass
class RemediationInfo:
    """Information for remediating an error.

    Attributes:
        steps: Ordered list of steps to fix the error
        documentation_url: Link to relevant documentation
        examples: Example code or commands that may help
    """

    steps: list[str] = field(default_factory=list)
    documentation_url: str | None = None
    examples: list[str] = field(default_factory=list)


def _remediate_schema_validation(error: SchemaValidationError) -> RemediationInfo:
    """Generate remediation for schema validation errors."""
    steps = [
        "Review the lattice.yaml file for syntax errors",
        "Ensure all required fields are present in entity definitions",
        "Verify field types match supported types (str, int, bool, float, list, dict)",
        "Check that constraints use valid operators (gt, lt, gte, lte, eq, ne)",
        "Run 'lattice-lock validate --verbose' for detailed error information",
    ]

    if error.validation_errors:
        steps.insert(
            0, f"Fix the following validation errors: {', '.join(error.validation_errors)}"
        )

    if error.schema_path:
        steps.insert(0, f"Open the schema file at: {error.schema_path}")

    return RemediationInfo(
        steps=steps,
        documentation_url=f"{DOCS_BASE_URL}/schema/validation",
        examples=[
            "# Valid entity definition example:",
            "entities:",
            "  User:",
            "    fields:",
            "      id: int",
            "      email: str",
            "    constraints:",
            "      email: {unique: true}",
        ],
    )


def _remediate_sheriff_violation(error: SheriffViolationError) -> RemediationInfo:
    """Generate remediation for Sheriff AST validation errors."""
    steps = [
        "Review the generated code for import discipline violations",
        "Ensure all functions and methods have type hints",
        "Remove any forbidden imports (check Sheriff configuration)",
        "Run 'lattice-lock sheriff --fix' to auto-fix some violations",
    ]

    if error.file_path:
        steps.insert(0, f"Open the file at: {error.file_path}")
        if error.line_number:
            steps[0] += f" (line {error.line_number})"

    if error.violation_type:
        violation_steps = {
            "missing_type_hint": [
                "Add type hints to all function parameters and return values",
                "Use 'from typing import ...' for complex types",
            ],
            "forbidden_import": [
                "Remove the forbidden import",
                "Use an approved alternative from the allowed imports list",
            ],
            "missing_docstring": [
                "Add a docstring to the function or class",
                "Follow Google-style docstring format",
            ],
        }
        if error.violation_type in violation_steps:
            steps = violation_steps[error.violation_type] + steps

    return RemediationInfo(
        steps=steps,
        documentation_url=f"{DOCS_BASE_URL}/governance/sheriff",
        examples=[
            "# Correct type hints example:",
            "def process_user(user_id: int, name: str) -> dict[str, Any]:",
            '    """Process a user record."""',
            "    return {'id': user_id, 'name': name}",
        ],
    )


def _remediate_gauntlet_failure(error: GauntletFailureError) -> RemediationInfo:
    """Generate remediation for Gauntlet semantic contract failures."""
    steps = [
        "Review the failing test to understand the expected behavior",
        "Check that the implementation matches the 'ensures' clauses in lattice.yaml",
        "Verify business logic constraints are correctly implemented",
        "Run 'pytest -v' to see detailed test output",
    ]

    if error.test_file:
        steps.insert(0, f"Open the test file at: {error.test_file}")
        if error.test_name:
            steps.insert(1, f"Focus on test: {error.test_name}")

    if error.assertion_error:
        steps.insert(0, f"Assertion failed: {error.assertion_error}")

    return RemediationInfo(
        steps=steps,
        documentation_url=f"{DOCS_BASE_URL}/governance/gauntlet",
        examples=[
            "# Ensure clause in lattice.yaml:",
            "entities:",
            "  User:",
            "    ensures:",
            '      - "age >= 18"',
            '      - "email contains @"',
        ],
    )


def _remediate_runtime_error(error: LatticeRuntimeError) -> RemediationInfo:
    """Generate remediation for runtime errors."""
    steps = [
        "Check the operation that failed and its inputs",
        "Verify all required dependencies are installed",
        "Check system resources (memory, disk space)",
        "Review logs for additional context",
    ]

    if error.operation:
        steps.insert(0, f"The operation '{error.operation}' failed")

    if error.cause:
        steps.insert(1, f"Underlying cause: {error.cause}")

    return RemediationInfo(
        steps=steps,
        documentation_url=f"{DOCS_BASE_URL}/troubleshooting/runtime",
    )


def _remediate_configuration_error(error: ConfigurationError) -> RemediationInfo:
    """Generate remediation for configuration errors."""
    steps = [
        "Check that all required environment variables are set",
        "Verify configuration file syntax (YAML, JSON, etc.)",
        "Ensure configuration values match expected types",
        "Copy .env.example to .env and fill in required values",
    ]

    if error.config_key:
        steps.insert(0, f"Missing or invalid configuration: {error.config_key}")

    if error.config_file:
        steps.insert(1, f"Check configuration file: {error.config_file}")

    if error.expected_type:
        steps.append(f"Expected type for value: {error.expected_type}")

    return RemediationInfo(
        steps=steps,
        documentation_url=f"{DOCS_BASE_URL}/configuration",
        examples=[
            "# Required environment variables:",
            "export OPENAI_API_KEY=sk-...",
            "export ANTHROPIC_API_KEY=sk-ant-...",
            "export ORCHESTRATOR_STRATEGY=balanced",
        ],
    )


def _remediate_network_error(error: NetworkError) -> RemediationInfo:
    """Generate remediation for network errors."""
    steps = [
        "Check your internet connection",
        "Verify the API endpoint is accessible",
        "Check API key validity and permissions",
        "Review rate limits and quotas",
        "Try again after a short delay",
    ]

    if error.url:
        steps.insert(0, f"Failed to connect to: {error.url}")

    if error.status_code:
        status_steps = {
            401: ["Verify your API key is correct and not expired"],
            403: ["Check that your API key has the required permissions"],
            404: ["Verify the endpoint URL is correct"],
            429: ["You've hit rate limits - wait before retrying"],
            500: ["The server encountered an error - try again later"],
            502: ["Bad gateway - the upstream server is unavailable"],
            503: ["Service unavailable - try again later"],
        }
        if error.status_code in status_steps:
            steps = status_steps[error.status_code] + steps
        steps.insert(0, f"HTTP status code: {error.status_code}")

    return RemediationInfo(
        steps=steps,
        documentation_url=f"{DOCS_BASE_URL}/troubleshooting/network",
    )


def _remediate_agent_error(error: AgentError) -> RemediationInfo:
    """Generate remediation for agent errors."""
    steps = [
        "Check the agent definition file for syntax errors",
        "Verify the agent memory file is accessible",
        "Ensure all subagents are properly configured",
        "Check token usage and limits",
        "Review agent interaction logs",
    ]

    if error.agent_name:
        steps.insert(0, f"Agent '{error.agent_name}' encountered an error")

    if error.subagent_name:
        steps.insert(1, f"Subagent involved: {error.subagent_name}")

    if error.operation:
        steps.insert(2, f"Failed operation: {error.operation}")

    return RemediationInfo(
        steps=steps,
        documentation_url=f"{DOCS_BASE_URL}/agents/troubleshooting",
    )


def _remediate_generic(error: Exception) -> RemediationInfo:
    """Generate generic remediation for unknown errors."""
    return RemediationInfo(
        steps=[
            "Review the error message for specific details",
            "Check the stack trace for the source of the error",
            "Search the documentation for related issues",
            "If the issue persists, report it on GitHub",
        ],
        documentation_url=f"{DOCS_BASE_URL}/troubleshooting",
    )


REMEDIATION_MAP: dict[type[Exception], Callable[[Exception], RemediationInfo]] = {
    SchemaValidationError: _remediate_schema_validation,
    SheriffViolationError: _remediate_sheriff_violation,
    GauntletFailureError: _remediate_gauntlet_failure,
    LatticeRuntimeError: _remediate_runtime_error,
    ConfigurationError: _remediate_configuration_error,
    NetworkError: _remediate_network_error,
    AgentError: _remediate_agent_error,
}


def get_remediation(error: Exception) -> RemediationInfo:
    """Get remediation information for an error.

    Looks up the error type in the remediation map and generates
    appropriate remediation steps.

    Args:
        error: The exception to get remediation for

    Returns:
        RemediationInfo with steps and documentation link
    """
    for error_class, remediation_func in REMEDIATION_MAP.items():
        if isinstance(error, error_class):
            return remediation_func(error)

    return _remediate_generic(error)


def format_remediation(error: Exception) -> str:
    """Format remediation information as a human-readable string.

    Args:
        error: The exception to format remediation for

    Returns:
        Formatted string with numbered steps and documentation link
    """
    info = get_remediation(error)
    lines = ["Remediation Steps:", ""]

    for i, step in enumerate(info.steps, 1):
        lines.append(f"  {i}. {step}")

    if info.documentation_url:
        lines.append("")
        lines.append(f"Documentation: {info.documentation_url}")

    if info.examples:
        lines.append("")
        lines.append("Example:")
        for example in info.examples:
            lines.append(f"  {example}")

    return "\n".join(lines)
