"""
Tests for the Lattice Lock error classification system.

Tests error types, classification, and remediation functionality.
"""

import pytest

from lattice_lock.errors import (
    LatticeError,
    SchemaValidationError,
    SheriffViolationError,
    GauntletFailureError,
    LatticeRuntimeError,
    ConfigurationError,
    NetworkError,
    AgentError,
    Severity,
    Category,
    Recoverability,
    ErrorContext,
    classify_error,
    get_severity,
    get_category,
    get_recoverability,
    get_remediation,
    format_remediation,
    RemediationInfo,
)


class TestErrorTypes:
    """Tests for error type hierarchy."""

    def test_lattice_error_is_base_exception(self) -> None:
        """Test that LatticeError inherits from Exception."""
        error = LatticeError("Test error")
        assert isinstance(error, Exception)

    def test_lattice_error_has_error_code(self) -> None:
        """Test that LatticeError has default error code."""
        error = LatticeError("Test error")
        assert error.error_code == "LL-000"

    def test_lattice_error_custom_error_code(self) -> None:
        """Test that LatticeError accepts custom error code."""
        error = LatticeError("Test error", error_code="LL-999")
        assert error.error_code == "LL-999"

    def test_lattice_error_str_includes_code(self) -> None:
        """Test that str(error) includes error code."""
        error = LatticeError("Test error", error_code="LL-001")
        assert "[LL-001]" in str(error)
        assert "Test error" in str(error)

    def test_lattice_error_to_dict(self) -> None:
        """Test error serialization to dictionary."""
        error = LatticeError("Test error", error_code="LL-001", details={"key": "value"})
        result = error.to_dict()
        assert result["error_code"] == "LL-001"
        assert result["message"] == "Test error"
        assert result["details"] == {"key": "value"}
        assert result["type"] == "LatticeError"

    def test_schema_validation_error_inherits_from_lattice_error(self) -> None:
        """Test SchemaValidationError inheritance."""
        error = SchemaValidationError("Schema invalid")
        assert isinstance(error, LatticeError)
        assert error.error_code == "LL-100"

    def test_schema_validation_error_with_path(self) -> None:
        """Test SchemaValidationError with schema path."""
        error = SchemaValidationError(
            "Schema invalid",
            schema_path="/path/to/lattice.yaml",
            validation_errors=["Missing field 'id'"],
        )
        assert error.schema_path == "/path/to/lattice.yaml"
        assert "Missing field 'id'" in error.validation_errors
        assert error.details["schema_path"] == "/path/to/lattice.yaml"

    def test_sheriff_violation_error(self) -> None:
        """Test SheriffViolationError attributes."""
        error = SheriffViolationError(
            "Missing type hint",
            file_path="/path/to/file.py",
            line_number=42,
            violation_type="missing_type_hint",
        )
        assert isinstance(error, LatticeError)
        assert error.error_code == "LL-200"
        assert error.file_path == "/path/to/file.py"
        assert error.line_number == 42
        assert error.violation_type == "missing_type_hint"

    def test_gauntlet_failure_error(self) -> None:
        """Test GauntletFailureError attributes."""
        error = GauntletFailureError(
            "Test failed",
            test_name="test_user_age_constraint",
            test_file="tests/contracts/test_user.py",
            assertion_error="assert 17 >= 18",
        )
        assert isinstance(error, LatticeError)
        assert error.error_code == "LL-300"
        assert error.test_name == "test_user_age_constraint"
        assert error.test_file == "tests/contracts/test_user.py"

    def test_runtime_error(self) -> None:
        """Test LatticeRuntimeError attributes."""
        cause = ValueError("Invalid value")
        error = LatticeRuntimeError(
            "Operation failed",
            operation="model_inference",
            cause=cause,
        )
        assert isinstance(error, LatticeError)
        assert error.error_code == "LL-400"
        assert error.operation == "model_inference"
        assert error.cause == cause

    def test_configuration_error(self) -> None:
        """Test ConfigurationError attributes."""
        error = ConfigurationError(
            "Missing API key",
            config_key="OPENAI_API_KEY",
            config_file=".env",
            expected_type="str",
        )
        assert isinstance(error, LatticeError)
        assert error.error_code == "LL-500"
        assert error.config_key == "OPENAI_API_KEY"
        assert error.config_file == ".env"

    def test_network_error(self) -> None:
        """Test NetworkError attributes."""
        error = NetworkError(
            "API request failed",
            url="https://api.openai.com/v1/chat",
            status_code=429,
            response_body="Rate limit exceeded",
        )
        assert isinstance(error, LatticeError)
        assert error.error_code == "LL-600"
        assert error.url == "https://api.openai.com/v1/chat"
        assert error.status_code == 429

    def test_agent_error(self) -> None:
        """Test AgentError attributes."""
        error = AgentError(
            "Agent failed",
            agent_name="prompt_architect",
            subagent_name="spec_analyzer",
            operation="analyze_specification",
        )
        assert isinstance(error, LatticeError)
        assert error.error_code == "LL-700"
        assert error.agent_name == "prompt_architect"
        assert error.subagent_name == "spec_analyzer"


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self) -> None:
        """Test all severity values exist."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"

    def test_severity_str(self) -> None:
        """Test severity string representation."""
        assert str(Severity.CRITICAL) == "critical"

    def test_severity_log_level(self) -> None:
        """Test severity to log level mapping."""
        assert Severity.CRITICAL.log_level == "CRITICAL"
        assert Severity.HIGH.log_level == "ERROR"
        assert Severity.MEDIUM.log_level == "WARNING"
        assert Severity.LOW.log_level == "INFO"


class TestCategory:
    """Tests for Category enum."""

    def test_category_values(self) -> None:
        """Test all category values exist."""
        assert Category.VALIDATION.value == "validation"
        assert Category.RUNTIME.value == "runtime"
        assert Category.CONFIGURATION.value == "configuration"
        assert Category.NETWORK.value == "network"
        assert Category.AGENT.value == "agent"
        assert Category.UNKNOWN.value == "unknown"


class TestRecoverability:
    """Tests for Recoverability enum."""

    def test_recoverability_values(self) -> None:
        """Test all recoverability values exist."""
        assert Recoverability.RECOVERABLE.value == "recoverable"
        assert Recoverability.MANUAL_INTERVENTION.value == "manual_intervention"
        assert Recoverability.FATAL.value == "fatal"

    def test_should_retry(self) -> None:
        """Test should_retry property."""
        assert Recoverability.RECOVERABLE.should_retry is True
        assert Recoverability.MANUAL_INTERVENTION.should_retry is False
        assert Recoverability.FATAL.should_retry is False


class TestClassifyError:
    """Tests for error classification."""

    def test_classify_schema_validation_error(self) -> None:
        """Test classification of SchemaValidationError."""
        error = SchemaValidationError("Invalid schema")
        context = classify_error(error)

        assert context.error_type == "SchemaValidationError"
        assert context.severity == Severity.HIGH
        assert context.category == Category.VALIDATION
        assert context.recoverability == Recoverability.MANUAL_INTERVENTION

    def test_classify_sheriff_violation_error(self) -> None:
        """Test classification of SheriffViolationError."""
        error = SheriffViolationError("Missing type hint")
        context = classify_error(error)

        assert context.severity == Severity.HIGH
        assert context.category == Category.VALIDATION

    def test_classify_network_error(self) -> None:
        """Test classification of NetworkError."""
        error = NetworkError("Connection failed")
        context = classify_error(error)

        assert context.severity == Severity.MEDIUM
        assert context.category == Category.NETWORK
        assert context.recoverability == Recoverability.RECOVERABLE

    def test_classify_unknown_error(self) -> None:
        """Test classification of unknown error type."""
        error = ValueError("Unknown error")
        context = classify_error(error)

        assert context.severity == Severity.MEDIUM
        assert context.category == Category.UNKNOWN
        assert context.recoverability == Recoverability.MANUAL_INTERVENTION

    def test_error_context_to_dict(self) -> None:
        """Test ErrorContext serialization."""
        error = ConfigurationError("Missing key", config_key="API_KEY")
        context = classify_error(error)
        result = context.to_dict()

        assert result["error_type"] == "ConfigurationError"
        assert result["severity"] == "high"
        assert result["category"] == "configuration"
        assert "API_KEY" in str(result["details"])

    def test_get_severity_helper(self) -> None:
        """Test get_severity helper function."""
        error = NetworkError("Failed")
        assert get_severity(error) == Severity.MEDIUM

    def test_get_category_helper(self) -> None:
        """Test get_category helper function."""
        error = AgentError("Failed")
        assert get_category(error) == Category.AGENT

    def test_get_recoverability_helper(self) -> None:
        """Test get_recoverability helper function."""
        error = LatticeRuntimeError("Failed")
        assert get_recoverability(error) == Recoverability.RECOVERABLE


class TestRemediation:
    """Tests for error remediation."""

    def test_get_remediation_returns_info(self) -> None:
        """Test that get_remediation returns RemediationInfo."""
        error = SchemaValidationError("Invalid schema")
        info = get_remediation(error)

        assert isinstance(info, RemediationInfo)
        assert len(info.steps) > 0
        assert info.documentation_url is not None

    def test_schema_validation_remediation_includes_steps(self) -> None:
        """Test schema validation remediation has relevant steps."""
        error = SchemaValidationError(
            "Invalid schema",
            schema_path="/path/to/lattice.yaml",
        )
        info = get_remediation(error)

        assert any("lattice.yaml" in step for step in info.steps)
        assert "schema" in info.documentation_url.lower()

    def test_network_error_remediation_includes_status_code(self) -> None:
        """Test network error remediation includes status code info."""
        error = NetworkError("Rate limited", status_code=429)
        info = get_remediation(error)

        assert any("429" in step or "rate" in step.lower() for step in info.steps)

    def test_format_remediation_produces_string(self) -> None:
        """Test format_remediation produces readable string."""
        error = ConfigurationError("Missing key", config_key="API_KEY")
        formatted = format_remediation(error)

        assert "Remediation Steps:" in formatted
        assert "1." in formatted
        assert "Documentation:" in formatted

    def test_remediation_for_unknown_error(self) -> None:
        """Test remediation for unknown error types."""
        error = ValueError("Unknown")
        info = get_remediation(error)

        assert len(info.steps) > 0
        assert info.documentation_url is not None


class TestErrorContextIntegration:
    """Integration tests for error context."""

    def test_full_error_workflow(self) -> None:
        """Test complete error classification and remediation workflow."""
        error = SheriffViolationError(
            "Missing type hint on function 'process_data'",
            file_path="src/processor.py",
            line_number=42,
            violation_type="missing_type_hint",
        )

        context = classify_error(error)

        assert context.error_type == "SheriffViolationError"
        assert context.error_code == "LL-200"
        assert context.severity == Severity.HIGH
        assert context.category == Category.VALIDATION
        assert context.recoverability == Recoverability.MANUAL_INTERVENTION
        assert len(context.remediation) > 0
        assert context.documentation_url is not None
        assert context.details["file_path"] == "src/processor.py"
        assert context.details["line_number"] == 42

    def test_error_context_preserves_original_error(self) -> None:
        """Test that ErrorContext preserves the original error."""
        error = GauntletFailureError("Test failed", test_name="test_user")
        context = classify_error(error)

        assert context.original_error is error
