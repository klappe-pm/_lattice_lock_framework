"""
Pytest configuration for Lattice Lock Framework tests.

This module configures pytest to:
1. Configure asyncio mode for async tests
2. Provide common fixtures
3. Ensure test isolation by resetting global state
"""

import os

import pytest


def _capture_global_state() -> dict:
    """Capture current global state for validation."""
    state = {}
    
    # Capture ProviderAvailability state
    try:
        from lattice_lock.orchestrator.api_clients import ProviderAvailability
        state["provider_checked"] = ProviderAvailability._checked
        state["provider_count"] = len(ProviderAvailability._status)
    except ImportError:
        pass
    
    # Capture BackgroundTaskQueue state
    try:
        from lattice_lock.utils.async_compat import BackgroundTaskQueue
        if BackgroundTaskQueue._instance is not None:
            state["background_tasks"] = BackgroundTaskQueue._instance.pending_count
        else:
            state["background_tasks"] = 0
    except ImportError:
        pass
    
    return state


def reset_all_globals() -> None:
    """Reset all global state for test isolation."""
    # Reset ProviderAvailability
    try:
        from lattice_lock.orchestrator.api_clients import ProviderAvailability
        ProviderAvailability.reset()
    except ImportError:
        pass
    
    # Reset BackgroundTaskQueue
    try:
        from lattice_lock.utils.async_compat import BackgroundTaskQueue
        BackgroundTaskQueue.reset()
    except ImportError:
        pass
    
    # Reset tracing metrics
    try:
        from lattice_lock.tracing import reset_performance_metrics
        reset_performance_metrics()
    except (ImportError, AttributeError):
        pass


@pytest.fixture(autouse=True)
def isolation():
    """Ensure test isolation by resetting global state before and after each test."""
    # Reset before test
    reset_all_globals()
    
    yield
    
    # Reset after test
    reset_all_globals()


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

