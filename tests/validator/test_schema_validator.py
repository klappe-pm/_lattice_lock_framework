import os
import tempfile

import pytest
from lattice_lock.validator.schema import validate_lattice_schema


@pytest.fixture
def valid_schema_content():
    return """
version: v2.1
generated_module: types_v2
entities:
  User:
    fields:
      id: { type: uuid, primary_key: true }
      name: { type: str }
      role: { enum: [admin, user] }
"""


@pytest.fixture
def temp_schema_file(valid_schema_content):
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(valid_schema_content)
        path = f.name
    yield path
    os.remove(path)


def test_valid_schema(temp_schema_file):
    result = validate_lattice_schema(temp_schema_file)
    assert result.valid
    assert len(result.errors) == 0


def test_missing_required_sections():
    content = """
version: v2.1
# missing generated_module and entities
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(content)
        path = f.name

    try:
        result = validate_lattice_schema(path)
        assert not result.valid
        error_msgs = [e.message for e in result.errors]
        assert "Missing required section: generated_module" in error_msgs
        assert "Missing required section: entities" in error_msgs
    finally:
        os.remove(path)


def test_invalid_version_format():
    content = """
version: 2.1
generated_module: types_v2
entities: {}
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(content)
        path = f.name

    try:
        result = validate_lattice_schema(path)
        assert not result.valid
        assert any("Invalid version format" in e.message for e in result.errors)
    finally:
        os.remove(path)


def test_undefined_entity_reference():
    content = """
version: v2.1
generated_module: types_v2
entities:
  User:
    fields:
      id: { type: uuid }
interfaces:
  UserService:
    methods:
      getUser:
        params:
          user: UnknownEntity
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(content)
        path = f.name

    try:
        result = validate_lattice_schema(path)
        assert not result.valid
        assert any("Undefined entity reference 'UnknownEntity'" in e.message for e in result.errors)
    finally:
        os.remove(path)


def test_invalid_field_type():
    content = """
version: v2.1
generated_module: types_v2
entities:
  User:
    fields:
      age: { type: unknown_type }
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(content)
        path = f.name

    try:
        result = validate_lattice_schema(path)
        assert not result.valid
        assert any("Unsupported field type: 'unknown_type'" in e.message for e in result.errors)
    finally:
        os.remove(path)


def test_numeric_constraint_on_string():
    content = """
version: v2.1
generated_module: types_v2
entities:
  User:
    fields:
      name: { type: str, gt: 10 }
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(content)
        path = f.name

    try:
        result = validate_lattice_schema(path)
        assert not result.valid
        assert any(
            "Numeric constraints used on non-numeric field" in e.message for e in result.errors
        )
    finally:
        os.remove(path)


def test_file_not_found():
    result = validate_lattice_schema("non_existent_file.yaml")
    assert not result.valid
    assert any("File not found" in e.message for e in result.errors)


def test_invalid_yaml_syntax():
    content = """
version: v2.1
entities:
  User: [
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(content)
        path = f.name

    try:
        result = validate_lattice_schema(path)
        assert not result.valid
        assert any("Invalid YAML format" in e.message for e in result.errors)
    finally:
        os.remove(path)


def test_malformed_definitions():
    content = """
version: v2.1
generated_module: types_v2
entities:
  User: "not a dict"
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(content)
        path = f.name

    try:
        result = validate_lattice_schema(path)
        assert not result.valid
        assert any(
            "Definition for entity 'User' must be a dictionary" in e.message for e in result.errors
        )
    finally:
        os.remove(path)


def test_malformed_fields():
    content = """
version: v2.1
generated_module: types_v2
entities:
  User:
    fields: "not a dict"
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write(content)
        path = f.name

    try:
        result = validate_lattice_schema(path)
        assert not result.valid
        assert any(
            "Fields for entity 'User' must be a dictionary" in e.message for e in result.errors
        )
    finally:
        os.remove(path)
