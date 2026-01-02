"""
Pytest configuration for Lattice Lock Framework tests.

This module configures pytest to:
1. Configure asyncio mode for async tests
2. Provide common fixtures
3. Reset singletons between tests for isolation
"""

import os

import pytest

from lattice_lock.admin.auth.storage import MemoryAuthStorage
from lattice_lock.orchestrator.providers.base import ProviderAvailability


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all singletons before and after each test for isolation."""
    # Reset before test
    MemoryAuthStorage.clear()
    ProviderAvailability.reset()
    try:
        from lattice_lock.database import reset_database_state

        reset_database_state()
    except ImportError:
        pass

    yield

    # Reset after test (cleanup)
    MemoryAuthStorage.clear()
    ProviderAvailability.reset()


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



@pytest.fixture
def cassette():
    """Fixture for recording/replaying API interactions."""
    import responses

    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def openai_cassette(cassette):
    """Cassette pre-configured for OpenAI API."""
    import re

    # Allow/mock standard OpenAI endpoints
    cassette.add_passthru(re.compile(r"https://api\.openai\.com/.*"))
    return cassette


@pytest.fixture
def anthropic_cassette(cassette):
    """Cassette pre-configured for Anthropic API."""
    import re

    cassette.add_passthru(re.compile(r"https://api\.anthropic\.com/.*"))
    return cassette


@pytest.fixture
def google_cassette(cassette):
    """Cassette pre-configured for Google AI/Vertex API."""
    import re

    cassette.add_passthru(re.compile(r"https://generativelanguage\.googleapis\.com/.*"))
    return cassette
