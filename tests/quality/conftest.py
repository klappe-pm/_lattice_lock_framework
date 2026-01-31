"""Fixtures for quality tests."""

from pathlib import Path

import pytest


@pytest.fixture
def src_path():
    """Return path to src directory."""
    return Path("src")


@pytest.fixture
def pyproject_path():
    """Return path to pyproject.toml."""
    return Path("pyproject.toml")


@pytest.fixture
def python_files(src_path):
    """Collect all Python files in src."""
    return list(src_path.rglob("*.py")) if src_path.exists() else []
