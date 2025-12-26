# Lattice Lock Framework - Master Refactoring Plan (v5.2 Final)

## Execution Order for Refactoring
### Execution Summary

| Chunk  | Focus                 | Risk         | Key Validation             |         |     |                           |
| ------ | --------------------- | ------------ | -------------------------- | ------- | --- | ------------------------- |
| 0      | Dependencies & Config | Low          | `pip check`, config load   |         |     |                           |
| 1      | Providers             | Low          | Import tests, no old paths |         |     |                           |
| 2      | Analysis & Scoring    | Low-Med      | Performance benchmark      |         |     |                           |
| 3      | Orchestrator          | **Med-High** | Token aggregation tests    |         |     |                           |
| 4      | Auth                  | Medium       | Security config tests      |         |     |                           |
| 5      | Error Handling        | Medium       | Background task lifecycle  |         |     |                           |
| 6      | Testing               |              |                            |         |     |                           |
| Medium | State isolation       |              | 7                          | Cleanup | Low | Full test suite, coverage |

**Critical Path:** `0 → 1 → 2 → 3 → 4 → 5 → 6 → 7`


## Work Chunk 0: Prerequisites, Dependencies & Config

**Objective:** Establish foundation with dependency safety, config injection, and custom exceptions.

**Risk Level:** Low

### Task 0.1: Update Dependencies with Safety Checks

Update `pyproject.toml`:

```toml
[project]
dependencies = [
    "PyYAML>=6.0,<7.0",      # Task Analysis patterns
    "PyJWT>=2.8.0,<3.0",     # Security-critical auth (replaces python-jose)
    "bcrypt>=4.0.0,<5.0",    # Password hashing
    "fastapi>=0.100.0",
    "pydantic>=2.0",
    # Remove python-jose entirely
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.1.0",
]
```

**Post-installation validation:**

```bash
pip install -e ".[dev]"
pip check
pip list --format=freeze > docs/dependency_snapshot.txt
```

### Task 0.2: Dependency Conflict Verification Script

Create `scripts/verify_deps.py`:

```python
"""Verify no conflicting dependencies before proceeding."""
import subprocess
import sys

def verify_dependencies():
    result = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ DEPENDENCY CONFLICT DETECTED:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    
    print("✅ All dependencies compatible")
    
    # Verify critical packages
    import importlib
    required = ["yaml", "jwt", "bcrypt"]
    for pkg in required:
        try:
            importlib.import_module(pkg)
            print(f"  ✓ {pkg} available")
        except ImportError:
            print(f"  ✗ {pkg} missing")
            sys.exit(1)

if __name__ == "__main__":
    verify_dependencies()
```

### Task 0.3: Create Custom Exception Classes

Create `src/lattice_lock/exceptions.py`:

```python
"""Framework-wide custom exceptions with clear failure boundaries."""

class LatticeError(Exception):
    """Base exception for Lattice Lock framework."""
    pass


class BillingIntegrityError(LatticeError):
    """
    Token aggregation or billing data corruption detected.
    
    This is a CRITICAL error - billing data integrity has been compromised.
    Requires immediate investigation.
    """
    pass


class SecurityConfigurationError(LatticeError):
    """
    Security requirements not met for current environment.
    
    Raised when production environment lacks required security configuration
    such as secret keys or secure algorithm settings.
    """
    pass


class BackgroundTaskError(LatticeError):
    """
    Background task failed to complete within timeout.
    
    Indicates potential data loss from incomplete async operations.
    """
    pass


class ProviderUnavailableError(LatticeError):
    """
    Provider credentials missing or provider unreachable.
    
    Attributes:
        provider: Name of the unavailable provider
        reason: Specific reason for unavailability
    """
    def __init__(self, provider: str, reason: str):
        self.provider = provider
        self.reason = reason
        super().__init__(f"Provider '{provider}' unavailable: {reason}")


class ValidationError(LatticeError):
    """Configuration or input validation failed."""
    pass
```

### Task 0.4: Central Configuration Loader

Create `src/lattice_lock/config/app_config.py`:

```python
"""Central Application Configuration with validation."""
import os
import re
import logging
from typing import Optional

from ..exceptions import SecurityConfigurationError, ValidationError

logger = logging.getLogger(__name__)


class AppConfig:
    """
    Root configuration object with environment validation.
    
    All configuration values are validated on initialization.
    Production environment enforces strict security requirements.
    """
    
    def __init__(self):
        self.env = os.environ.get("LATTICE_ENV", "dev")
        
        # Security Configuration
        self.secret_key: Optional[str] = os.environ.get("LATTICE_LOCK_SECRET_KEY")
        self.jwt_algorithm: str = "HS256"
        
        # Analyzer Configuration
        self.analyzer_cache_size: int = self._parse_int("ANALYZER_CACHE_SIZE", 1024)
        
        # Executor Configuration
        self.max_function_calls: int = self._parse_int("MAX_FUNCTION_CALLS", 10)
        self.background_task_timeout: float = float(
            os.environ.get("BACKGROUND_TASK_TIMEOUT", "5.0")
        )
        
        # Auth Configuration
        self.token_expiry_minutes: int = self._parse_int("TOKEN_EXPIRY_MINUTES", 30)
        
        # Validate after all values loaded
        self._validate_environment()
    
    def _validate_environment(self) -> None:
        """Validate configuration for current environment."""
        if self.env == "production":
            if not self.secret_key:
                raise SecurityConfigurationError(
                    "LATTICE_LOCK_SECRET_KEY must be set in production environment"
                )
            if len(self.secret_key) < 32:
                raise SecurityConfigurationError(
                    "LATTICE_LOCK_SECRET_KEY must be at least 32 characters in production"
                )
            logger.info("Production security configuration validated")
        else:
            if not self.secret_key:
                self.secret_key = "dev-secret-do-not-use-in-production"
                logger.warning("Using default dev secret key - NOT FOR PRODUCTION")
    
    def _parse_int(self, var: str, default: int) -> int:
        """Safely parse integer environment variables."""
        value = os.environ.get(var)
        if value is not None:
            if re.match(r"^\d+$", value):
                return int(value)
            else:
                raise ValidationError(f"Environment variable {var} must be an integer, got: {value}")
        return default
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load and validate configuration."""
        return cls()


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig.load()
    return _config


def reset_config() -> None:
    """Reset configuration for testing."""
    global _config
    _config = None
```

Create `src/lattice_lock/config/__init__.py`:

```python
from .app_config import AppConfig, get_config, reset_config

__all__ = ["AppConfig", "get_config", "reset_config"]
```

### Task 0.5: Logging Standards

Create `src/lattice_lock/utils/logging.py`:

```python
"""Logging configuration and standards for Lattice Lock."""
import logging
import re
from typing import Any

# Standard log levels by event type
LOG_LEVELS = {
    # Debug level - internal operations
    "cache_hit": logging.DEBUG,
    "cache_miss": logging.DEBUG,
    "internal_state": logging.DEBUG,
    
    # Info level - normal operations
    "model_selection": logging.INFO,
    "request_complete": logging.INFO,
    "provider_initialized": logging.INFO,
    
    # Warning level - recoverable issues
    "provider_failover": logging.WARNING,
    "retry_attempt": logging.WARNING,
    "deprecation": logging.WARNING,
    
    # Error level - failures
    "validation_failure": logging.ERROR,
    "provider_error": logging.ERROR,
    
    # Critical level - immediate attention required
    "security_violation": logging.CRITICAL,
    "billing_integrity": logging.CRITICAL,
    "data_corruption": logging.CRITICAL,
}

# Patterns to redact from logs
REDACT_PATTERNS = [
    re.compile(r"(api[_-]?key[\"']?\s*[:=]\s*[\"']?)([^\"'\s,}]+)", re.I),
    re.compile(r"(secret[_-]?key[\"']?\s*[:=]\s*[\"']?)([^\"'\s,}]+)", re.I),
    re.compile(r"(password[\"']?\s*[:=]\s*[\"']?)([^\"'\s,}]+)", re.I),
    re.compile(r"(bearer\s+)([^\s,}]+)", re.I),
    re.compile(r"(token[\"']?\s*[:=]\s*[\"']?)([^\"'\s,}]+)", re.I),
]


def redact_sensitive(message: str) -> str:
    """Redact sensitive data from log messages."""
    result = message
    for pattern in REDACT_PATTERNS:
        result = pattern.sub(r"\1[REDACTED]", result)
    return result


class RedactingFormatter(logging.Formatter):
    """Formatter that automatically redacts sensitive data."""
    
    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return redact_sensitive(original)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure logging with redaction for the framework."""
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    
    root_logger = logging.getLogger("lattice_lock")
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with standard configuration.
    
    Usage:
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
```

### Task 0.6: Document Reset Method Requirements

Create `docs/testing/reset_methods.md`:

````markdown
# Reset Methods for Test Isolation

All stateful components MUST implement reset functionality to ensure test isolation.

## Required Reset Methods

| Component | Reset Method | Location | Purpose |
|-----------|--------------|----------|---------|
| `AppConfig` | `reset_config()` | `config/app_config.py` | Clear cached config |
| `ProviderAvailability` | `.reset()` | `providers/base.py` | Clear provider status cache |
| `ErrorMetrics` | `reset_metrics()` | `errors/middleware.py` | Clear error counters |
| `PerformanceMetrics` | `reset_performance_metrics()` | `tracing.py` | Clear timing data |
| `InMemoryAuthStorage` | `.clear_all()` | `auth/storage.py` | Clear users/tokens/keys |
| `BackgroundTaskQueue` | Reinitialize via global | `utils/async_compat.py` | Clear pending tasks |
| `ClientPool` | `.close_all()` | `execution/client_pool.py` | Close all connections |
| `TaskAnalyzer` | `.reset_cache()` | `analysis/analyzer.py` | Clear analysis cache |

## Implementation Pattern

```python
class MyStatefulComponent:
    _instance = None  # If singleton
    
    def __init__(self):
        self._state = {}
    
    def reset(self) -> None:
        """Reset all state for testing."""
        self._state.clear()
    
    @classmethod
    def reset_singleton(cls) -> None:
        """Reset singleton instance for testing."""
        cls._instance = None
````

## Conftest Integration

All reset methods are called automatically via the `reset_global_state` fixture in `tests/conftest.py`.

````

### Task 0.7: Rollback Criteria Template

Create `docs/refactoring/rollback_criteria.md`:

```markdown
# Rollback Criteria for Refactoring Chunks

Each work chunk must define explicit rollback criteria. If ANY criteria is met,
immediately revert the chunk and investigate.

## Template

For each chunk, document:

````

## Chunk N Rollback Criteria

REVERT IF ANY OF THE FOLLOWING OCCUR:

1. [ ] Test suite pass rate drops below 95%
2. [ ] Any CRITICAL-level log messages in production
3. [ ] Token aggregation tests fail
4. [ ] Security configuration tests fail
5. [ ] Performance regression >20% on benchmarks
6. [ ] [Chunk-specific criteria]

ROLLBACK PROCEDURE:

1. git revert <commit-hash>
2. Deploy previous version
3. Notify team in #lattice-alerts
4. Create incident ticket

```

## Chunk-Specific Criteria

### Chunk 3 (Orchestrator)
- Any `BillingIntegrityError` exceptions in logs
- Token counts in responses don't match expected aggregation
- Cost tracking shows anomalies vs baseline

### Chunk 4 (Auth)
- Any `SecurityConfigurationError` in production
- JWT validation failures spike
- Authentication success rate drops below 99%
```

### Chunk 0 Validation Gate

```bash
# Run before marking Chunk 0 complete
python scripts/verify_deps.py
pytest tests/config/ -v
python -c "from lattice_lock.config import get_config; get_config()"
python -c "from lattice_lock.exceptions import BillingIntegrityError; print('✅ Exceptions available')"
```

**Rollback Criteria for Chunk 0:**

- [ ] `pip check` fails
- [ ] Any import errors for new modules
- [ ] Config validation raises unexpected exceptions

---

## Work Chunk 1: Provider Architecture Unification

**Objective:** Split `api_clients.py` into modular providers with validation.

**Risk Level:** Low

### Task 1.1: Create Package Structure

Create directory structure:

```
src/lattice_lock/orchestrator/providers/
├── __init__.py
├── base.py
├── factory.py
├── openai.py
├── anthropic.py
├── google.py
├── xai.py
├── azure.py
├── bedrock.py
├── local.py
└── dial.py
```

### Task 1.2: Implement Base Provider with Validation

Create `src/lattice_lock/orchestrator/providers/base.py`:

