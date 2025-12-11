"""
Tests for lattice.yaml examples and fixtures.

This module validates that:
1. All example schemas are valid
2. Invalid fixtures produce appropriate errors
3. The schema validator catches common mistakes
"""
import pytest
from pathlib import Path

from lattice_lock_validator.schema import validate_lattice_schema, ValidationResult
from lattice_lock_gauntlet.parser import LatticeParser


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"


class TestValidExamples:
    """Test that all example schemas pass validation."""

    def test_basic_example_is_valid(self):
        """Basic example should pass validation."""
        schema_path = EXAMPLES_DIR / "basic" / "lattice.yaml"
        result = validate_lattice_schema(str(schema_path))

        assert result.valid, f"Basic example should be valid. Errors: {[e.message for e in result.errors]}"
        assert len(result.errors) == 0

    def test_advanced_example_is_valid(self):
        """Advanced example should pass validation."""
        schema_path = EXAMPLES_DIR / "advanced" / "lattice.yaml"
        result = validate_lattice_schema(str(schema_path))

        assert result.valid, f"Advanced example should be valid. Errors: {[e.message for e in result.errors]}"
        assert len(result.errors) == 0

    def test_root_example_is_valid(self):
        """Root examples/lattice.yaml should pass validation."""
        schema_path = EXAMPLES_DIR / "lattice.yaml"
        if schema_path.exists():
            result = validate_lattice_schema(str(schema_path))
            assert result.valid, f"Root example should be valid. Errors: {[e.message for e in result.errors]}"


class TestValidFixtures:
    """Test that valid fixtures pass validation."""

    def test_valid_fixture_passes(self):
        """Valid fixture should pass validation."""
        schema_path = FIXTURES_DIR / "valid_lattice.yaml"
        result = validate_lattice_schema(str(schema_path))

        assert result.valid, f"Valid fixture should pass. Errors: {[e.message for e in result.errors]}"
        assert len(result.errors) == 0


class TestInvalidFixtures:
    """Test that invalid fixtures produce appropriate errors."""

    def test_missing_version_is_invalid(self):
        """Missing version field should produce error."""
        schema_path = FIXTURES_DIR / "invalid_lattice_missing_version.yaml"
        result = validate_lattice_schema(str(schema_path))

        assert not result.valid, "Missing version should be invalid"
        error_messages = [e.message for e in result.errors]
        assert any("version" in msg.lower() for msg in error_messages), \
            f"Should mention missing version. Got: {error_messages}"

    def test_missing_entities_is_invalid(self):
        """Missing entities section should produce error."""
        schema_path = FIXTURES_DIR / "invalid_lattice_missing_entities.yaml"
        result = validate_lattice_schema(str(schema_path))

        assert not result.valid, "Missing entities should be invalid"
        error_messages = [e.message for e in result.errors]
        assert any("entities" in msg.lower() for msg in error_messages), \
            f"Should mention missing entities. Got: {error_messages}"

    def test_bad_type_is_invalid(self):
        """Unknown field type should produce error."""
        schema_path = FIXTURES_DIR / "invalid_lattice_bad_type.yaml"
        result = validate_lattice_schema(str(schema_path))

        assert not result.valid, "Unknown type should be invalid"
        error_messages = [e.message for e in result.errors]
        assert any("type" in msg.lower() or "money" in msg.lower() for msg in error_messages), \
            f"Should mention invalid type. Got: {error_messages}"

    def test_numeric_constraint_on_string_is_invalid(self):
        """Numeric constraint on string field should produce error."""
        schema_path = FIXTURES_DIR / "invalid_lattice_numeric_constraint_on_string.yaml"
        result = validate_lattice_schema(str(schema_path))

        assert not result.valid, "Numeric constraint on string should be invalid"
        error_messages = [e.message for e in result.errors]
        assert any("numeric" in msg.lower() or "constraint" in msg.lower() for msg in error_messages), \
            f"Should mention invalid constraint. Got: {error_messages}"

    def test_bad_version_format_is_invalid(self):
        """Malformed version string should produce error."""
        schema_path = FIXTURES_DIR / "invalid_lattice_bad_version.yaml"
        result = validate_lattice_schema(str(schema_path))

        assert not result.valid, "Bad version format should be invalid"
        error_messages = [e.message for e in result.errors]
        assert any("version" in msg.lower() for msg in error_messages), \
            f"Should mention version format. Got: {error_messages}"

    def test_ensures_unknown_field_is_invalid(self):
        """Ensures clause referencing unknown field should produce error."""
        schema_path = FIXTURES_DIR / "invalid_lattice_ensures_unknown_field.yaml"
        result = validate_lattice_schema(str(schema_path))

        assert not result.valid, "Unknown field in ensures should be invalid"
        error_messages = [e.message for e in result.errors]
        assert any("field" in msg.lower() or "unknown" in msg.lower() or "nonexistent" in msg.lower()
                   for msg in error_messages), \
            f"Should mention unknown field. Got: {error_messages}"


