import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from lattice_lock.validator.structure import (
    main,
    validate_repository_structure,
)


@pytest.fixture
def temp_repo():
    """Create a temporary directory structure mimicking a valid repo."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname)
        # Fixed path to match internal validator expectation
        (path / "docs" / "agents" / "agent_definitions").mkdir(parents=True)
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
    assert any("Missing required root directory: docs/" in e.message for e in result.errors)


def test_snake_case_violation(temp_repo):
    (Path(temp_repo) / "src" / "BadName.py").touch()
    result = validate_repository_structure(temp_repo)
    assert not result.valid
    assert any("does not follow snake_case" in e.message for e in result.errors)


def test_agent_definition_naming(temp_repo):
    cat_dir = Path(temp_repo) / "docs" / "agents" / "agent_definitions" / "test_agent"
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


def test_main_cli_success(temp_repo):
    with (
        patch.object(sys, "argv", ["structure.py", str(temp_repo)]),
        patch.object(sys, "exit") as mock_exit,
    ):
        main()
        mock_exit.assert_called_with(0)


def test_main_cli_failure(tmp_path):
    # Empty dir should fail
    with (
        patch.object(sys, "argv", ["structure.py", str(tmp_path)]),
        patch.object(sys, "exit") as mock_exit,
    ):
        main()
        mock_exit.assert_called_with(1)