```python
"""Base classes for all API providers."""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider availability status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"
    ERROR = "error"


class ProviderAvailability:
    """
    Singleton for tracking provider credential availability.
    
    Checks environment for required API keys and tracks provider status.
    """
    _instance: Optional["ProviderAvailability"] = None
    _status: dict[str, ProviderStatus] = {}
    _messages: dict[str, str] = {}
    
    REQUIRED_CREDENTIALS: dict[str, list[str]] = {
        "openai": ["OPENAI_API_KEY"],
        "anthropic": ["ANTHROPIC_API_KEY"],
        "google": ["GOOGLE_API_KEY"],
        "xai": ["XAI_API_KEY"],
        "azure": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"],
        "bedrock": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
        "local": [],  # No credentials required
    }
    
    @classmethod
    def reset(cls) -> None:
        """Reset singleton state for testing."""
        cls._instance = None
        cls._status.clear()
        cls._messages.clear()
    
    @classmethod
    def is_available(cls, provider: str) -> bool:
        """Check if provider has required credentials."""
        import os
        required = cls.REQUIRED_CREDENTIALS.get(provider.lower(), [])
        return all(os.environ.get(key) for key in required)
    
    @classmethod
    def get_status(cls, provider: str) -> ProviderStatus:
        """Get cached status for provider."""
        return cls._status.get(provider.lower(), ProviderStatus.UNKNOWN)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of providers with configured credentials."""
        return [p for p in cls.REQUIRED_CREDENTIALS if cls.is_available(p)]


class BaseAPIClient(ABC):
    """
    Abstract base class for all API provider clients.
    
    All providers must:
    1. Validate configuration on initialization
    2. Implement health_check for connectivity verification
    3. Implement chat_completion for LLM calls
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize client with configuration.
        
        Args:
            config: Application configuration object
            
        Raises:
            ProviderUnavailableError: If required credentials missing
        """
        self.config = config
        self._validate_config()
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def _validate_config(self) -> None:
        """
        Provider-specific configuration validation.
        
        Must check for required API keys and raise ProviderUnavailableError
        if any are missing.
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify provider connectivity and credential validity.
        
        Implementation Requirements:
        - Verify API credentials are valid (not just present)
        - Confirm provider endpoint is reachable
        - Execute minimal API call (e.g., list models)
        - Cache results for max 60 seconds
        - Must not consume significant billable quota
        
        Returns:
            True if provider is healthy and accessible
            
        Raises:
            ProviderUnavailableError: If health check fails
        """
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        **kwargs
    ) -> Any:
        """
        Execute a chat completion request.
        
        Args:
            model: Model identifier
            messages: Conversation messages
            **kwargs: Provider-specific options
            
        Returns:
            APIResponse with completion result
        """
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources."""
        pass
```

### Task 1.3: Implement Provider Files

For each provider file (example `openai.py`):

```python
"""OpenAI API provider implementation."""
import logging
import os
from typing import Any

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class OpenAIAPIClient(BaseAPIClient):
    """OpenAI API client implementation."""
    
    PROVIDER_NAME = "openai"
    
    def __init__(self, config: AppConfig, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        super().__init__(config)
    
    def _validate_config(self) -> None:
        """Validate OpenAI API key is present."""
        if not self.api_key:
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                reason="OPENAI_API_KEY environment variable not set"
            )
    
    async def health_check(self) -> bool:
        """Verify OpenAI API connectivity."""
        try:
            # Minimal API call to verify credentials
            # Implementation: call models.list() endpoint
            logger.debug("OpenAI health check passed")
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            raise ProviderUnavailableError(
                provider=self.PROVIDER_NAME,
                reason=str(e)
            )
    
    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        **kwargs
    ) -> Any:
        """Execute OpenAI chat completion."""
        # Implementation details...
        pass
```

### Task 1.4: Create Factory

Create `src/lattice_lock/orchestrator/providers/factory.py`:

```python
"""Provider factory for creating API clients."""
import logging
from typing import Type

from lattice_lock.config import AppConfig, get_config

from .base import BaseAPIClient, ProviderAvailability
from .openai import OpenAIAPIClient
from .anthropic import AnthropicAPIClient
from .google import GoogleAPIClient
from .xai import XAIAPIClient
from .azure import AzureOpenAIClient
from .bedrock import BedrockAPIClient
from .local import LocalModelClient
from .dial import DIALClient

logger = logging.getLogger(__name__)

# Provider name to client class mapping
PROVIDER_CLIENTS: dict[str, Type[BaseAPIClient]] = {
    "openai": OpenAIAPIClient,
    "anthropic": AnthropicAPIClient,
    "google": GoogleAPIClient,
    "xai": XAIAPIClient,
    "azure": AzureOpenAIClient,
    "bedrock": BedrockAPIClient,
    "local": LocalModelClient,
    "dial": DIALClient,
}

# Aliases for common names
PROVIDER_ALIASES: dict[str, str] = {
    "grok": "xai",
    "gemini": "google",
    "claude": "anthropic",
    "ollama": "local",
}


def get_api_client(
    provider: str,
    check_availability: bool = True,
    config: AppConfig | None = None,
    **kwargs
) -> BaseAPIClient:
    """
    Factory function to get the appropriate API client.
    
    Args:
        provider: Provider name (e.g., 'openai', 'anthropic')
        check_availability: Whether to check credentials before creating
        config: Optional config override (uses global if not provided)
        **kwargs: Additional arguments for client initialization
        
    Returns:
        Configured API client instance
        
    Raises:
        ValueError: If provider is unknown
        ProviderUnavailableError: If credentials missing and check_availability=True
    """
    config = config or get_config()
    
    # Resolve aliases
    provider_lower = provider.lower()
    provider_lower = PROVIDER_ALIASES.get(provider_lower, provider_lower)
    
    if provider_lower not in PROVIDER_CLIENTS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDER_CLIENTS.keys())}")
    
    if check_availability and not ProviderAvailability.is_available(provider_lower):
        from lattice_lock.exceptions import ProviderUnavailableError
        raise ProviderUnavailableError(
            provider=provider_lower,
            reason="Required credentials not configured"
        )
    
    client_class = PROVIDER_CLIENTS[provider_lower]
    logger.info(f"Creating {client_class.__name__} for provider '{provider}'")
    
    return client_class(config=config, **kwargs)
```

### Task 1.5: Update Package Exports

Create `src/lattice_lock/orchestrator/providers/__init__.py`:

```python
"""
Lattice Lock Provider Package

API clients for all supported model providers.
"""
from .base import (
    BaseAPIClient,
    ProviderAvailability,
    ProviderStatus,
)
from .factory import get_api_client, PROVIDER_CLIENTS, PROVIDER_ALIASES
from .openai import OpenAIAPIClient
from .anthropic import AnthropicAPIClient
from .google import GoogleAPIClient
from .xai import XAIAPIClient
from .azure import AzureOpenAIClient
from .bedrock import BedrockAPIClient
from .local import LocalModelClient
from .dial import DIALClient

__all__ = [
    # Base classes
    "BaseAPIClient",
    "ProviderAvailability",
    "ProviderStatus",
    # Factory
    "get_api_client",
    "PROVIDER_CLIENTS",
    "PROVIDER_ALIASES",
    # Concrete providers
    "OpenAIAPIClient",
    "AnthropicAPIClient",
    "GoogleAPIClient",
    "XAIAPIClient",
    "AzureOpenAIClient",
    "BedrockAPIClient",
    "LocalModelClient",
    "DIALClient",
]
```

### Task 1.6: Update All Internal Imports

Search and replace throughout codebase:

```bash
# Find all files importing from old location
grep -r "from lattice_lock.orchestrator.api_clients import" src/
grep -r "from .api_clients import" src/

# Update each file to use new import path
# Old: from lattice_lock.orchestrator.api_clients import ...
# New: from lattice_lock.orchestrator.providers import ...
```

### Task 1.7: Delete Old Module

```bash
rm src/lattice_lock/orchestrator/api_clients.py
```

### Task 1.8: Create Validation Tests

Create `tests/providers/test_provider_validation.py`:

```python
"""Provider validation tests."""
import pytest
from unittest.mock import patch

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError
from lattice_lock.orchestrator.providers import (
    OpenAIAPIClient,
    ProviderAvailability,
    get_api_client,
)


class TestProviderInitialization:
    """Test provider initialization validates config."""
    
    def test_openai_requires_api_key(self):
        """OpenAI client must validate API key on init."""
        with patch.dict("os.environ", {}, clear=True):
            config = AppConfig()
            with pytest.raises(ProviderUnavailableError) as exc:
                OpenAIAPIClient(config)
            assert "OPENAI_API_KEY" in str(exc.value)
    
    def test_factory_checks_availability(self):
        """Factory should check credentials by default."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ProviderUnavailableError):
                get_api_client("openai")
    
    def test_factory_skip_availability_check(self):
        """Factory can skip availability check when requested."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            client = get_api_client("openai", check_availability=False)
            assert client is not None


class TestProviderAvailability:
    """Test provider availability tracking."""
    
    def setup_method(self):
        ProviderAvailability.reset()
    
    def test_reset_clears_state(self):
        """Reset should clear all cached status."""
        ProviderAvailability._status["test"] = "value"
        ProviderAvailability.reset()
        assert len(ProviderAvailability._status) == 0
    
    def test_available_providers_list(self):
        """Should return only providers with credentials."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}, clear=True):
            available = ProviderAvailability.get_available_providers()
            assert "openai" in available
            assert "anthropic" not in available
```

### Chunk 1 Validation Gate

```bash
pytest tests/providers/ -v
python -c "from lattice_lock.orchestrator.providers import get_api_client; print('✅ Provider imports work')"
grep -r "from.*api_clients import" src/ && echo "❌ Old imports found" || echo "✅ No old imports"
```

**Rollback Criteria for Chunk 1:**

- [ ] Any `from .api_clients import` statements remain in codebase
- [ ] Provider initialization tests fail
- [ ] Import errors from providers package

---

## Work Chunk 2: Task Analysis & Scoring

**Objective:** Externalize patterns, optimize regex, and migrate both `TaskAnalyzer` and `ModelScorer`.

**Risk Level:** Low-Medium

### Task 2.1: Create Analysis Package Structure

```
src/lattice_lock/orchestrator/analysis/
├── __init__.py
├── analyzer.py
├── patterns.yaml
├── semantic_router.py
└── types.py

src/lattice_lock/orchestrator/scoring/
├── __init__.py
├── model_scorer.py
└── scorer_config.yaml
```

### Task 2.2: Create Pattern Configuration

Create `src/lattice_lock/orchestrator/analysis/patterns.yaml`:

```yaml
# Task Analysis Patterns
# Pre-compiled at load time for performance

version: "1.0"

task_patterns:
  CODE_GENERATION:
    - ["\\bwrite\\s+code\\b", 1.0]
    - ["\\bimplement\\b", 0.9]
    - ["\\bcreate\\s+function\\b", 0.95]
    - ["\\bdef\\s+\\w+\\s*\\(", 0.8]
    - ["\\bclass\\s+\\w+", 0.8]
    
  DEBUGGING:
    - ["\\bdebug\\b", 0.9]
    - ["\\bfix\\s+(?:this|the)?\\s*(?:bug|error|issue)", 0.95]
    - ["\\btraceback\\b", 0.85]
    - ["\\bexception\\b", 0.7]
    - ["TypeError|ValueError|KeyError", 0.8]
    
  REASONING:
    - ["\\bexplain\\s+(?:why|how)", 0.85]
    - ["\\banalyze\\b", 0.8]
    - ["\\bcompare\\b", 0.7]
    - ["\\bwhat\\s+(?:is|are)\\s+the\\s+(?:difference|pros|cons)", 0.9]
    
  DATA_ANALYSIS:
    - ["\\bpd\\.", 0.9]
    - ["\\bdf\\[", 0.85]
    - ["\\.csv\\b", 0.7]
    - ["\\b(?:analyze|visualize)\\s+(?:the\\s+)?data", 0.9]
    
  GENERAL:
    - [".*", 0.1]  # Fallback pattern
```

### Task 2.3: Create Analysis Types

Create `src/lattice_lock/orchestrator/analysis/types.py`:

```python
"""Task analysis type definitions."""
from dataclasses import dataclass, field
from typing import Any

from ..types import TaskType


@dataclass
class TaskAnalysis:
    """
    Comprehensive task analysis result.
    
    Attributes:
        primary_type: Most likely task type
        confidence: Confidence score (0.0-1.0)
        secondary_types: Additional relevant types
        scores: Raw scores for each task type
        features: Extracted prompt features
    """
    primary_type: TaskType
    confidence: float
    secondary_types: list[TaskType] = field(default_factory=list)
    scores: dict[TaskType, float] = field(default_factory=dict)
    features: dict[str, Any] = field(default_factory=dict)
```

