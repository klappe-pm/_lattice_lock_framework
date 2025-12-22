import os
import shutil
import tempfile
from pathlib import Path

import pytest
from lattice_lock_validator.structure import validate_file_naming, validate_repository_structure


@pytest.fixture
def temp_repo():
    # Create a temporary directory structure mimicking a valid repo
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname)
        (path / "docs" / "agent_definitions").mkdir(parents=True)
        (path / "src").mkdir()
        (path / "scripts").mkdir()
        (path / ".gitignore").touch()
        (path / "README.md").touch()
        yield tmpdirname


def test_valid_structure(temp_repo):
    result = validate_repository_structure(temp_repo)
    assert result.valid
    assert len(result.errors) == 0


def test_missing_required_directory(temp_repo):
    shutil.rmtree(os.path.join(temp_repo, "docs"))
    result = validate_repository_structure(temp_repo)
    assert not result.valid
    assert any(
        "Missing required root directory: docs/" in e.message for e in result.errors
    )


def test_snake_case_violation(temp_repo):
    # Create a file with bad name
    (Path(temp_repo) / "src" / "BadName.py").touch()
    result = validate_repository_structure(temp_repo)
    assert not result.valid
    assert any("does not follow snake_case" in e.message for e in result.errors)


def test_space_in_filename(temp_repo):
    (Path(temp_repo) / "src" / "file with space.txt").touch()
    result = validate_repository_structure(temp_repo)
    assert not result.valid
    assert any("File name contains spaces" in e.message for e in result.errors)


def test_agent_definition_naming(temp_repo):
    # Valid
    cat_dir = Path(temp_repo) / "docs" / "agent_definitions" / "test_agent"
    cat_dir.mkdir()
    (cat_dir / "test_agent_my_agent_definition.yaml").touch()

    # Invalid name
    (cat_dir / "wrong_name.yaml").touch()

    result = validate_repository_structure(temp_repo)
    assert not result.valid
    assert any(
        "Agent definition 'wrong_name.yaml' must end with '_definition.yaml'" in e.message
        for e in result.errors
    )
    # The category check might depend on how path parts are parsed.
    # Let's check if the category error is present without being too specific on the message format if it's flaky,
    # but it should be deterministic.
    # Let's print errors if assertion fails
    error_messages = [e.message for e in result.errors]
    assert any(
        "must start with category prefix 'test_agent_'" in msg for msg in error_messages
    ), f"Errors: {error_messages}"


def test_file_naming_edge_cases():
    # Test file naming directly
    res = validate_file_naming(
        "/path/to/repo/agent_definitions/cat/cat_agent_def.yaml", "/path/to/repo"
    )
    assert not res.valid
    assert any("must end with '_definition.yaml'" in e.message for e in res.errors)

    res = validate_file_naming(
        "/path/to/repo/agent_definitions/cat/cat_def_definition.yaml", "/path/to/repo"
    )
    # Should be valid naming-wise if snake_case is followed
    # cat_def_definition.yaml is snake_case.
    # But it must start with category prefix 'cat_'
    # Here category is 'cat'. Prefix is 'cat_'. Filename starts with 'cat_'.
    # So it should be valid?
    # Wait, validate_file_naming doesn't check validity of the file content, just name.
    # And snake_case.
    assert res.valid

    res = validate_file_naming(
        "/path/to/repo/agent_definitions/cat/other_definition.yaml", "/path/to/repo"
    )
    assert not res.valid
    assert any("must start with category prefix 'cat_'" in e.message for e in res.errors)


def test_prohibited_files():
    res = validate_file_naming("test.tmp")
    assert not res.valid
    assert any("Prohibited file type/name" in e.message for e in res.errors)

    res = validate_file_naming(".DS_Store")
    assert not res.valid
    assert any("Prohibited file type/name" in e.message for e in res.errors)
