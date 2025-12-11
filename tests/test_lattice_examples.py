"""Tests for lattice.yaml example files and test fixtures.

This module validates that:
1. Example files are valid and can be parsed
2. Test fixtures work correctly for validation testing
3. Invalid fixtures produce appropriate error messages
"""

import os
import pytest
from pathlib import Path

from src.lattice_lock_validator.schema import validate_lattice_schema


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestBasicExample:
    """Tests for the basic lattice.yaml example."""

    @pytest.fixture
    def basic_example_path(self):
        return str(PROJECT_ROOT / "examples" / "basic" / "lattice.yaml")

    def test_basic_example_exists(self, basic_example_path):
        """Verify the basic example file exists."""
        assert os.path.exists(basic_example_path), "Basic example file should exist"

    def test_basic_example_is_valid(self, basic_example_path):
        """Verify the basic example passes validation."""
        result = validate_lattice_schema(basic_example_path)
        assert result.valid, f"Basic example should be valid. Errors: {[e.message for e in result.errors]}"
        assert len(result.errors) == 0, "Basic example should have no errors"

    def test_basic_example_has_two_entities(self, basic_example_path):
        """Verify the basic example has exactly 2 entities."""
        import yaml
        with open(basic_example_path, 'r') as f:
            data = yaml.safe_load(f)
        assert len(data['entities']) == 2, "Basic example should have 2 entities"
        assert 'User' in data['entities'], "Basic example should have User entity"
        assert 'Product' in data['entities'], "Basic example should have Product entity"


class TestAdvancedExample:
    """Tests for the advanced lattice.yaml example."""

    @pytest.fixture
    def advanced_example_path(self):
        return str(PROJECT_ROOT / "examples" / "advanced" / "lattice.yaml")

    def test_advanced_example_exists(self, advanced_example_path):
        """Verify the advanced example file exists."""
        assert os.path.exists(advanced_example_path), "Advanced example file should exist"

    def test_advanced_example_is_valid(self, advanced_example_path):
        """Verify the advanced example passes validation."""
        result = validate_lattice_schema(advanced_example_path)
        assert result.valid, f"Advanced example should be valid. Errors: {[e.message for e in result.errors]}"
        assert len(result.errors) == 0, "Advanced example should have no errors"

    def test_advanced_example_has_multiple_entities(self, advanced_example_path):
        """Verify the advanced example has multiple entities."""
        import yaml
        with open(advanced_example_path, 'r') as f:
            data = yaml.safe_load(f)
        assert len(data['entities']) >= 3, "Advanced example should have at least 3 entities"

    def test_advanced_example_has_interfaces(self, advanced_example_path):
        """Verify the advanced example has interface definitions."""
        import yaml
        with open(advanced_example_path, 'r') as f:
            data = yaml.safe_load(f)
        assert 'interfaces' in data, "Advanced example should have interfaces"
        assert len(data['interfaces']) >= 1, "Advanced example should have at least 1 interface"

    def test_advanced_example_has_ensures_clauses(self, advanced_example_path):
        """Verify the advanced example has ensures clauses."""
        import yaml
        with open(advanced_example_path, 'r') as f:
            data = yaml.safe_load(f)

        has_ensures = False
        for entity_name, entity_def in data['entities'].items():
            if 'ensures' in entity_def:
                has_ensures = True
                break
        assert has_ensures, "Advanced example should have at least one entity with ensures clauses"