### Task 2.4: Create Optimized Analyzer

Create `src/lattice_lock/orchestrator/analysis/analyzer.py`:

```python
"""
Task Analyzer with pre-compiled regex patterns.

Patterns are loaded from YAML and compiled once at initialization
for optimal performance.
"""
import hashlib
import logging
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

from lattice_lock.config import AppConfig

from ..types import TaskType, TaskRequirements
from .types import TaskAnalysis

logger = logging.getLogger(__name__)


def _load_yaml_safe():
    """Load PyYAML with helpful error if missing."""
    try:
        import yaml
        return yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for TaskAnalyzer. "
            "Install with: pip install 'PyYAML>=6.0'"
        )


class TaskAnalyzer:
    """
    Analyzes prompts to determine task type using pre-compiled patterns.
    
    Patterns are loaded from YAML and compiled once at initialization.
    Results are cached using LRU strategy.
    """
    
    def __init__(
        self,
        config: AppConfig,
        patterns_path: Path | None = None,
    ):
        """
        Initialize analyzer with configuration.
        
        Args:
            config: Application configuration
            patterns_path: Optional custom patterns file path
        """
        self.config = config
        self._patterns_path = patterns_path or Path(__file__).parent / "patterns.yaml"
        
        # Load and pre-compile patterns
        self._compiled_patterns = self._load_and_compile(self._patterns_path)
        
        # LRU cache for analysis results
        self._cache: OrderedDict[str, TaskAnalysis] = OrderedDict()
        self._cache_size = config.analyzer_cache_size
        
        logger.info(f"TaskAnalyzer initialized with {len(self._compiled_patterns)} task types")
    
    def _load_and_compile(self, path: Path) -> dict[str, list[tuple[re.Pattern, float]]]:
        """
        Load patterns from YAML and PRE-COMPILE all regex.
        
        This is the key performance optimization - patterns are compiled
        once at startup rather than on every analysis.
        """
        yaml = _load_yaml_safe()
        
        with open(path) as f:
            raw = yaml.safe_load(f)
        
        compiled = {}
        pattern_count = 0
        
        for task_type, patterns in raw.get("task_patterns", {}).items():
            compiled[task_type] = []
            for pattern_str, weight in patterns:
                try:
                    compiled_pattern = re.compile(pattern_str, re.IGNORECASE)
                    compiled[task_type].append((compiled_pattern, weight))
                    pattern_count += 1
                except re.error as e:
                    logger.warning(f"Invalid regex pattern '{pattern_str}': {e}")
        
        logger.debug(f"Compiled {pattern_count} regex patterns")
        return compiled
    
    def analyze(self, prompt: str) -> TaskRequirements:
        """
        Analyze prompt and return task requirements.
        
        Uses cached results when available.
        """
        analysis = self._analyze_with_cache(prompt)
        return TaskRequirements(
            task_type=analysis.primary_type,
            # Map other fields as needed
        )
    
    def analyze_full(self, prompt: str) -> TaskAnalysis:
        """Return full analysis with all scores."""
        return self._analyze_with_cache(prompt)
    
    def _analyze_with_cache(self, prompt: str) -> TaskAnalysis:
        """Check cache or perform analysis."""
        cache_key = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        
        if cache_key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(cache_key)
            logger.debug(f"Cache hit for prompt hash {cache_key}")
            return self._cache[cache_key]
        
        # Perform analysis
        analysis = self._perform_analysis(prompt)
        
        # Add to cache with LRU eviction
        self._cache[cache_key] = analysis
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)
        
        return analysis
    
    def _perform_analysis(self, prompt: str) -> TaskAnalysis:
        """Execute pattern matching against prompt."""
        scores: dict[str, float] = {}
        
        for task_type, patterns in self._compiled_patterns.items():
            score = 0.0
            for pattern, weight in patterns:
                if pattern.search(prompt):
                    score = max(score, weight)
            scores[task_type] = score
        
        # Find best match
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_scores[0][0] if sorted_scores else "GENERAL"
        confidence = sorted_scores[0][1] if sorted_scores else 0.0
        
        return TaskAnalysis(
            primary_type=TaskType[primary],
            confidence=confidence,
            scores={TaskType[k]: v for k, v in scores.items()},
        )
    
    def reset_cache(self) -> None:
        """Clear analysis cache for testing."""
        self._cache.clear()
        logger.debug("TaskAnalyzer cache cleared")
```

### Task 2.5: Create Semantic Router

Create `src/lattice_lock/orchestrator/analysis/semantic_router.py`:

```python
"""
Semantic Router for LLM-based task classification.

Used as fallback when pattern matching confidence is low.
"""
import logging
from typing import Any, Protocol

from ..types import TaskType

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Protocol for LLM clients used by SemanticRouter."""
    
    async def chat_completion(
        self, model: str, messages: list[dict], max_tokens: int, temperature: float
    ) -> Any:
        ...


class SemanticRouter:
    """
    LLM-based task classification for uncertain cases.
    
    Args:
        client: LLM client implementing chat_completion
        model: Model to use for classification
        confidence_threshold: Min pattern confidence to skip LLM routing
    """
    
    CLASSIFICATION_PROMPT = """Classify this prompt into one task type:
{types}

Prompt: {prompt}

Return ONLY the task type name, nothing else."""
    
    def __init__(
        self,
        client: LLMClient | None = None,
        model: str = "gpt-4o-mini",
        confidence_threshold: float = 0.5,
    ):
        self.client = client
        self.model = model
        self.confidence_threshold = confidence_threshold
    
    async def route(self, prompt: str) -> TaskType:
        """Route prompt to task type using LLM."""
        if not self.client:
            logger.debug("No LLM client configured, returning GENERAL")
            return TaskType.GENERAL
        
        types_str = ", ".join(t.name for t in TaskType)
        classification_prompt = self.CLASSIFICATION_PROMPT.format(
            types=types_str,
            prompt=prompt[:1000]  # Truncate long prompts
        )
        
        try:
            response = await self.client.chat_completion(
                model=self.model,
                messages=[{"role": "user", "content": classification_prompt}],
                max_tokens=20,
                temperature=0.0,
            )
            
            result = response.content.strip().upper()
            for task_type in TaskType:
                if task_type.name in result:
                    return task_type
            
            return TaskType.GENERAL
            
        except Exception as e:
            logger.warning(f"Semantic routing failed: {e}")
            return TaskType.GENERAL
    
    def should_route(self, pattern_confidence: float) -> bool:
        """Determine if LLM routing needed based on pattern confidence."""
        return pattern_confidence < self.confidence_threshold
```

### Task 2.6: Migrate ModelScorer

Create `src/lattice_lock/orchestrator/scoring/model_scorer.py`:

```python
"""
Model Scorer for ranking models by capability match.

Scores models based on their capabilities against task requirements.
"""
import logging
from pathlib import Path
from typing import Any

from lattice_lock.config import AppConfig

from ..types import ModelCapabilities, TaskRequirements, TaskType
from ..analysis.types import TaskAnalysis

logger = logging.getLogger(__name__)


def _load_yaml_safe():
    """Load PyYAML with helpful error if missing."""
    try:
        import yaml
        return yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for ModelScorer. "
            "Install with: pip install 'PyYAML>=6.0'"
        )


class ModelScorer:
    """
    Scores models based on capability match to task requirements.
    
    Uses configurable weights loaded from YAML.
    """
    
    DEFAULT_WEIGHTS = {
        "context_window": 0.2,
        "speed": 0.15,
        "cost": 0.15,
        "capability_match": 0.5,
    }
    
    def __init__(
        self,
        config: AppConfig,
        weights_path: Path | None = None,
    ):
        """
        Initialize scorer with configuration.
        
        Args:
            config: Application configuration
            weights_path: Optional custom weights file
        """
        self.config = config
        self._weights = self._load_weights(weights_path)
        logger.info("ModelScorer initialized")
    
    def _load_weights(self, path: Path | None) -> dict[str, float]:
        """Load scoring weights from configuration."""
        if path is None:
            return self.DEFAULT_WEIGHTS.copy()
        
        yaml = _load_yaml_safe()
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            return data.get("weights", self.DEFAULT_WEIGHTS)
        except Exception as e:
            logger.warning(f"Failed to load weights from {path}: {e}")
            return self.DEFAULT_WEIGHTS.copy()
    
    def score(
        self,
        model: ModelCapabilities,
        requirements: TaskRequirements,
    ) -> float:
        """
        Calculate fitness score for model given requirements.
        
        Args:
            model: Model capability information
            requirements: Task requirements to match
            
        Returns:
            Score from 0.0 (poor match) to 1.0 (perfect match)
        """
        scores = {
            "context_window": self._score_context(model, requirements),
            "speed": self._score_speed(model, requirements),
            "cost": self._score_cost(model, requirements),
            "capability_match": self._score_capabilities(model, requirements),
        }
        
        total = sum(
            scores[k] * self._weights[k]
            for k in scores
        )
        
        logger.debug(f"Model {model.name} scored {total:.3f} for {requirements.task_type}")
        return total
    
    def _score_context(self, model: ModelCapabilities, req: TaskRequirements) -> float:
        """Score based on context window adequacy."""
        if model.context_window >= req.min_context_window:
            return 1.0
        return model.context_window / req.min_context_window
    
    def _score_speed(self, model: ModelCapabilities, req: TaskRequirements) -> float:
        """Score based on latency requirements."""
        # Implementation based on model benchmarks
        return 0.8  # Placeholder
    
    def _score_cost(self, model: ModelCapabilities, req: TaskRequirements) -> float:
        """Score based on cost efficiency."""
        # Implementation based on pricing data
        return 0.7  # Placeholder
    
    def _score_capabilities(self, model: ModelCapabilities, req: TaskRequirements) -> float:
        """Score based on capability match to task type."""
        task_capabilities = {
            TaskType.CODE_GENERATION: ["code", "programming"],
            TaskType.REASONING: ["reasoning", "analysis"],
            TaskType.CREATIVE_WRITING: ["creative", "writing"],
            # ... other task types
        }
        
        required = set(task_capabilities.get(req.task_type, []))
        model_caps = set(model.capabilities)
        
        if not required:
            return 0.5
        
        overlap = len(required & model_caps)
        return overlap / len(required)
```

### Task 2.7: Create Package Exports

Create `src/lattice_lock/orchestrator/analysis/__init__.py`:

```python
from .analyzer import TaskAnalyzer
from .semantic_router import SemanticRouter
from .types import TaskAnalysis

__all__ = ["TaskAnalyzer", "TaskAnalysis", "SemanticRouter"]
```

Create `src/lattice_lock/orchestrator/scoring/__init__.py`:

```python
from .model_scorer import ModelScorer

__all__ = ["ModelScorer"]
```

### Task 2.8: Delete Old Module

```bash
rm src/lattice_lock/orchestrator/scorer.py
rm src/lattice_lock/orchestrator/routing/analyzer.py
```

### Task 2.9: Update Internal Imports

```bash
# Find and update all imports
grep -r "from.*scorer import" src/
grep -r "from.*routing.analyzer import" src/

# Update to new paths
# Old: from lattice_lock.orchestrator.scorer import TaskAnalyzer, ModelScorer
# New: from lattice_lock.orchestrator.analysis import TaskAnalyzer
#      from lattice_lock.orchestrator.scoring import ModelScorer
```

### Task 2.10: Create Performance Validation Test

Create `tests/analysis/test_performance.py`:

```python
"""Performance validation for TaskAnalyzer."""
import time
import pytest

from lattice_lock.config import AppConfig
from lattice_lock.orchestrator.analysis import TaskAnalyzer


class TestAnalyzerPerformance:
    """Validate regex pre-compilation performance."""
    
    @pytest.fixture
    def analyzer(self):
        config = AppConfig()
        return TaskAnalyzer(config)
    
    def test_regex_precompilation_performance(self, analyzer):
        """
        Pre-compiled regex must analyze 1000 prompts in under 100ms.
        
        This validates the performance improvement from pre-compilation.
        """
        prompts = [
            "Write a Python function to sort a list",
            "Debug this error: TypeError in line 42",
            "Explain how neural networks work",
            "Analyze the sales data and create a visualization",
        ] * 250  # 1000 prompts
        
        start = time.perf_counter()
        for prompt in prompts:
            analyzer.analyze(prompt)
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.1, f"Analysis took {elapsed:.3f}s, expected < 0.1s"
    
    def test_cache_improves_repeat_performance(self, analyzer):
        """Cached lookups should be significantly faster."""
        prompt = "Write a function to calculate fibonacci numbers"
        
        # First call (cache miss)
        start = time.perf_counter()
        analyzer.analyze(prompt)
        first_call = time.perf_counter() - start
        
        # Second call (cache hit)
        start = time.perf_counter()
        analyzer.analyze(prompt)
        second_call = time.perf_counter() - start
        
        # Cache hit should be at least 10x faster
        assert second_call < first_call / 10
```

