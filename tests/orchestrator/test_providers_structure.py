"""
Tests for Provider Architecture Structure
"""

import pytest

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError
from lattice_lock.orchestrator.providers import BaseAPIClient, ProviderAvailability, get_api_client
from lattice_lock.orchestrator.providers.anthropic import AnthropicAPIClient
from lattice_lock.orchestrator.providers.openai import OpenAIAPIClient


def test_imports():
    """Verify all providers can be imported."""

    assert BaseAPIClient
    assert ProviderAvailability


def test_factory_creation(monkeypatch):
    """Verify factory creates correct instances."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    config = AppConfig.load()

    client = get_api_client("openai", config=config)
    assert isinstance(client, OpenAIAPIClient)
    assert client.api_key == "test-key"

    client = get_api_client("anthropic", config=config)
    assert isinstance(client, AnthropicAPIClient)
    assert not client.use_dial

    client = get_api_client("claude", config=config)  # Alias
    assert isinstance(client, AnthropicAPIClient)


def test_factory_dial_creation(monkeypatch):
    """Verify factory creates DIAL client correctly."""
    monkeypatch.setenv("DIAL_API_KEY", "dial-key")
    monkeypatch.setenv("DIAL_URL", "http://dial")

    config = AppConfig.load()

    client = get_api_client("dial", config=config)
    assert isinstance(client, AnthropicAPIClient)
    assert client.use_dial
    assert client.api_key == "dial-key"


def test_validation_failure(monkeypatch):
    """Verify validation raises error when keys missing."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    config = AppConfig.load()

    with pytest.raises(ProviderUnavailableError) as exc:
        get_api_client("openai", config=config)
    assert "OPENAI_API_KEY" in str(exc.value)


def test_availability_singleton(monkeypatch):
    """Verify ProviderAvailability checks."""
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    ProviderAvailability.reset()  # Important!

    assert ProviderAvailability.is_available("openai")
    assert not ProviderAvailability.is_available("anthropic")

    available = ProviderAvailability.get_available_providers()
    assert "openai" in available
    assert "anthropic" not in available
