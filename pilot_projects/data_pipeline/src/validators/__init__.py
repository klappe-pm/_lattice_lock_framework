"""
Data validators for the pipeline.

Validators check transformed data against rules before loading.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Pattern
import re


class RuleType(Enum):
    """Types of validation rules."""
    REQUIRED = "required"
    TYPE_CHECK = "type_check"
    RANGE = "range"
    REGEX = "regex"
    CUSTOM = "custom"


class Severity(Enum):
    """Severity levels for validation errors."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationRule:
    """Rule for validating transformed data."""
    id: int
    name: str
    rule_type: RuleType
    field_name: str
    rule_config: dict[str, Any]
    severity: Severity = Severity.ERROR
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ValidationResult:
    """Result of validating a single record."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)


class BaseValidator(ABC):
    """Base class for all validators."""

    def __init__(self, rule: ValidationRule) -> None:
        self.rule = rule

    @abstractmethod
    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Validate the data against the rule."""
        pass


class RequiredValidator(BaseValidator):
    """Validator that checks for required fields."""

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Check if required field is present and not empty."""
        field_name = self.rule.field_name
        result = ValidationResult(is_valid=True)

        if field_name not in data:
            message = f"Required field '{field_name}' is missing"
            if self.rule.severity == Severity.ERROR:
                result.is_valid = False
                result.errors.append(message)
            elif self.rule.severity == Severity.WARNING:
                result.warnings.append(message)
            else:
                result.info.append(message)
        elif data[field_name] is None or data[field_name] == "":
            message = f"Required field '{field_name}' is empty"
            if self.rule.severity == Severity.ERROR:
                result.is_valid = False
                result.errors.append(message)
            elif self.rule.severity == Severity.WARNING:
                result.warnings.append(message)
            else:
                result.info.append(message)

        return result


class TypeCheckValidator(BaseValidator):
    """Validator that checks field types."""

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Check if field has the expected type."""
        field_name = self.rule.field_name
        result = ValidationResult(is_valid=True)

        if field_name not in data:
            return result

        value = data[field_name]
        expected_type = self.rule.rule_config.get("type", "str")

        type_mapping = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
        }

        expected = type_mapping.get(expected_type)
        if expected and not isinstance(value, expected):
            message = f"Field '{field_name}' expected type {expected_type}, got {type(value).__name__}"
            if self.rule.severity == Severity.ERROR:
                result.is_valid = False
                result.errors.append(message)
            elif self.rule.severity == Severity.WARNING:
                result.warnings.append(message)
            else:
                result.info.append(message)

        return result


class RangeValidator(BaseValidator):
    """Validator that checks numeric ranges."""

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Check if field value is within the specified range."""
        field_name = self.rule.field_name
        result = ValidationResult(is_valid=True)

        if field_name not in data:
            return result

        value = data[field_name]
        if not isinstance(value, (int, float)):
            return result

        config = self.rule.rule_config
        min_value = config.get("min")
        max_value = config.get("max")

        if min_value is not None and value < min_value:
            message = f"Field '{field_name}' value {value} is below minimum {min_value}"
            if self.rule.severity == Severity.ERROR:
                result.is_valid = False
                result.errors.append(message)
            elif self.rule.severity == Severity.WARNING:
                result.warnings.append(message)
            else:
                result.info.append(message)

        if max_value is not None and value > max_value:
            message = f"Field '{field_name}' value {value} is above maximum {max_value}"
            if self.rule.severity == Severity.ERROR:
                result.is_valid = False
                result.errors.append(message)
            elif self.rule.severity == Severity.WARNING:
                result.warnings.append(message)
            else:
                result.info.append(message)

        return result


class RegexValidator(BaseValidator):
    """Validator that checks field values against regex patterns."""

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Check if field value matches the regex pattern."""
        field_name = self.rule.field_name
        result = ValidationResult(is_valid=True)

        if field_name not in data:
            return result

        value = data[field_name]
        if not isinstance(value, str):
            return result

        pattern = self.rule.rule_config.get("pattern", "")
        if not re.match(pattern, value):
            message = f"Field '{field_name}' value does not match pattern '{pattern}'"
            if self.rule.severity == Severity.ERROR:
                result.is_valid = False
                result.errors.append(message)
            elif self.rule.severity == Severity.WARNING:
                result.warnings.append(message)
            else:
                result.info.append(message)

        return result


class ValidationEngine:
    """Engine that runs multiple validators on data."""

    def __init__(self) -> None:
        self._validators: list[BaseValidator] = []

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        if not rule.is_active:
            return

        validator_mapping = {
            RuleType.REQUIRED: RequiredValidator,
            RuleType.TYPE_CHECK: TypeCheckValidator,
            RuleType.RANGE: RangeValidator,
            RuleType.REGEX: RegexValidator,
        }

        validator_class = validator_mapping.get(rule.rule_type)
        if validator_class:
            self._validators.append(validator_class(rule))

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Run all validators on the data."""
        combined_result = ValidationResult(is_valid=True)

        for validator in self._validators:
            result = validator.validate(data)

            if not result.is_valid:
                combined_result.is_valid = False

            combined_result.errors.extend(result.errors)
            combined_result.warnings.extend(result.warnings)
            combined_result.info.extend(result.info)

        return combined_result


__all__ = [
    "RuleType",
    "Severity",
    "ValidationRule",
    "ValidationResult",
    "BaseValidator",
    "RequiredValidator",
    "TypeCheckValidator",
    "RangeValidator",
    "RegexValidator",
    "ValidationEngine",
]