### Chunk 2 Validation Gate

```bash
pytest tests/analysis/ -v
pytest tests/scoring/ -v
python -c "from lattice_lock.orchestrator.analysis import TaskAnalyzer; print('✅ Analysis imports work')"
python -c "from lattice_lock.orchestrator.scoring import ModelScorer; print('✅ Scoring imports work')"
grep -r "from.*scorer import" src/ && echo "❌ Old imports found" || echo "✅ No old imports"
```

**Rollback Criteria for Chunk 2:**

- [ ] Performance test fails (>100ms for 1000 prompts)
- [ ] Pattern YAML fails to load
- [ ] Any old imports remain in codebase

---

## Work Chunk 3: Model Orchestrator Decomposition

**Objective:** Extract ModelSelector and ConversationExecutor with billing-critical token aggregation.

**Risk Level:** Medium-High (billing integrity critical)

⚠️ **CRITICAL:** This chunk contains billing-critical logic. Implement tests BEFORE refactoring code. Require second engineer review for token aggregation implementation.

### Task 3.1: Create Selection Package

Create `src/lattice_lock/orchestrator/selection/__init__.py` and `model_selector.py`:

```python
"""Model selection logic."""
from .model_selector import ModelSelector

__all__ = ["ModelSelector"]
```

Create `src/lattice_lock/orchestrator/selection/model_selector.py`:

```python
"""
Model Selection extracted from ModelOrchestrator.

Handles model ranking and fallback chain generation.
"""
import logging
from typing import Optional

from lattice_lock.config import AppConfig

from ..analysis import TaskAnalyzer
from ..scoring import ModelScorer
from ..registry import ModelRegistry
from ..guide import ModelGuideParser
from ..types import TaskRequirements

logger = logging.getLogger(__name__)


class ModelSelector:
    """
    Selects optimal model based on task requirements and scoring.
    
    Uses multi-stage selection:
    1. Check guide recommendations
    2. Filter by hard constraints
    3. Score remaining candidates
    4. Return highest-scoring model
    """
    
    def __init__(
        self,
        registry: ModelRegistry,
        scorer: ModelScorer,
        guide: ModelGuideParser | None = None,
        config: AppConfig | None = None,
    ):
        self.registry = registry
        self.scorer = scorer
        self.guide = guide
        self.config = config
    
    def select_best_model(self, requirements: TaskRequirements) -> str | None:
        """
        Select highest-scoring model for requirements.
        
        Args:
            requirements: Task requirements to match
            
        Returns:
            Model ID string, or None if no suitable model
        """
        # Check guide recommendations first
        if self.guide:
            recommended = self.guide.get_recommended_models(requirements.task_type.name)
            if recommended:
                valid = self._validate_recommendations(recommended, requirements)
                if valid:
                    logger.info(f"Using guide recommendation: {valid[0]}")
                    return valid[0]
        
        # Score all candidates
        candidates = self._score_candidates(requirements)
        
        if not candidates:
            logger.warning(f"No suitable model for {requirements.task_type}")
            return None
        
        best = candidates[0]
        logger.info(f"Selected model: {best[0]} (score: {best[1]:.3f})")
        return best[0]
    
    def _validate_recommendations(
        self,
        recommendations: list[str],
        requirements: TaskRequirements,
    ) -> list[str]:
        """Filter recommendations by hard constraints."""
        valid = []
        for model_id in recommendations:
            model = self.registry.get_model(model_id)
            if model and self.scorer.score(model, requirements) > 0:
                valid.append(model_id)
        return valid
    
    def _score_candidates(
        self,
        requirements: TaskRequirements,
    ) -> list[tuple[str, float]]:
        """Score all available models."""
        candidates = []
        
        for model in self.registry.get_all_models():
            # Skip blocked models
            if self.guide and self.guide.is_model_blocked(model.api_name):
                continue
            
            score = self.scorer.score(model, requirements)
            if score > 0:
                candidates.append((model.api_name, score))
        
        return sorted(candidates, key=lambda x: x[1], reverse=True)
    
    def get_fallback_chain(
        self,
        requirements: TaskRequirements,
        exclude: list[str] | None = None,
        max_fallbacks: int = 5,
    ) -> list[str]:
        """
        Get ordered list of fallback models.
        
        Args:
            requirements: Task requirements
            exclude: Models to exclude (e.g., already failed)
            max_fallbacks: Maximum number of fallbacks to return
        """
        exclude_set = set(exclude or [])
        
        # Check guide for explicit chain
        if self.guide:
            chain = self.guide.get_fallback_chain(requirements.task_type.name)
            if chain:
                return [m for m in chain if m not in exclude_set][:max_fallbacks]
        
        # Build from scored candidates
        candidates = self._score_candidates(requirements)
        return [m for m, _ in candidates if m not in exclude_set][:max_fallbacks]
```

### Task 3.2: Create Execution Package

Create directory structure:

```
src/lattice_lock/orchestrator/execution/
├── __init__.py
├── client_pool.py
└── conversation.py
```

### Task 3.3: Implement Client Pool

Create `src/lattice_lock/orchestrator/execution/client_pool.py`:

```python
"""
Client Pool for managing API client lifecycle.
"""
import logging
from typing import Dict

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import ProviderUnavailableError

from ..providers import (
    BaseAPIClient,
    ProviderAvailability,
    get_api_client,
)

logger = logging.getLogger(__name__)


class ClientPool:
    """
    Manages API client instances with lazy initialization.
    
    Provides client caching and provider availability checking.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self._clients: Dict[str, BaseAPIClient] = {}
    
    def get_client(self, provider: str) -> BaseAPIClient:
        """
        Get or create client for provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Configured client instance
            
        Raises:
            ProviderUnavailableError: If credentials missing
        """
        if provider not in self._clients:
            logger.debug(f"Creating client for provider: {provider}")
            self._clients[provider] = get_api_client(
                provider,
                check_availability=True,
                config=self.config,
            )
        
        return self._clients[provider]
    
    def is_available(self, provider: str) -> bool:
        """Check if provider has credentials configured."""
        return ProviderAvailability.is_available(provider)
    
    def get_available_providers(self) -> list[str]:
        """Get list of available providers."""
        return ProviderAvailability.get_available_providers()
    
    async def close_all(self) -> None:
        """Close all client connections."""
        for provider, client in self._clients.items():
            try:
                await client.__aexit__(None, None, None)
                logger.debug(f"Closed client for {provider}")
            except Exception as e:
                logger.warning(f"Error closing {provider} client: {e}")
        
        self._clients.clear()
    
    def reset(self) -> None:
        """Reset pool state for testing."""
        self._clients.clear()
```

### Task 3.4: Implement Conversation Executor with Token Aggregation

⚠️ **BILLING-CRITICAL CODE** - Requires second engineer review

Create `src/lattice_lock/orchestrator/execution/conversation.py`:

```python
"""
Conversation Executor with billing-critical token aggregation.

CRITICAL: This module handles token counting for billing.
All changes must be reviewed by a second engineer.
"""
import json
import logging
import uuid
from typing import Any, Dict

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import BillingIntegrityError
from lattice_lock.tracing import AsyncSpanContext, get_current_trace_id

from ..providers import BaseAPIClient
from ..types import APIResponse, FunctionCall
from ..function_calling import FunctionCallHandler

logger = logging.getLogger(__name__)


class ConversationExecutor:
    """
    Executes conversations with automatic function call handling.
    
    CRITICAL: Implements billing-accurate token aggregation across
    multi-turn conversations with tool use.
    """
    
    def __init__(
        self,
        function_handler: FunctionCallHandler,
        config: AppConfig,
    ):
        self.function_handler = function_handler
        self.config = config
        self.max_function_calls = config.max_function_calls
    
    async def execute(
        self,
        client: BaseAPIClient,
        model: str,
        messages: list[dict[str, Any]],
        trace_id: str | None = None,
        **kwargs,
    ) -> APIResponse:
        """
        Execute conversation with token aggregation.
        
        CRITICAL: Token totals MUST be accurately aggregated across
        all iterations for correct billing.
        
        Args:
            client: API client to use
            model: Model identifier
            messages: Conversation messages
            trace_id: Optional trace ID for observability
            **kwargs: Additional API arguments
            
        Returns:
            APIResponse with aggregated token usage
        """
        request_trace_id = trace_id or get_current_trace_id() or str(uuid.uuid4())
        
        async with AsyncSpanContext(
            "conversation_execute",
            trace_id=request_trace_id,
            attributes={"model": model, "message_count": len(messages)},
        ):
            # BILLING CRITICAL: Initialize aggregation counters
            total_usage: Dict[str, int] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }
            
            conversation = list(messages)  # Copy to avoid mutation
            function_call_count = 0
            
            functions_metadata = self.function_handler.get_registered_functions_metadata()
            functions = list(functions_metadata.values()) if functions_metadata else None
            
            while function_call_count < self.max_function_calls:
                async with AsyncSpanContext(
                    "llm_call",
                    trace_id=request_trace_id,
                    attributes={"iteration": function_call_count},
                ):
                    response = await client.chat_completion(
                        model=model,
                        messages=conversation,
                        functions=functions,
                        **kwargs,
                    )
                
                # BILLING CRITICAL: Aggregate usage from EVERY call
                if response.usage:
                    self._aggregate_usage(total_usage, response.usage)
                    logger.debug(
                        f"Token aggregation after call {function_call_count}: "
                        f"prompt={total_usage['prompt_tokens']}, "
                        f"completion={total_usage['completion_tokens']}"
                    )
                
                # Check if conversation is complete
                if not response.function_call:
                    # BILLING CRITICAL: Validate and assign aggregated totals
                    self._validate_token_totals(total_usage, response)
                    response.usage = total_usage
                    return response
                
                # Handle function call
                function_call_count += 1
                logger.info(
                    f"Function call {function_call_count}/{self.max_function_calls}: "
                    f"{response.function_call.name}"
                )
                
                try:
                    result = await self._execute_function(response.function_call)
                    conversation = self._append_function_result(
                        conversation, response, result
                    )
                except Exception as e:
                    logger.error(f"Function execution failed: {e}")
                    response.error = str(e)
                    response.usage = total_usage
                    return response
            
            # Max calls reached
            logger.warning(f"Max function calls ({self.max_function_calls}) reached")
            response.usage = total_usage
            return response
    
    def _aggregate_usage(self, total: Dict[str, int], usage: Any) -> None:
        """
        BILLING CRITICAL: Aggregate token usage from a single call.
        
        Args:
            total: Running total to update
            usage: Usage from current call
        """
        if hasattr(usage, "prompt_tokens"):
            total["prompt_tokens"] += usage.prompt_tokens or 0
        elif isinstance(usage, dict):
            total["prompt_tokens"] += usage.get("prompt_tokens", 0)
        
        if hasattr(usage, "completion_tokens"):
            total["completion_tokens"] += usage.completion_tokens or 0
        elif isinstance(usage, dict):
            total["completion_tokens"] += usage.get("completion_tokens", 0)
        
        # Recalculate total (don't trust provider's total)
        total["total_tokens"] = total["prompt_tokens"] + total["completion_tokens"]
    
    def _validate_token_totals(self, aggregated: Dict[str, int], response: APIResponse) -> None:
        """
        BILLING CRITICAL: Validate aggregation integrity.
        
        Raises BillingIntegrityError if token data appears corrupted.
        """
        # Check for zero aggregation when response has usage
        if response.usage:
            response_total = getattr(response.usage, "total_tokens", 0)
            if isinstance(response.usage, dict):
                response_total = response.usage.get("total_tokens", 0)
            
            if aggregated["total_tokens"] == 0 and response_total > 0:
                logger.critical(
                    "TOKEN AGGREGATION FAILURE: "
                    f"Aggregated total is 0 but response has {response_total} tokens"
                )
                raise BillingIntegrityError(
                    f"Token aggregation failed: expected >0, got {aggregated['total_tokens']}"
                )
        
        # Validate arithmetic consistency
        if aggregated["total_tokens"] != (aggregated["prompt_tokens"] + aggregated["completion_tokens"]):
            logger.critical(
                f"TOKEN SUM MISMATCH: total={aggregated['total_tokens']}, "
                f"prompt+completion={aggregated['prompt_tokens'] + aggregated['completion_tokens']}"
            )
            raise BillingIntegrityError("Token total does not match sum of prompt + completion")
    
    async def _execute_function(self, function_call: FunctionCall) -> Any:
        """Execute a function call."""
        return await self.function_handler.execute_function_call(
            function_call.name,
            **function_call.arguments,
        )
    
    def _append_function_result(
        self,
        conversation: list[dict],
        response: APIResponse,
        result: Any,
    ) -> list[dict]:
        """Append function call and result to conversation."""
        tool_call_id = self._extract_tool_call_id(response)
        
        # Assistant's function call
        conversation.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": response.function_call.name,
                    "arguments": json.dumps(response.function_call.arguments),
                },
            }],
        })
        
        # Tool response
        conversation.append({
            "role": "tool",
            "content": str(result),
            "tool_call_id": tool_call_id,
        })
        
        return conversation
    
    def _extract_tool_call_id(self, response: APIResponse) -> str:
        """Extract tool_call_id from response, or generate fallback."""
        try:
            raw = response.raw_response
            if raw and "choices" in raw:
                tool_calls = raw["choices"][0].get("message", {}).get("tool_calls", [])
                if tool_calls:
                    return tool_calls[0]["id"]
                except (KeyError, IndexError, TypeError) as e: logger.debug(f"Could not extract tool_call_id: {e}")
                return f"call_{uuid.uuid4().hex[:12]}"
```