class TestLatticeParser:
    """Test the Gauntlet parser with examples."""

    def test_parse_basic_example(self):
        """Parser should extract entities from basic example."""
        schema_path = EXAMPLES_DIR / "basic" / "lattice.yaml"
        parser = LatticeParser(str(schema_path))
        entities = parser.parse()

        assert len(entities) == 2, f"Expected 2 entities, got {len(entities)}"
        entity_names = {e.name for e in entities}
        assert "User" in entity_names
        assert "Post" in entity_names

    def test_parse_advanced_example(self):
        """Parser should extract entities from advanced example."""
        schema_path = EXAMPLES_DIR / "advanced" / "lattice.yaml"
        parser = LatticeParser(str(schema_path))
        entities = parser.parse()

        assert len(entities) == 5, f"Expected 5 entities, got {len(entities)}"
        entity_names = {e.name for e in entities}
        assert "Customer" in entity_names
        assert "Product" in entity_names
        assert "Order" in entity_names
        assert "Payment" in entity_names
        assert "Review" in entity_names

    def test_parse_extracts_ensures_clauses(self):
        """Parser should extract ensures clauses from entities."""
        schema_path = EXAMPLES_DIR / "advanced" / "lattice.yaml"
        parser = LatticeParser(str(schema_path))
        entities = parser.parse()

        # Find Order entity which has explicit ensures
        order_entity = next((e for e in entities if e.name == "Order"), None)
        assert order_entity is not None, "Order entity not found"

        # Should have ensures clauses (both implicit from constraints and explicit)
        assert len(order_entity.ensures) > 0, "Order should have ensures clauses"

    def test_parse_extracts_field_constraints(self):
        """Parser should extract implicit constraints from fields."""
        schema_path = FIXTURES_DIR / "valid_lattice.yaml"
        parser = LatticeParser(str(schema_path))
        entities = parser.parse()

        # Find TestEntity
        test_entity = next((e for e in entities if e.name == "TestEntity"), None)
        assert test_entity is not None, "TestEntity not found"

        # Should have extracted constraints from integer_field (gte, lte)
        constraint_fields = {c.field for c in test_entity.ensures}
        assert "integer_field" in constraint_fields, "Should extract integer_field constraints"


class TestExampleDocumentation:
    """Test that examples have proper documentation."""

    def test_basic_example_has_comments(self):
        """Basic example should have explanatory comments."""
        schema_path = EXAMPLES_DIR / "basic" / "lattice.yaml"
        content = schema_path.read_text()

        # Should have comment explaining what this is
        assert "#" in content, "Example should have comments"

    def test_advanced_example_has_comments(self):
        """Advanced example should have explanatory comments."""
        schema_path = EXAMPLES_DIR / "advanced" / "lattice.yaml"
        content = schema_path.read_text()

        # Should have comment explaining features
        assert "#" in content, "Example should have comments"
        assert "interface" in content.lower() or "entities" in content.lower()
