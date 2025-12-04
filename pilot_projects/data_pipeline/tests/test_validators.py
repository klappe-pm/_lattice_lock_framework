"""
Tests for data validators.

Validates validation rule enforcement.
"""

import pytest
from src.validators import (
    RuleType,
    Severity,
    ValidationRule,
    ValidationResult,
    RequiredValidator,
    TypeCheckValidator,
    RangeValidator,
    RegexValidator,
    ValidationEngine,
)


class TestRequiredValidator:
    """Tests for RequiredValidator."""

    def test_valid_when_field_present(self) -> None:
        """Test validation passes when field is present."""
        rule = ValidationRule(
            id=1,
            name="require_name",
            rule_type=RuleType.REQUIRED,
            field_name="name",
            rule_config={},
        )
        validator = RequiredValidator(rule)

        result = validator.validate({"name": "John"})

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid_when_field_missing(self) -> None:
        """Test validation fails when field is missing."""
        rule = ValidationRule(
            id=1,
            name="require_name",
            rule_type=RuleType.REQUIRED,
            field_name="name",
            rule_config={},
            severity=Severity.ERROR,
        )
        validator = RequiredValidator(rule)

        result = validator.validate({"age": 25})

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "missing" in result.errors[0]

    def test_invalid_when_field_empty(self) -> None:
        """Test validation fails when field is empty."""
        rule = ValidationRule(
            id=1,
            name="require_name",
            rule_type=RuleType.REQUIRED,
            field_name="name",
            rule_config={},
            severity=Severity.ERROR,
        )
        validator = RequiredValidator(rule)

        result = validator.validate({"name": ""})

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "empty" in result.errors[0]

    def test_warning_severity(self) -> None:
        """Test that warning severity adds to warnings."""
        rule = ValidationRule(
            id=1,
            name="require_name",
            rule_type=RuleType.REQUIRED,
            field_name="name",
            rule_config={},
            severity=Severity.WARNING,
        )
        validator = RequiredValidator(rule)

        result = validator.validate({"age": 25})

        assert result.is_valid is True
        assert len(result.warnings) == 1


class TestTypeCheckValidator:
    """Tests for TypeCheckValidator."""

    def test_valid_string_type(self) -> None:
        """Test validation passes for correct string type."""
        rule = ValidationRule(
            id=1,
            name="check_name_type",
            rule_type=RuleType.TYPE_CHECK,
            field_name="name",
            rule_config={"type": "str"},
        )
        validator = TypeCheckValidator(rule)

        result = validator.validate({"name": "John"})

        assert result.is_valid is True

    def test_invalid_type(self) -> None:
        """Test validation fails for incorrect type."""
        rule = ValidationRule(
            id=1,
            name="check_age_type",
            rule_type=RuleType.TYPE_CHECK,
            field_name="age",
            rule_config={"type": "int"},
            severity=Severity.ERROR,
        )
        validator = TypeCheckValidator(rule)

        result = validator.validate({"age": "twenty-five"})

        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_valid_int_type(self) -> None:
        """Test validation passes for correct int type."""
        rule = ValidationRule(
            id=1,
            name="check_age_type",
            rule_type=RuleType.TYPE_CHECK,
            field_name="age",
            rule_config={"type": "int"},
        )
        validator = TypeCheckValidator(rule)

        result = validator.validate({"age": 25})

        assert result.is_valid is True


class TestRangeValidator:
    """Tests for RangeValidator."""

    def test_valid_within_range(self) -> None:
        """Test validation passes when value is within range."""
        rule = ValidationRule(
            id=1,
            name="check_age_range",
            rule_type=RuleType.RANGE,
            field_name="age",
            rule_config={"min": 0, "max": 120},
        )
        validator = RangeValidator(rule)

        result = validator.validate({"age": 25})

        assert result.is_valid is True

    def test_invalid_below_min(self) -> None:
        """Test validation fails when value is below minimum."""
        rule = ValidationRule(
            id=1,
            name="check_age_range",
            rule_type=RuleType.RANGE,
            field_name="age",
            rule_config={"min": 18},
            severity=Severity.ERROR,
        )
        validator = RangeValidator(rule)

        result = validator.validate({"age": 15})

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "below minimum" in result.errors[0]

    def test_invalid_above_max(self) -> None:
        """Test validation fails when value is above maximum."""
        rule = ValidationRule(
            id=1,
            name="check_price_range",
            rule_type=RuleType.RANGE,
            field_name="price",
            rule_config={"max": 100},
            severity=Severity.ERROR,
        )
        validator = RangeValidator(rule)

        result = validator.validate({"price": 150})

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "above maximum" in result.errors[0]


class TestRegexValidator:
    """Tests for RegexValidator."""

    def test_valid_email_pattern(self) -> None:
        """Test validation passes for valid email pattern."""
        rule = ValidationRule(
            id=1,
            name="check_email",
            rule_type=RuleType.REGEX,
            field_name="email",
            rule_config={"pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
        )
        validator = RegexValidator(rule)

        result = validator.validate({"email": "test@example.com"})

        assert result.is_valid is True

    def test_invalid_email_pattern(self) -> None:
        """Test validation fails for invalid email pattern."""
        rule = ValidationRule(
            id=1,
            name="check_email",
            rule_type=RuleType.REGEX,
            field_name="email",
            rule_config={"pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
            severity=Severity.ERROR,
        )
        validator = RegexValidator(rule)

        result = validator.validate({"email": "invalid-email"})

        assert result.is_valid is False
        assert len(result.errors) == 1


class TestValidationEngine:
    """Tests for ValidationEngine."""

    def test_multiple_rules(self) -> None:
        """Test engine with multiple rules."""
        engine = ValidationEngine()

        engine.add_rule(ValidationRule(
            id=1,
            name="require_name",
            rule_type=RuleType.REQUIRED,
            field_name="name",
            rule_config={},
        ))
        engine.add_rule(ValidationRule(
            id=2,
            name="check_age_range",
            rule_type=RuleType.RANGE,
            field_name="age",
            rule_config={"min": 0, "max": 120},
        ))

        result = engine.validate({"name": "John", "age": 25})

        assert result.is_valid is True

    def test_combined_errors(self) -> None:
        """Test that engine combines errors from multiple validators."""
        engine = ValidationEngine()

        engine.add_rule(ValidationRule(
            id=1,
            name="require_name",
            rule_type=RuleType.REQUIRED,
            field_name="name",
            rule_config={},
            severity=Severity.ERROR,
        ))
        engine.add_rule(ValidationRule(
            id=2,
            name="check_age_range",
            rule_type=RuleType.RANGE,
            field_name="age",
            rule_config={"min": 18},
            severity=Severity.ERROR,
        ))

        result = engine.validate({"age": 15})

        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_inactive_rules_ignored(self) -> None:
        """Test that inactive rules are ignored."""
        engine = ValidationEngine()

        engine.add_rule(ValidationRule(
            id=1,
            name="require_name",
            rule_type=RuleType.REQUIRED,
            field_name="name",
            rule_config={},
            is_active=False,
        ))

        result = engine.validate({})

        assert result.is_valid is True