### Task 3.5: Create Token Aggregation Tests (IMPLEMENT FIRST)

⚠️ **IMPLEMENT THESE TESTS BEFORE THE REFACTORING CODE**

Create `tests/execution/test_token_aggregation.py`:

```python
"""
BILLING CRITICAL: Token aggregation validation tests.

These tests MUST pass before any changes to ConversationExecutor.
Run with: pytest tests/execution/test_token_aggregation.py -v
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from lattice_lock.config import AppConfig
from lattice_lock.exceptions import BillingIntegrityError
from lattice_lock.orchestrator.execution.conversation import ConversationExecutor
from lattice_lock.orchestrator.function_calling import FunctionCallHandler


def create_mock_response(prompt_tokens: int, completion_tokens: int, has_function_call: bool = False):
    """Create a mock API response with specified token counts."""
    response = MagicMock()
    response.usage = MagicMock()
    response.usage.prompt_tokens = prompt_tokens
    response.usage.completion_tokens = completion_tokens
    response.usage.total_tokens = prompt_tokens + completion_tokens
    response.function_call = MagicMock() if has_function_call else None
    response.raw_response = {"choices": [{"message": {"tool_calls": [{"id": "call_123"}]}}]}
    
    if has_function_call:
        response.function_call.name = "test_function"
        response.function_call.arguments = {}
    
    return response


def create_mock_provider(call_sequence: list):
    """
    Create mock provider that returns responses in sequence.
    
    Args:
        call_sequence: List of (prompt_tokens, completion_tokens, has_function_call) tuples
    """
    provider = AsyncMock()
    responses = [create_mock_response(*args) for args in call_sequence]
    provider.chat_completion = AsyncMock(side_effect=responses)
    return provider


class TestTokenAggregation:
    """Validate billing-critical token aggregation."""
    
    @pytest.fixture
    def config(self):
        return AppConfig()
    
    @pytest.fixture
    def function_handler(self):
        handler = MagicMock(spec=FunctionCallHandler)
        handler.get_registered_functions_metadata.return_value = {"test": {}}
        handler.execute_function_call = AsyncMock(return_value="result")
        return handler
    
    @pytest.fixture
    def executor(self, config, function_handler):
        return ConversationExecutor(function_handler, config)
    
    @pytest.mark.asyncio
    async def test_single_call_token_count(self, executor):
        """Single call should return exact token counts."""
        provider = create_mock_provider([
            (100, 50, False),  # No function call
        ])
        
        response = await executor.execute(
            client=provider,
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}],
        )
        
        assert response.usage["prompt_tokens"] == 100
        assert response.usage["completion_tokens"] == 50
        assert response.usage["total_tokens"] == 150
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool_call_count", [1, 2, 3, 5])
    async def test_multi_tool_token_aggregation(self, executor, tool_call_count):
        """
        CRITICAL: Validate token totals across N sequential tool calls.
        
        Each call adds 100 prompt + 50 completion tokens.
        Total should be (tool_call_count + 1) * (100 + 50)
        """
        # Build call sequence: N function calls + 1 final response
        call_sequence = [(100, 50, True)] * tool_call_count + [(100, 50, False)]
        provider = create_mock_provider(call_sequence)
        
        response = await executor.execute(
            client=provider,
            model="test-model",
            messages=[{"role": "user", "content": "Process data"}],
        )
        
        expected_calls = tool_call_count + 1
        expected_prompt = expected_calls * 100
        expected_completion = expected_calls * 50
        expected_total = expected_prompt + expected_completion
        
        assert response.usage["prompt_tokens"] == expected_prompt, \
            f"Expected {expected_prompt} prompt tokens, got {response.usage['prompt_tokens']}"
        assert response.usage["completion_tokens"] == expected_completion, \
            f"Expected {expected_completion} completion tokens, got {response.usage['completion_tokens']}"
        assert response.usage["total_tokens"] == expected_total, \
            f"Expected {expected_total} total tokens, got {response.usage['total_tokens']}"
    
    @pytest.mark.asyncio
    async def test_zero_aggregation_raises_error(self, executor):
        """Must raise BillingIntegrityError if aggregation fails."""
        # Create response where usage is not properly aggregated
        provider = AsyncMock()
        response = MagicMock()
        response.usage = MagicMock()
        response.usage.total_tokens = 100  # Has usage
        response.function_call = None
        
        # Force aggregation to fail by mocking internal state
        provider.chat_completion = AsyncMock(return_value=response)
        
        # Patch _aggregate_usage to simulate failure
        original_aggregate = executor._aggregate_usage
        
        def broken_aggregate(total, usage):
            pass  # Don't actually aggregate
        
        executor._aggregate_usage = broken_aggregate
        
        with pytest.raises(BillingIntegrityError):
            await executor.execute(
                client=provider,
                model="test-model",
                messages=[{"role": "user", "content": "Test"}],
            )
        
        executor._aggregate_usage = original_aggregate
    
    @pytest.mark.asyncio
    async def test_arithmetic_consistency(self, executor):
        """Total must equal prompt + completion."""
        provider = create_mock_provider([
            (100, 50, True),
            (75, 25, False),
        ])
        
        response = await executor.execute(
            client=provider,
            model="test-model",
            messages=[{"role": "user", "content": "Test"}],
        )
        
        assert response.usage["total_tokens"] == (
            response.usage["prompt_tokens"] + response.usage["completion_tokens"]
        ), "Total tokens must equal prompt + completion"


@pytest.mark.stress
class TestTokenAggregationStress:
    """Stress tests for billing integrity at scale."""
    
    @pytest.fixture
    def config(self):
        config = AppConfig()
        config.max_function_calls = 1000  # Allow many calls for stress test
        return config
    
    @pytest.fixture
    def function_handler(self):
        handler = MagicMock(spec=FunctionCallHandler)
        handler.get_registered_functions_metadata.return_value = {"test": {}}
        handler.execute_function_call = AsyncMock(return_value="result")
        return handler
    
    @pytest.fixture
    def executor(self, config, function_handler):
        return ConversationExecutor(function_handler, config)
    
    @pytest.mark.asyncio
    async def test_100_tool_calls_aggregation(self, executor):
        """Validate accurate aggregation at 100 tool calls."""
        call_count = 100
        tokens_per_call = (50, 25)  # prompt, completion
        
        call_sequence = [(*tokens_per_call, True)] * call_count + [(*tokens_per_call, False)]
        provider = create_mock_provider(call_sequence)
        
        response = await executor.execute(
            client=provider,
            model="stress-test",
            messages=[{"role": "user", "content": "Heavy workload"}],
        )
        
        expected_calls = call_count + 1
        expected_total = expected_calls * sum(tokens_per_call)
        
        assert response.usage["total_tokens"] == expected_total, \
            f"At {call_count} tool calls: expected {expected_total}, got {response.usage['total_tokens']}"
````

### Task 3.6: Create Execution Package Exports

Create `src/lattice_lock/orchestrator/execution/__init__.py`:

```python
from .client_pool import ClientPool
from .conversation import ConversationExecutor

__all__ = ["ClientPool", "ConversationExecutor"]
```

### Task 3.7: Refactor ModelOrchestrator

Update `src/lattice_lock/orchestrator/core.py`:

```python
"""
Lattice Lock Model Orchestrator

Slim coordinator that delegates to specialized components.
"""
import logging

from lattice_lock.config import AppConfig, get_config
from lattice_lock.tracing import AsyncSpanContext, generate_trace_id, get_current_trace_id

from .analysis import TaskAnalyzer
from .cost.tracker import CostTracker
from .execution import ClientPool, ConversationExecutor
from .function_calling import FunctionCallHandler
from .guide import ModelGuideParser
from .providers import FallbackManager, ProviderUnavailableError
from .registry import ModelRegistry
from .scoring import ModelScorer
from .selection import ModelSelector
from .types import APIResponse, TaskRequirements, TaskType

logger = logging.getLogger(__name__)


class ModelOrchestrator:
    """
    Intelligent model orchestration system.
    
    Routes requests to optimal models based on task analysis,
    capability scoring, and availability. Coordinates specialized
    components for selection, execution, and fallback handling.
    """
    
    def __init__(
        self,
        guide_path: str | None = None,
        config: AppConfig | None = None,
    ):
        self.config = config or get_config()
        
        # Core components
        self.registry = ModelRegistry()
        self.guide = ModelGuideParser(guide_path)
        self.scorer = ModelScorer(self.config)
        
        # Analysis
        self.analyzer = TaskAnalyzer(self.config)
        
        # Selection
        self.selector = ModelSelector(
            registry=self.registry,
            scorer=self.scorer,
            guide=self.guide,
            config=self.config,
        )
        
        # Execution
        self.client_pool = ClientPool(self.config)
        self.function_handler = FunctionCallHandler()
        self.executor = ConversationExecutor(
            function_handler=self.function_handler,
            config=self.config,
        )
        
        # Resilience
        self.fallback_manager = FallbackManager(max_retries=1)
        
        # Cost tracking
        self.cost_tracker = CostTracker(self.registry)
        
        logger.info("ModelOrchestrator initialized")
    
    def register_function(self, name: str, func) -> None:
        """Register a function for model tool use."""
        self.function_handler.register_function(name, func)
    
    async def route_request(
        self,
        prompt: str,
        model_id: str | None = None,
        task_type: TaskType | None = None,
        trace_id: str | None = None,
        **kwargs,
    ) -> APIResponse:
        """
        Route a request to the appropriate model.
        
        Args:
            prompt: User prompt
            model_id: Optional specific model override
            task_type: Optional task type override
            trace_id: Optional trace ID for distributed tracing
            **kwargs: Additional API arguments
            
        Returns:
            APIResponse with model completion
        """
        request_trace_id = trace_id or get_current_trace_id() or generate_trace_id()
        
        async with AsyncSpanContext(
            "route_request",
            trace_id=request_trace_id,
            attributes={"model_id": model_id, "task_type": str(task_type)},
        ):
            # 1. Analyze task
            requirements = self.analyzer.analyze(prompt)
            if task_type:
                requirements.task_type = task_type
            
            logger.info(f"Task: {requirements.task_type.name}")
            
            # 2. Select model
            selected_model_id = model_id or self.selector.select_best_model(requirements)
            if not selected_model_id:
                raise ValueError("No suitable model found")
            
            model = self.registry.get_model(selected_model_id)
            if not model:
                raise ValueError(f"Model {selected_model_id} not in registry")
            
            logger.info(f"Selected: {selected_model_id} ({model.provider.value})")
            
            # 3. Execute with fallback
            messages = kwargs.pop("messages", None) or [{"role": "user", "content": prompt}]
            
            return await self._execute_with_fallback(
                model_id=selected_model_id,
                messages=messages,
                requirements=requirements,
                trace_id=request_trace_id,
                **kwargs,
            )
    
    async def _execute_with_fallback(
        self,
        model_id: str,
        messages: list[dict],
        requirements: TaskRequirements,
        trace_id: str,
        **kwargs,
    ) -> APIResponse:
        """Execute request with automatic fallback on failure."""
        # Build candidate chain
        fallback_chain = self.selector.get_fallback_chain(
            requirements, exclude=[model_id]
        )
        candidates = [model_id] + fallback_chain
        
        # Filter to available providers
        available = []
        for mid in candidates:
            model = self.registry.get_model(mid)
            if model and self.client_pool.is_available(model.provider.value):
                available.append(mid)
        
        if not available:
            providers = self.client_pool.get_available_providers()
            raise RuntimeError(f"No available providers. Configured: {providers or 'None'}")
        
        async def try_model(candidate_id: str) -> APIResponse:
            model = self.registry.get_model(candidate_id)
            client = self.client_pool.get_client(model.provider.value)
            
            response = await self.executor.execute(
                client=client,
                model=model.api_name,
                messages=messages,
                trace_id=trace_id,
                **kwargs,
            )
            
            # Track cost with AGGREGATED token counts
            self.cost_tracker.record_transaction(
                response,
                task_type=str(requirements.task_type),
                trace_id=trace_id,
            )
            
            return response
        
        return await self.fallback_manager.execute_with_fallback(
            func=try_model,
            candidates=available,
        )
    
    def get_available_providers(self) -> list[str]:
        """Get list of available providers."""
        return self.client_pool.get_available_providers()
    
    async def close(self) -> None:
        """Clean up resources."""
        await self.client_pool.close_all()
