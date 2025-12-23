"""
Pytest configuration for Lattice Lock Framework tests.

This module configures pytest to:
1. Configure asyncio mode for async tests
2. Provide common fixtures
"""

import os

import pytest

# ...


@pytest.fixture(scope="session")
def auth_secrets():
    """Load test secrets from environment or generate safe defaults."""
    import secrets
    
    def get_or_generate(key, length=32):
        return os.getenv(key) or secrets.token_urlsafe(length)

    return {
        "SECRET_KEY": get_or_generate("LATTICE_TEST_SECRET_KEY"),
        "PASSWORD": get_or_generate("LATTICE_TEST_PASSWORD", 16),
        "ADMIN_PASSWORD": get_or_generate("LATTICE_TEST_ADMIN_PASSWORD", 16),
        "OPERATOR_PASSWORD": get_or_generate("LATTICE_TEST_OPERATOR_PASSWORD", 16),
        "CUSTOM_SECRET_KEY": get_or_generate("LATTICE_TEST_CUSTOM_SECRET_KEY"),
    }




@pytest.fixture
def sample_prompt():
    """Sample prompt fixture for testing."""
    return "Write a Python function that calculates the factorial of a number"


@pytest.fixture
def sample_code_with_error():
    """Sample code with error for debugging tests."""
    return """
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']  # KeyError if items empty
    return total
"""