class TestValidFixture:
    """Tests for the valid test fixture."""

    @pytest.fixture
    def valid_fixture_path(self):
        return str(PROJECT_ROOT / "tests" / "fixtures" / "valid_lattice.yaml")

    def test_valid_fixture_exists(self, valid_fixture_path):
        """Verify the valid fixture file exists."""
        assert os.path.exists(valid_fixture_path), "Valid fixture file should exist"

    def test_valid_fixture_is_valid(self, valid_fixture_path):
        """Verify the valid fixture passes validation."""
        result = validate_lattice_schema(valid_fixture_path)
        assert result.valid, f"Valid fixture should be valid. Errors: {[e.message for e in result.errors]}"
        assert len(result.errors) == 0, "Valid fixture should have no errors"

    def test_valid_fixture_has_all_field_types(self, valid_fixture_path):
        """Verify the valid fixture exercises all field types."""
        import yaml
        with open(valid_fixture_path, 'r') as f:
            data = yaml.safe_load(f)

        # Collect all field types used
        field_types = set()
        for entity_name, entity_def in data['entities'].items():
            for field_name, field_def in entity_def.get('fields', {}).items():
                if 'type' in field_def:
                    field_types.add(field_def['type'])
                if 'enum' in field_def:
                    field_types.add('enum')

        expected_types = {'uuid', 'str', 'int', 'decimal', 'bool', 'enum'}
        assert expected_types.issubset(field_types), f"Valid fixture should use all field types. Missing: {expected_types - field_types}"


class TestInvalidFixture:
    """Tests for the invalid test fixture."""

    @pytest.fixture
    def invalid_fixture_path(self):
        return str(PROJECT_ROOT / "tests" / "fixtures" / "invalid_lattice.yaml")

    def test_invalid_fixture_exists(self, invalid_fixture_path):
        """Verify the invalid fixture file exists."""
        assert os.path.exists(invalid_fixture_path), "Invalid fixture file should exist"

    def test_invalid_fixture_fails_validation(self, invalid_fixture_path):
        """Verify the invalid fixture fails validation."""
        result = validate_lattice_schema(invalid_fixture_path)
        assert not result.valid, "Invalid fixture should fail validation"
        assert len(result.errors) > 0, "Invalid fixture should have errors"

    def test_invalid_fixture_detects_version_error(self, invalid_fixture_path):
        """Verify the invalid fixture detects version format error."""
        result = validate_lattice_schema(invalid_fixture_path)
        error_messages = [e.message for e in result.errors]
        assert any("version" in msg.lower() for msg in error_messages), \
            "Should detect invalid version format"

    def test_invalid_fixture_detects_missing_generated_module(self, invalid_fixture_path):
        """Verify the invalid fixture detects missing generated_module."""
        result = validate_lattice_schema(invalid_fixture_path)
        error_messages = [e.message for e in result.errors]
        assert any("generated_module" in msg.lower() for msg in error_messages), \
            "Should detect missing generated_module"

    def test_invalid_fixture_detects_unknown_field_type(self, invalid_fixture_path):
        """Verify the invalid fixture detects unknown field type."""
        result = validate_lattice_schema(invalid_fixture_path)
        error_messages = [e.message for e in result.errors]
        assert any("unknown_type" in msg.lower() or "unsupported" in msg.lower() for msg in error_messages), \
            "Should detect unknown field type"

    def test_invalid_fixture_detects_numeric_constraint_on_string(self, invalid_fixture_path):
        """Verify the invalid fixture detects numeric constraint on string field."""
        result = validate_lattice_schema(invalid_fixture_path)
        error_messages = [e.message for e in result.errors]
        assert any("numeric" in msg.lower() for msg in error_messages), \
            "Should detect numeric constraint on non-numeric field"

    def test_invalid_fixture_detects_undefined_entity_reference(self, invalid_fixture_path):
        """Verify the invalid fixture detects undefined entity reference."""
        result = validate_lattice_schema(invalid_fixture_path)
        error_messages = [e.message for e in result.errors]
        assert any("undefined" in msg.lower() or "undefinedentity" in msg.lower() for msg in error_messages), \
            "Should detect undefined entity reference"


class TestExistingExample:
    """Tests for the existing root-level lattice.yaml example."""

    @pytest.fixture
    def existing_example_path(self):
        return str(PROJECT_ROOT / "examples" / "lattice.yaml")

    def test_existing_example_exists(self, existing_example_path):
        """Verify the existing example file exists."""
        assert os.path.exists(existing_example_path), "Existing example file should exist"

    def test_existing_example_is_valid(self, existing_example_path):
        """Verify the existing example passes validation."""
        result = validate_lattice_schema(existing_example_path)
        assert result.valid, f"Existing example should be valid. Errors: {[e.message for e in result.errors]}"