```

### Chunk 3 Validation Gate

```bash
# CRITICAL: Run token aggregation tests FIRST
pytest tests/execution/test_token_aggregation.py -v --strict-markers

# Then run all execution tests
pytest tests/execution/ -v

# Integration check
python -c "from lattice_lock.orchestrator.execution import ConversationExecutor; print('✅ Execution imports work')"
python -c "from lattice_lock.orchestrator.selection import ModelSelector; print('✅ Selection imports work')"
```

**Rollback Criteria for Chunk 3:**

- [ ] ANY token aggregation test fails
- [ ] `BillingIntegrityError` raised during normal operation
- [ ] Token counts in responses don't match expected values
- [ ] Cost tracking shows anomalies vs baseline

---

## Work Chunk 4: Admin Auth Security Hardening

**Objective:** Modernize auth with PyJWT and strict security validation.

**Risk Level:** Medium

### Task 4.1: Create Auth Package Structure

```
src/lattice_lock/admin/auth/
├── __init__.py
├── config.py
├── models.py
├── passwords.py
├── tokens.py
├── api_keys.py
├── storage.py
├── users.py
├── dependencies.py
└── flows.py
```

### Task 4.2: Implement Auth Config

Create `src/lattice_lock/admin/auth/config.py`:

```python
"""Authentication configuration with security enforcement."""
import os
import logging
from typing import Optional

from pydantic import BaseModel, Field, SecretStr, model_validator

from lattice_lock.exceptions import SecurityConfigurationError

logger = logging.getLogger(__name__)


class AuthConfig(BaseModel):
    """
    Authentication configuration with production security enforcement.
    
    In production, strict security requirements are enforced:
    - Secret key must be set via environment variable
    - Secret key must be at least 32 characters
    """
    
    secret_key: Optional[SecretStr] = Field(default=None)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    api_key_prefix: str = "llk_"
    password_min_length: int = 8
    
    @model_validator(mode="after")
    def enforce_security(self) -> "AuthConfig":
        """Enforce security requirements based on environment."""
        env = os.environ.get("LATTICE_ENV", "dev")
        
        # Try to load from environment if not set
        if self.secret_key is None:
            env_key = os.environ.get("LATTICE_LOCK_SECRET_KEY")
            if env_key:
                self.secret_key = SecretStr(env_key)
        
        if env == "production":
            if self.secret_key is None:
                raise SecurityConfigurationError(
                    "LATTICE_LOCK_SECRET_KEY must be set in production environment"
                )
            if len(self.secret_key.get_secret_value()) < 32:
                raise SecurityConfigurationError(
                    "LATTICE_LOCK_SECRET_KEY must be at least 32 characters in production"
                )
            logger.info("Production security configuration validated")
        else:
            if self.secret_key is None:
                self.secret_key = SecretStr("dev-secret-key-do-not-use-in-production")
                logger.warning(
                    "Using default dev secret key. "
                    "Set LATTICE_LOCK_SECRET_KEY for production."
                )
        
        return self


# Global config instance
_auth_config: Optional[AuthConfig] = None


def get_auth_config() -> AuthConfig:
    """Get the authentication configuration."""
    global _auth_config
    if _auth_config is None:
        _auth_config = AuthConfig()
    return _auth_config


def configure_auth(config: AuthConfig) -> None:
    """Set the authentication configuration."""
    global _auth_config
    _auth_config = config


def reset_auth_config() -> None:
    """Reset auth config for testing."""
    global _auth_config
    _auth_config = None
```

### Task 4.3: Implement Auth Storage Protocol

Create `src/lattice_lock/admin/auth/storage.py`:

```python
"""
Authentication storage abstraction.

Defines protocol for storage backends and provides in-memory implementation.
Future: Implement DatabaseAuthStorage for production persistence.
"""
from datetime import datetime, timezone
from typing import Protocol, Optional, Dict, Set, Tuple, List

from .models import User, Role, APIKeyInfo


class AuthStorage(Protocol):
    """
    Protocol for authentication storage backends.
    
    Implement this protocol for custom storage (e.g., database).
    """
    
    # User operations
    def get_user(self, username: str) -> Optional[User]: ...
    def create_user(self, user: User) -> None: ...
    def delete_user(self, username: str) -> bool: ...
    def list_users(self) -> List[User]: ...
    
    # Token revocation
    def revoke_token(self, jti: str) -> None: ...
    def is_token_revoked(self, jti: str) -> bool: ...
    
    # API keys
    def store_api_key(
        self, key_hash: str, username: str, role: Role, key_id: str, name: str
    ) -> None: ...
    def get_api_key_info(self, key_hash: str) -> Optional[Tuple[str, Role, str]]: ...
    def delete_api_key(self, key_id: str) -> bool: ...
    def list_api_keys(self, username: str) -> List[APIKeyInfo]: ...
    
    # Cleanup
    def clear_all(self) -> None: ...


class InMemoryAuthStorage:
    """
    In-memory implementation of AuthStorage.
    
    Suitable for development and testing. For production, implement
    a database-backed storage class.
    """
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._revoked_tokens: Set[str] = set()
        self._api_keys: Dict[str, Tuple[str, Role, str]] = {}  # hash -> (user, role, key_id)
        self._api_key_metadata: Dict[str, APIKeyInfo] = {}  # key_id -> metadata
    
    def get_user(self, username: str) -> Optional[User]:
        return self._users.get(username)
    
    def create_user(self, user: User) -> None:
        self._users[user.username] = user
    
    def delete_user(self, username: str) -> bool:
        if username in self._users:
            del self._users[username]
            return True
        return False
    
    def list_users(self) -> List[User]:
        return list(self._users.values())
    
    def revoke_token(self, jti: str) -> None:
        self._revoked_tokens.add(jti)
    
    def is_token_revoked(self, jti: str) -> bool:
        return jti in self._revoked_tokens
    
    def store_api_key(
        self, key_hash: str, username: str, role: Role, key_id: str, name: str
    ) -> None:
        self._api_keys[key_hash] = (username, role, key_id)
        self._api_key_metadata[key_id] = APIKeyInfo(
            key_id=key_id,
            created_at=datetime.now(timezone.utc),
            name=name,
        )
    
    def get_api_key_info(self, key_hash: str) -> Optional[Tuple[str, Role, str]]:
        return self._api_keys.get(key_hash)
    
    def delete_api_key(self, key_id: str) -> bool:
        # Find and remove the key
        for key_hash, (_, _, kid) in list(self._api_keys.items()):
            if kid == key_id:
                del self._api_keys[key_hash]
                self._api_key_metadata.pop(key_id, None)
                return True
        return False
    
    def list_api_keys(self, username: str) -> List[APIKeyInfo]:
        result = []
        for key_hash, (user, _, key_id) in self._api_keys.items():
            if user == username:
                if key_id in self._api_key_metadata:
                    result.append(self._api_key_metadata[key_id])
        return result
    
    def clear_all(self) -> None:
        """Reset all storage for testing."""
        self._users.clear()
        self._revoked_tokens.clear()
        self._api_keys.clear()
        self._api_key_metadata.clear()


# Global storage instance
_storage: Optional[AuthStorage] = None


def get_storage() -> AuthStorage:
    """Get the current storage instance."""
    global _storage
    if _storage is None:
        _storage = InMemoryAuthStorage()
    return _storage


def set_storage(storage: AuthStorage) -> None:
    """Set the storage implementation."""
    global _storage
    _storage = storage


def reset_storage() -> None:
    """Reset storage for testing."""
    global _storage
    _storage = None
```

### Task 4.4: Implement JWT Tokens with PyJWT

Create `src/lattice_lock/admin/auth/tokens.py`:

```python
"""
JWT token operations using PyJWT.

Replaces deprecated python-jose with actively maintained PyJWT.
"""
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, status

from .config import get_auth_config
from .models import Role, TokenData
from .storage import get_storage

logger = logging.getLogger(__name__)


def create_access_token(
    username: str,
    role: Role,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    config = get_auth_config()
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=config.access_token_expire_minutes)
    
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    jti = secrets.token_urlsafe(16)
    
    payload = {
        "sub": username,
        "role": role.value,
        "exp": expire,
        "iat": now,
        "jti": jti,
        "token_type": "access",
    }
    
    return jwt.encode(
        payload,
        config.secret_key.get_secret_value(),
        algorithm=config.algorithm,
    )


