"""
Lattice Lock Error Types

Defines the error hierarchy for the Lattice Lock Framework.
All framework-specific exceptions inherit from LatticeError.
"""

from typing import Any


class LatticeError(Exception):
    """Base exception for all Lattice Lock Framework errors.

    All framework-specific exceptions should inherit from this class
    to enable consistent error handling and classification.

    Attributes:
        message: Human-readable error description
        error_code: Machine-parseable error code (e.g., "LL-001")
        details: Additional context about the error
    """

    error_code: str = "LL-000"

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if error_code is not None:
            self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "type": self.__class__.__name__,
        }


class SchemaValidationError(LatticeError):
    """Error raised when schema validation fails.

    This error is raised during the Meta-Schema Validator phase
    when lattice.yaml files contain invalid schema definitions.

    Error codes: LL-100 to LL-199
    """

    error_code: str = "LL-100"

    def __init__(
        self,
        message: str,
        schema_path: str | None = None,
        validation_errors: list[str] | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if schema_path:
            details["schema_path"] = schema_path
        if validation_errors:
            details["validation_errors"] = validation_errors
        super().__init__(message, error_code, details)
        self.schema_path = schema_path
        self.validation_errors = validation_errors or []


class SheriffViolationError(LatticeError):
    """Error raised when Sheriff AST validation fails.

    This error is raised during the Sheriff validation phase
    when generated code violates import discipline or type hint requirements.

    Error codes: LL-200 to LL-299
    """

    error_code: str = "LL-200"

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        line_number: int | None = None,
        violation_type: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if file_path:
            details["file_path"] = file_path
        if line_number is not None:
            details["line_number"] = line_number
        if violation_type:
            details["violation_type"] = violation_type
        super().__init__(message, error_code, details)
        self.file_path = file_path
        self.line_number = line_number
        self.violation_type = violation_type


class GauntletFailureError(LatticeError):
    """Error raised when Gauntlet semantic contract tests fail.

    This error is raised during the Gauntlet validation phase
    when generated code fails pytest semantic contract tests.

    Error codes: LL-300 to LL-399
    """

    error_code: str = "LL-300"

    def __init__(
        self,
        message: str,
        test_name: str | None = None,
        test_file: str | None = None,
        assertion_error: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if test_name:
            details["test_name"] = test_name
        if test_file:
            details["test_file"] = test_file
        if assertion_error:
            details["assertion_error"] = assertion_error
        super().__init__(message, error_code, details)
        self.test_name = test_name
        self.test_file = test_file
        self.assertion_error = assertion_error


class LatticeRuntimeError(LatticeError):
    """Error raised during framework runtime operations.

    This error is raised when runtime operations fail,
    such as model orchestration, API calls, or file operations.

    Error codes: LL-400 to LL-499
    """

    error_code: str = "LL-400"

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        cause: Exception | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if operation:
            details["operation"] = operation
        if cause:
            details["cause"] = str(cause)
            details["cause_type"] = type(cause).__name__
        super().__init__(message, error_code, details)
        self.operation = operation
        self.cause = cause


class ConfigurationError(LatticeError):
    """Error raised when configuration is invalid or missing.

    This error is raised when environment variables, config files,
    or other configuration sources are invalid or missing.

    Error codes: LL-500 to LL-599
    """

    error_code: str = "LL-500"

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_file: str | None = None,
        expected_type: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        if config_file:
            details["config_file"] = config_file
        if expected_type:
            details["expected_type"] = expected_type
        super().__init__(message, error_code, details)
        self.config_key = config_key
        self.config_file = config_file
        self.expected_type = expected_type


class NetworkError(LatticeError):
    """Error raised when network operations fail.

    This error is raised when API calls, HTTP requests,
    or other network operations fail.

    Error codes: LL-600 to LL-699
    """

    error_code: str = "LL-600"

    def __init__(
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
        response_body: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if url:
            details["url"] = url
        if status_code is not None:
            details["status_code"] = status_code
        if response_body:
            details["response_body"] = response_body[:500]
        super().__init__(message, error_code, details)
        self.url = url
        self.status_code = status_code
        self.response_body = response_body


class AgentError(LatticeError):
    """Error raised when agent operations fail.

    This error is raised when agent orchestration, memory operations,
    or inter-agent communication fails.

    Error codes: LL-700 to LL-799
    """

    error_code: str = "LL-700"

    def __init__(
        self,
        message: str,
        agent_name: str | None = None,
        subagent_name: str | None = None,
        operation: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        if agent_name:
            details["agent_name"] = agent_name
        if subagent_name:
            details["subagent_name"] = subagent_name
        if operation:
            details["operation"] = operation
        super().__init__(message, error_code, details)
        self.agent_name = agent_name
        self.subagent_name = subagent_name
        self.operation = operation
