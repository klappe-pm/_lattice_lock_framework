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
    """Load test secrets from environment or implementation-safe defaults."""
    return {
        "SECRET_KEY": os.getenv(
            "LATTICE_TEST_SECRET_KEY", "dummy-test-secret-key-must-be-min-32-chars"
        ),
        "PASSWORD": os.getenv("LATTICE_TEST_PASSWORD", "dummy_user_password"),
        "ADMIN_PASSWORD": os.getenv("LATTICE_TEST_ADMIN_PASSWORD", "dummy_admin_password"),
        "OPERATOR_PASSWORD": os.getenv("LATTICE_TEST_OPERATOR_PASSWORD", "dummy_operator_password"),
        "CUSTOM_SECRET_KEY": os.getenv(
            "LATTICE_TEST_CUSTOM_SECRET_KEY", "dummy-custom-secret-key-min-32-chars"
        ),
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