def create_refresh_token(
    username: str,
    role: Role,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token."""
    config = get_auth_config()
    
    if expires_delta is None:
        expires_delta = timedelta(days=config.refresh_token_expire_days)
    
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    jti = secrets.token_urlsafe(16)
    
    payload = {
        "sub": username,
        "role": role.value,
        "exp": expire,
        "iat": now,
        "jti": jti,
        "token_type": "refresh",
    }
    
    return jwt.encode(
        payload,
        config.secret_key.get_secret_value(),
        algorithm=config.algorithm,
    )


def verify_token(token: str, expected_type: str = "access") -> TokenData:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        expected_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded TokenData
        
    Raises:
        HTTPException: If token is invalid, expired, or revoked
    """
    config = get_auth_config()
    storage = get_storage()
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            config.secret_key.get_secret_value(),
            algorithms=[config.algorithm],
        )
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        jti: str = payload.get("jti", "")
        if storage.is_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )
        
        token_type: str = payload.get("token_type", "access")
        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type: expected {expected_type}",
            )
        
        role = Role(payload.get("role"))
        
        return TokenData(
            sub=username,
            role=role,
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            jti=jti,
            token_type=token_type,
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise credentials_exception


def revoke_token(jti: str) -> None:
    """Revoke a token by its JTI."""
    get_storage().revoke_token(jti)
    logger.info(f"Token revoked: {jti[:8]}...")
```

### Task 4.5: Implement Remaining Auth Modules

Create the remaining modules following similar patterns:

- `models.py` - Role enum, User, TokenData, TokenResponse, APIKeyInfo
- `passwords.py` - hash_password, verify_password using bcrypt
- `api_keys.py` - generate, verify, revoke, rotate API keys
- `users.py` - CRUD operations for users
- `dependencies.py` - FastAPI Depends functions
- `flows.py` - Login flows

### Task 4.6: Create Auth Package Exports

Create `src/lattice_lock/admin/auth/__init__.py`:

```python
"""
Lattice Lock Admin Authentication Package

JWT and API key authentication with role-based access control.
"""
from .config import AuthConfig, get_auth_config, configure_auth, reset_auth_config
from .models import Role, User, TokenData, TokenResponse, APIKeyInfo
from .passwords import hash_password, verify_password
from .tokens import create_access_token, create_refresh_token, verify_token, revoke_token
from .api_keys import generate_api_key, verify_api_key, revoke_api_key, rotate_api_key
from .storage import (
    AuthStorage, InMemoryAuthStorage,
    get_storage, set_storage, reset_storage,
)
from .users import create_user, get_user, authenticate_user, delete_user
from .dependencies import (
    get_current_user, require_roles, require_permission,
    require_admin, require_operator, require_viewer,
)
from .flows import login_for_access_token, refresh_access_token

__all__ = [
    # Config
    "AuthConfig", "get_auth_config", "configure_auth", "reset_auth_config",
    # Models
    "Role", "User", "TokenData", "TokenResponse", "APIKeyInfo",
    # Passwords
    "hash_password", "verify_password",
    # Tokens
    "create_access_token", "create_refresh_token", "verify_token", "revoke_token",
    # API Keys
    "generate_api_key", "verify_api_key", "revoke_api_key", "rotate_api_key",
    # Storage
    "AuthStorage", "InMemoryAuthStorage", "get_storage", "set_storage", "reset_storage",
    # Users
    "create_user", "get_user", "authenticate_user", "delete_user",
    # Dependencies
    "get_current_user", "require_roles", "require_permission",
    "require_admin", "require_operator", "require_viewer",
    # Flows
    "login_for_access_token", "refresh_access_token",
]
```

### Task 4.7: Delete Old Auth Module

```bash
rm src/lattice_lock/admin/auth.py
```

### Task 4.8: Create Security Tests

Create `tests/auth/test_security.py`:

```python
"""Security validation tests for authentication."""
import pytest
from unittest.mock import patch

from lattice_lock.exceptions import SecurityConfigurationError
from lattice_lock.admin.auth import AuthConfig, reset_auth_config


class TestProductionSecurityEnforcement:
    """Test production security requirements."""
    
    def setup_method(self):
        reset_auth_config()
    
    def teardown_method(self):
        reset_auth_config()
    
    def test_production_requires_secret_key(self):
        """Production must have LATTICE_LOCK_SECRET_KEY set."""
        with patch.dict("os.environ", {
            "LATTICE_ENV": "production",
        }, clear=True):
            with pytest.raises(SecurityConfigurationError) as exc:
                AuthConfig()
            assert "must be set in production" in str(exc.value)
    
    def test_production_rejects_short_key(self):
        """Production must reject keys under 32 characters."""
        with patch.dict("os.environ", {
            "LATTICE_ENV": "production",
            "LATTICE_LOCK_SECRET_KEY": "short_key",
        }):
            with pytest.raises(SecurityConfigurationError) as exc:
                AuthConfig()
            assert "at least 32 characters" in str(exc.value)
    
    def test_production_accepts_valid_key(self):
        """Production accepts keys of 32+ characters."""
        with patch.dict("os.environ", {
            "LATTICE_ENV": "production",
            "LATTICE_LOCK_SECRET_KEY": "a" * 32,
        }):
            config = AuthConfig()
            assert config.secret_key is not None
    
    def test_dev_uses_default_key(self):
        """Development environment uses default key if not set."""
        with patch.dict("os.environ", {
            "LATTICE_ENV": "dev",
        }, clear=True):
            config = AuthConfig()
            assert config.secret_key is not None
            assert "dev" in config.secret_key.get_secret_value()
```

### Chunk 4 Validation Gate

```bash
pytest tests/auth/test_security.py -v --strict-markers
pytest tests/auth/ -v
python -c "from lattice_lock.admin.auth import create_access_token, verify_token; print('✅ Auth imports work')"
```

**Rollback Criteria for Chunk 4:**

- [ ] ANY security test fails
- [ ] `SecurityConfigurationError` not raised for insecure production config
- [ ] JWT validation fails for valid tokens
- [ ] Authentication success rate drops

---

## Work Chunk 5: Error Middleware & Background Tasks

**Objective:** Fix background task lifecycle and deduplicate error boundary logic.

**Risk Level:** Medium

### Task 5.1: Create Background Task Queue

Create `src/lattice_lock/utils/async_compat.py`:

```python
"""
Async/Sync compatibility utilities.

Provides background task management with shutdown guarantees.
"""
import asyncio
import functools
import inspect
import logging
import time
from typing import Any, Awaitable, Callable, Set

from lattice_lock.exceptions import BackgroundTaskError

logger = logging.getLogger(__name__)


class BackgroundTaskQueue:
    """
    Background task queue with lifecycle management.
    
    Ensures tasks are tracked and can be awaited during shutdown.
    Prevents task submission after shutdown initiated.
    """
    
    def __init__(self):
        self._tasks: Set[asyncio.Task] = set()
        self._shutdown = False
    
    def enqueue(self, coro: Awaitable[Any]) -> asyncio.Task | None:
        """
        Enqueue a coroutine for background execution.
        
        Args:
            coro: Coroutine to execute
            
        Returns:
            Task if enqueued, None if no event loop
            
        Raises:
            RuntimeError: If called after shutdown initiated
        """
        if self._shutdown:
            logger.error(f"Task rejected after shutdown: {coro}")
            raise RuntimeError("Cannot enqueue tasks after shutdown initiated")
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.debug("No event loop available for background task")
            return None
        
        task = loop.create_task(self._run_with_cleanup(coro))
        self._tasks.add(task)
        return task
    
    async def _run_with_cleanup(self, coro: Awaitable[Any]) -> Any:
        """Run coroutine and remove from tracking on completion."""
        try:
            return await coro
        finally:
            current = asyncio.current_task()
            if current:
                self._tasks.discard(current)
    
    async def wait_all(self, timeout: float = 5.0) -> None:
        """
        Wait for all pending tasks to complete.
        
        Args:
            timeout: Maximum seconds to wait
            
        Raises:
            BackgroundTaskError: If tasks don't complete within timeout
        """
        self._shutdown = True
        
        if not self._tasks:
            return
        
        logger.info(f"Waiting for {len(self._tasks)} background tasks...")
        
        done, pending = await asyncio.wait(
            self._tasks,
            timeout=timeout,
            return_when=asyncio.ALL_COMPLETED,
        )
        
        if pending:
            logger.critical(f"UNFINISHED TASKS: {len(pending)} tasks did not complete")
            for task in pending:
                task.cancel()
            raise BackgroundTaskError(
                f"{len(pending)} background tasks failed to complete within {timeout}s"
            )
        
        logger.info("All background tasks completed")
    
    def pending_count(self) -> int:
        """Get count of pending tasks."""
        return len(self._tasks)
    
    def reset(self) -> None:
        """Reset queue state for testing."""
        self._tasks.clear()
        self._shutdown = False


# Global background queue
_background_queue: BackgroundTaskQueue | None = None


def get_background_queue() -> BackgroundTaskQueue:
    """Get the global background task queue."""
    global _background_queue
    if _background_queue is None:
        _background_queue = BackgroundTaskQueue()
    return _background_queue


def reset_background_queue() -> None:
    """Reset background queue for testing."""
    global _background_queue
    _background_queue = None
```

### Task 5.2: Refactor Error Boundary with Shared Logic

Update `src/lattice_lock/errors/middleware.py`:

```python
"""
Error middleware with deduplicated sync/async handling.
"""
import asyncio
import functools
import inspect
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from lattice_lock.utils.async_compat import get_background_queue

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt using exponential backoff."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


@dataclass
class ErrorContext:
    """Context information about an error."""
    error_type: str
    message: str
    severity: str = "medium"
    category: str = "unknown"
    details: dict = field(default_factory=dict)
    recoverability: Any = None


def classify_error(e: Exception) -> ErrorContext:
    """Classify an exception into an ErrorContext."""
    # Implementation
    return ErrorContext(
        error_type=type(e).__name__,
        message=str(e),
    )


def _build_error_handler(
    func_name: str,
    retry_config: RetryConfig,
    recoverable_errors: list[type[Exception]],
    on_error: Callable[[ErrorContext], Any] | None,
    log_errors: bool,
    track_metrics: bool,
):
    """
    Build shared error handling logic for sync and async wrappers.
    
    This eliminates duplication between sync_wrapper and async_wrapper.
    """
    
    def handle_error(e: Exception, attempt: int) -> tuple[bool, float]:
        """
        Handle an error and determine retry behavior.
        
        Returns:
            (should_retry, delay_seconds)
        """
        context = classify_error(e)
        
        if track_metrics:
            _global_metrics.record_error(context)
        
        if log_errors:
            logger.error(f"{func_name} failed: {context.message}")
        
        if on_error:
            on_error(context)
        
        # Determine if we should retry
        is_recoverable = any(isinstance(e, t) for t in recoverable_errors)
        can_retry = (
            is_recoverable and
            getattr(context.recoverability, "should_retry", False) and
            attempt < retry_config.max_retries
        )
        
        delay = retry_config.get_delay(attempt) if can_retry else 0
        return can_retry, delay
    
    return handle_error


def error_boundary(
    recoverable_errors: list[type[Exception]] | None = None,
    on_error: Callable[[ErrorContext], Any] | None = None,
    retry_config: RetryConfig | None = None,
    fallback: Callable[..., T] | None = None,
    log_errors: bool = True,
    track_metrics: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator providing error boundary protection with unified sync/async handling.
    
    Args:
        recoverable_errors: Exception types that can be retried
        on_error: Callback when error occurs
        retry_config: Retry behavior configuration
        fallback: Fallback function if all retries fail
        log_errors: Whether to log errors
        track_metrics: Whether to track error metrics
    """
    recoverable = recoverable_errors or []
    config = retry_config or RetryConfig(max_retries=0)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        handle_error = _build_error_handler(
            func.__name__, config, recoverable, on_error, log_errors, track_metrics
        )
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                attempt = 0
                while True:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        can_retry, delay = handle_error(e, attempt)
                        if can_retry:
                            logger.info(
                                f"Retrying {func.__name__} in {delay:.2f}s "
                                f"(attempt {attempt + 1}/{config.max_retries})"
                            )
                            await asyncio.sleep(delay)
                            attempt += 1
                        elif fallback is not None:
                            logger.warning(f"Using fallback for {func.__name__}")
                            if asyncio.iscoroutinefunction(fallback):
                                return await fallback(*args, **kwargs)
                            return fallback(*args, **kwargs)
                        else:
                            raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                attempt = 0
                while True:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        can_retry, delay = handle_error(e, attempt)
                        if can_retry:
                            logger.info(
                                f"Retrying {func.__name__} in {delay:.2f}s "
                                f"(attempt {attempt + 1}/{config.max_retries})"
                            )
                            time.sleep(delay)
                            attempt += 1
                        elif fallback is not None:
                            logger.warning(f"Using fallback for {func.__name__}")
                            return fallback(*args, **kwargs)
                        else:
                            raise
            return sync_wrapper
    
    return decorator


@dataclass
class ErrorMetrics:
    """Tracks error metrics for telemetry."""
    
    error_counts: dict[str, int] = field(default_factory=dict)
    error_rates: dict[str, float] = field(default_factory=dict)
    last_errors: dict[str, list[float]] = field(default_factory=list)
    _persistence_enabled: bool = True
    _persistence_errors: int = 0
    _max_persistence_errors: int = 10
    
    def record_error(self, context: ErrorContext, project_id: str | None = None) -> None:
        """Record an error occurrence."""
        error_type = context.error_type
        current_time = time.time()
        
        # Sync metric updates
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        if error_type not in self.last_errors:
            self.last_errors[error_type] = []
        self.last_errors[error_type].append(current_time)
        
        # Rate calculation (last 60 seconds)
        cutoff = current_time - 60
        self.last_errors[error_type] = [
            t for t in self.last_errors[error_type] if t > cutoff
        ]
        self.error_rates[error_type] = len(self.last_errors[error_type])
        
        # Async persistence via background queue
        if project_id and self._persistence_enabled:
            self._enqueue_persistence(context, project_id)
    
    def _enqueue_persistence(self, context: ErrorContext, project_id: str) -> None:
        """Enqueue error persistence as background task."""
        queue = get_background_queue()
        try:
            task = queue.enqueue(self._persist_error(context, project_id))
            if task is None:
                logger.debug("No event loop for error persistence")
        except RuntimeError as e:
            logger.warning(f"Could not enqueue persistence: {e}")
    
    async def _persist_error(self, context: ErrorContext, project_id: str) -> None:
        """Persist error to database."""
        try:
            from lattice_lock.admin.db import async_session
            from lattice_lock.admin.routes import record_project_error
            
            async with async_session() as db:
                await record_project_error(
                    db, project_id, context.error_type, context.message,
                    context.severity, context.category, context.details
                )
            
            self._persistence_errors = 0
            
        except ImportError:
            logger.info("Database module unavailable, disabling error persistence")
            self._persistence_enabled = False
        except Exception as e:
            self._persistence_errors += 1
            logger.warning(f"Error persistence failed ({self._persistence_errors}): {e}")
            
            if self._persistence_errors >= self._max_persistence_errors:
                logger.error("Too many persistence failures, disabling")
                self._persistence_enabled = False
    
    def reset(self) -> None:
        """Reset metrics for testing."""
        self.error_counts.clear()
        self.error_rates.clear()
        self.last_errors.clear()
        self._persistence_enabled = True
        self._persistence_errors = 0


# Global metrics instance
_global_metrics = ErrorMetrics()


def reset_metrics() -> None:
    """Reset global metrics for testing."""
    global _global_metrics
    _global_metrics = ErrorMetrics()


def get_metrics() -> ErrorMetrics:
    """Get the global metrics instance."""
    return _global_metrics
```

### Task 5.3: Update Application Lifespan

Update the main FastAPI application (e.g., `src/lattice_lock/admin/app.py`):

```python
"""FastAPI application with proper lifespan management."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from lattice_lock.utils.async_compat import get_background_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Ensures graceful shutdown of background tasks.
    """
    # Startup
    app.state.task_queue = get_background_queue()
    yield
    # Shutdown - CRITICAL: await all background tasks
    await app.state.task_queue.wait_all()


app = FastAPI(lifespan=lifespan)
```

### Chunk 5 Validation Gate

```bash
pytest tests/errors/ -v
pytest tests/utils/test_async_compat.py -v
python -c "from lattice_lock.utils.async_compat import BackgroundTaskQueue; print('✅ Async utils work')"
```

**Rollback Criteria for Chunk 5:**

- [ ] Background tasks fail to complete on shutdown
- [ ] `BackgroundTaskError` raised during normal operation
- [ ] Error metrics not recorded correctly

---

## Work Chunk 6: Testing Infrastructure

**Objective:** Standardize test isolation with comprehensive reset fixtures.

**Risk Level:** Medium

### Task 6.1: Implement Global State Capture

Create `tests/conftest.py`:

```python
"""
Pytest configuration with comprehensive state isolation.

All global state is reset before and after each test to prevent pollution.
"""
import pytest
from typing import Dict, Any


def _capture_global_state() -> Dict[str, Any]:
    """
    Capture snapshot of all global state for isolation validation.
    
    Returns dict with counts of various stateful components.
    """
    state = {}
    
    try:
        from lattice_lock.orchestrator.providers.base import ProviderAvailability
        state["provider_status_count"] = len(getattr(ProviderAvailability, "_status", {}))
    except ImportError:
        state["provider_status_count"] = 0
    
    try:
        from lattice_lock.errors.middleware import get_metrics
        metrics = get_metrics()
        state["error_count"] = sum(metrics.error_counts.values())
    except ImportError:
        state["error_count"] = 0
    
    try:
        from lattice_lock.admin.auth import get_storage
        state["user_count"] = len(get_storage().list_users())
    except ImportError:
        state["user_count"] = 0
    
    return state


def _reset_all_globals() -> None:
    """Reset all global state."""
    # Config
    try:
        from lattice_lock.config import reset_config
        reset_config()
    except ImportError:
        pass
    
    # Providers
    try:
        from lattice_lock.orchestrator.providers.base import ProviderAvailability
        ProviderAvailability.reset()
    except ImportError:
        pass
    
    # Error metrics
    try:
        from lattice_lock.errors.middleware import reset_metrics
        reset_metrics()
    except ImportError:
        pass
    
    # Performance metrics
    try:
        from lattice_lock.tracing import reset_performance_metrics
        reset_performance_metrics()
    except ImportError:
        pass
    
    # Auth storage
    try:
        from lattice_lock.admin.auth import reset_storage, reset_auth_config
        reset_storage()
        reset_auth_config()
    except ImportError:
        pass
    
    # Background queue
    try:
        from lattice_lock.utils.async_compat import reset_background_queue
        reset_background_queue()
    except ImportError:
        pass


@pytest.fixture(autouse=True)
def reset_global_state():
    """
    Reset all global state before and after each test.
    
    This fixture runs automatically for every test.
    """
    _reset_all_globals()
    yield
    _reset_all_globals()


@pytest.fixture(autouse=True)
def validate_test_isolation():
    """
    Validate no global state leaks between tests.
    
    Captures state before test, verifies reset after test.
    """
    initial = _capture_global_state()
    yield
    _reset_all_globals()
    final = _capture_global_state()
    
    # Verify state was properly reset
    assert final["provider_status_count"] == 0, "Provider state leaked"
    assert final["error_count"] == 0, "Error metrics leaked"
    assert final["user_count"] == 0, "Auth users leaked"


@pytest.fixture
def config():
    """Provide a clean AppConfig for tests."""
    from lattice_lock.config import AppConfig
    return AppConfig()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for tests."""
    from unittest.mock import AsyncMock, MagicMock
    
    client = MagicMock()
    client.chat_completion = AsyncMock(return_value=MagicMock(
        content="Test response",
        model="gpt-4",
        provider="openai",
        usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        function_call=None,
    ))
    return client


@pytest.fixture
def test_user():
    """Create a test user."""
    from lattice_lock.admin.auth import create_user, Role
    return create_user("testuser", "TestPassword123!", Role.ADMIN)


@pytest.fixture
def auth_token(test_user):
    """Create an auth token for test user."""
    from lattice_lock.admin.auth import create_access_token
    return create_access_token(test_user.username, test_user.role)
```

### Task 6.2: Create Infrastructure Validation Tests

Create `tests/test_infrastructure.py`:

```python
"""Tests validating test infrastructure itself."""
import pytest


class TestStateIsolation:
    """Verify test isolation works correctly."""
    
    def test_state_reset_between_tests_1(self):
        """First test that modifies global state."""
        from lattice_lock.errors.middleware import get_metrics, ErrorContext
        
        metrics = get_metrics()
        metrics.record_error(ErrorContext(
            error_type="TestError",
            message="Test message",
        ))
        
        assert metrics.error_counts.get("TestError") == 1
    
    def test_state_reset_between_tests_2(self):
        """Second test verifying state was reset."""
        from lattice_lock.errors.middleware import get_metrics
        
        metrics = get_metrics()
        # Should be 0 because fixture reset state
        assert metrics.error_counts.get("TestError", 0) == 0
    
    def test_provider_state_isolation(self):
        """Verify provider state resets."""
        from lattice_lock.orchestrator.providers.base import ProviderAvailability
        
        # Modify state
        ProviderAvailability._status["test"] = "modified"
        
        # Should be present
        assert "test" in ProviderAvailability._status
    
    def test_provider_state_was_reset(self):
        """Verify previous test's state was reset."""
        from lattice_lock.orchestrator.providers.base import ProviderAvailability
        
        # Should be empty due to fixture
        assert "test" not in ProviderAvailability._status


class TestFixtureAvailability:
    """Verify all fixtures are available."""
    
    def test_config_fixture(self, config):
        assert config is not None
        assert hasattr(config, "analyzer_cache_size")
    
    def test_mock_client_fixture(self, mock_openai_client):
        assert mock_openai_client is not None
        assert hasattr(mock_openai_client, "chat_completion")
```

### Chunk 6 Validation Gate

```bash
# Run tests twice to verify isolation
pytest tests/test_infrastructure.py -v --count=2 -x

# Full test suite
pytest tests/ -v
```

**Rollback Criteria for Chunk 6:**

- [ ] Tests fail when run twice in sequence
- [ ] State isolation tests fail
- [ ] Any test depends on execution order

---

## Work Chunk 7: Cleanup & Final Validation

**Objective:** Remove dead code and perform final integrity checks.

**Risk Level:** Low

### Task 7.1: Delete Dead Code

```bash
# Verify no imports before deleting
grep -r "grok_api" src/ tests/
grep -r "from.*api_clients" src/ tests/
grep -r "from.*scorer import" src/ tests/

# Delete if no imports found
rm -f src/lattice_lock/orchestrator/grok_api.py
# api_clients.py already deleted in Chunk 1
# scorer.py already deleted in Chunk 2
# admin/auth.py already deleted in Chunk 4
```

### Task 7.2: Update Package Exports

Update `src/lattice_lock/orchestrator/__init__.py`:

```python
"""
Lattice Lock Orchestrator Package

Intelligent model orchestration with automatic routing, fallback,
and cost optimization.
"""
from .core import ModelOrchestrator
from .types import TaskType, TaskRequirements, APIResponse, ModelCapabilities
from .providers import get_api_client, ProviderAvailability
from .analysis import TaskAnalyzer, TaskAnalysis
from .scoring import ModelScorer
from .selection import ModelSelector
from .execution import ClientPool, ConversationExecutor

__all__ = [
    # Core
    "ModelOrchestrator",
    # Types
    "TaskType",
    "TaskRequirements",
    "APIResponse",
    "ModelCapabilities",
    # Providers
    "get_api_client",
    "ProviderAvailability",
    # Analysis
    "TaskAnalyzer",
    "TaskAnalysis",
    # Scoring
    "ModelScorer",
    # Selection
    "ModelSelector",
    # Execution
    "ClientPool",
    "ConversationExecutor",
]
```

### Task 7.3: Create System Integration Tests

Create `tests/integration/test_system_integrity.py`:

```python
"""
System-wide integration tests.

Validates end-to-end functionality after refactoring.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestFullRequestLifecycle:
    """Test complete request flow through orchestrator."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_request(self, config):
        """Validate complete request with token aggregation."""
        from lattice_lock.orchestrator import ModelOrchestrator
        
        # Create mock provider response
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_response.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )
        mock_response.function_call = None
        
        with patch(
            "lattice_lock.orchestrator.providers.get_api_client"
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.chat_completion = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client
            
            orchestrator = ModelOrchestrator(config=config)
            
            # This would need actual model registry setup
            # Simplified for example
    
    def test_security_production_gate(self):
        """System must fail with insecure production config."""
        from lattice_lock.exceptions import SecurityConfigurationError
        from lattice_lock.admin.auth import AuthConfig
        
        with patch.dict("os.environ", {
            "LATTICE_ENV": "production",
            "LATTICE_LOCK_SECRET_KEY": "",
        }, clear=True):
            with pytest.raises(SecurityConfigurationError):
                AuthConfig()


class TestComponentInteraction:
    """Test component collaboration."""
    
    def test_analyzer_to_scorer_flow(self, config):
        """TaskAnalyzer output works with ModelScorer."""
        from lattice_lock.orchestrator.analysis import TaskAnalyzer
        from lattice_lock.orchestrator.scoring import ModelScorer
        
        analyzer = TaskAnalyzer(config)
        scorer = ModelScorer(config)
        
        # Analyze a prompt
        requirements = analyzer.analyze("Write a Python function to sort a list")
        
        # Should be compatible with scorer
        assert hasattr(requirements, "task_type")
```

### Task 7.4: Final Dependency Validation

```bash
# Run dependency check
pip install -e ".[dev]"
pip check

# Verify all imports work
python -c "
from lattice_lock.config import AppConfig
from lattice_lock.orchestrator import ModelOrchestrator
from lattice_lock.orchestrator.providers import get_api_client
from lattice_lock.orchestrator.analysis import TaskAnalyzer
from lattice_lock.orchestrator.scoring import ModelScorer
from lattice_lock.orchestrator.selection import ModelSelector
from lattice_lock.orchestrator.execution import ConversationExecutor
from lattice_lock.admin.auth import create_access_token
from lattice_lock.exceptions import BillingIntegrityError
print('✅ All imports successful')
"
```

### Chunk 7 Validation Gate

```bash
# Full test suite
pytest tests/ -v --cov=src --cov-fail-under=80

# Type checking
mypy src/

# Linting
ruff check src/

# Integration tests
pytest tests/integration/ -v

# Final dependency check
pip check
```

**Rollback Criteria for Chunk 7:**

- [ ] Test coverage below 80%
- [ ] Type checking fails
- [ ] Linting errors
- [ ] Any integration test fails

---

## CI/CD Configuration

Create `.github/workflows/refactor-validation.yml`:

```yaml
name: Refactor Validation

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip check
      
      - name: Dependency verification
        run: python scripts/verify_deps.py
      
      - name: Type checking
        run: mypy src/
      
      - name: Linting
        run: ruff check src/ --exit-non-zero-on-fix
      
      - name: Unit tests
        run: pytest tests/ -v --cov=src --cov-fail-under=80
      
      - name: Token aggregation tests (BLOCKING)
        run: pytest tests/execution/test_token_aggregation.py -v --strict-markers
      
      - name: Security tests (BLOCKING)
        run: pytest tests/auth/test_security.py -v --strict-markers
      
      - name: Test isolation validation
        run: pytest tests/ --count=2 -x
      
      - name: Integration tests
        run: pytest tests/integration/ -v
```

---

