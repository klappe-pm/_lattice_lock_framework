"""
Pytest configuration for Lattice Lock Framework tests.

This module configures pytest to:
1. Configure asyncio mode for async tests
2. Provide common fixtures
"""
import pytest


# Legacy test files skip list - imports normalized as of 2025-12-14
# Only skip files that genuinely can't be run
LEGACY_TEST_FILES = [
    "test_tool_matcher.py",  # Requires lattice_lock_agents package which may not exist
]


def pytest_ignore_collect(collection_path, config):
    """Skip legacy test files with broken imports."""
    if collection_path.name in LEGACY_TEST_FILES:
        return True
    return False


@pytest.fixture
def sample_prompt():
    """Sample prompt fixture for testing."""
    return "Write a Python function that calculates the factorial of a number"


@pytest.fixture
def sample_code_with_error():
    """Sample code with error for debugging tests."""
    return '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']  # KeyError if items empty
    return total
'''
