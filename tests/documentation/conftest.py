"""Fixtures for documentation tests."""

from pathlib import Path

import pytest


@pytest.fixture
def docs_path():
    """Return path to docs directory."""
    return Path("docs")


@pytest.fixture
def markdown_files(docs_path):
    """Collect all markdown files in docs."""
    return list(docs_path.rglob("*.md")) if docs_path.exists() else []


@pytest.fixture
def all_markdown_files():
    """Collect all markdown files in project."""
    project_root = Path(".")
    md_files = []
    for pattern in ["*.md", "docs/**/*.md", "agents/**/*.md", ".github/**/*.md"]:
        md_files.extend(project_root.glob(pattern))
    return list(set(md_files))


@pytest.fixture
def readme_file():
    """Return path to README.md."""
    readme = Path("README.md")
    if not readme.exists():
        readme = Path("readme.md")
    return readme if readme.exists() else None
