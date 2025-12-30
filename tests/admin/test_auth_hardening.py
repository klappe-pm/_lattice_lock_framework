from datetime import timedelta

import pytest

from lattice_lock.admin.auth import passwords, tokens
from lattice_lock.admin.auth.config import AuthConfig
from lattice_lock.admin.auth.models import Role
from lattice_lock.exceptions import SecurityConfigurationError


class TestAuthConfiguration:
    def test_dev_default_secret(self, monkeypatch):
        monkeypatch.setenv("LATTICE_ENV", "dev")
        monkeypatch.delenv("LATTICE_LOCK_SECRET_KEY", raising=False)
        config = AuthConfig.load()
        assert config.secret_key.get_secret_value() == "dev-secret-do-not-use-in-production"

    def test_production_missing_secret_raises_error(self, monkeypatch):
        monkeypatch.setenv("LATTICE_ENV", "production")
        monkeypatch.delenv("LATTICE_LOCK_SECRET_KEY", raising=False)
        with pytest.raises(SecurityConfigurationError):
            AuthConfig.load()

    def test_production_weak_secret_raises_error(self, monkeypatch):
        monkeypatch.setenv("LATTICE_ENV", "production")
        monkeypatch.setenv("LATTICE_LOCK_SECRET_KEY", "weak")
        with pytest.raises(SecurityConfigurationError):
            AuthConfig.load()

    def test_production_strong_secret_success(self, monkeypatch):
        monkeypatch.setenv("LATTICE_ENV", "production")
        strong_secret = "a" * 32
        monkeypatch.setenv("LATTICE_LOCK_SECRET_KEY", strong_secret)
        config = AuthConfig.load()
        assert config.secret_key.get_secret_value() == strong_secret


class TestTokenFunctions:
    @pytest.fixture
    def mock_config(self, monkeypatch):
        # Mock get_config to return a known config
        config = AuthConfig(secret_key="test-secret-key-must-be-long-enough", algorithm="HS256")
        monkeypatch.setattr("lattice_lock.admin.auth.tokens.get_config", lambda: config)
        return config

    def test_create_and_verify_token(self, mock_config):
        token = tokens.create_access_token("testuser", Role.ADMIN)
        decoded = tokens.verify_token(token)
        assert decoded is not None
        assert decoded.sub == "testuser"
        assert decoded.role == Role.ADMIN

    def test_token_expiry(self, mock_config):
        # Create token that expired 1 minute ago
        expires = timedelta(minutes=-1)
        token = tokens.create_access_token("testuser", Role.ADMIN, expires_delta=expires)
        with pytest.raises(Exception):  # verifies raise exception on invalid/expired
            tokens.verify_token(token)

    def test_invalid_signature(self, mock_config):
        token = tokens.create_access_token("testuser", Role.ADMIN)

        # Tamper with token
        header, payload, signature = token.split(".")
        # Simulating tampering by modifying signature
        tampered_sig = signature[:-1] + ("A" if signature[-1] != "A" else "B")
        tampered_token = f"{header}.{payload}.{tampered_sig}"

        with pytest.raises(Exception):
            tokens.verify_token(tampered_token)


class TestPasswords:
    def test_hash_and_verify(self):
        password = "securepassword"
        hashed = passwords.get_password_hash(password)
        assert hashed != password
        assert passwords.verify_password(password, hashed) is True
        assert passwords.verify_password("wrong", hashed) is False
