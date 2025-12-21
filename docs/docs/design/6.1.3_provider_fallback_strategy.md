# Provider Client and Fallback Strategy Design

**Task ID:** 6.1.3
**Author:** Gemini Antimatter (Design Doc)
**Phase:** 6.1 - Breaking Issues / Orchestrator Contract Hardening
**Dependencies:** 6.1.1 (light dependency)
**Status:** Design Complete
**Date:** 2024-12-10

---

## Executive Summary

The framework declares 7 providers in `ModelProvider` enum but has inconsistent client implementations. `BedrockClient` explicitly raises `NotImplementedError`, and the factory function is missing mappings for `azure` and `bedrock`. This document defines provider maturity tiers, fallback behavior, and a migration strategy.

---

## 1. Provider Maturity Classification

### 1.1 Tier Definitions

| Tier | Definition | User Expectation | SLA |
|------|------------|------------------|-----|
| **Production** | Fully implemented, tested, documented | Works reliably in production | 99.9% success rate |
| **Beta** | Implemented but limited testing | May have edge cases | 95% success rate |
| **Experimental** | Partially implemented, known limitations | Use at own risk | No SLA |
| **Planned** | Not implemented, raises errors | Will fail at runtime | N/A |

### 1.2 Current Provider Classification

| Provider | Client Class | Tier | Rationale |
|----------|--------------|------|-----------|
| **OpenAI** | `OpenAIAPIClient` | Production | Full implementation, function calling, well-tested |
| **Anthropic** | `AnthropicAPIClient` | Production | Full implementation, DIAL support, function calling |
| **Google** | `GoogleAPIClient` | Beta | Implemented but Gemini API has nuances |
| **xAI (Grok)** | `GrokAPIClient` | Beta | Full implementation, streaming, newer provider |
| **Ollama** | `LocalModelClient` | Beta | Works but fallback to legacy API, no function calling guarantee |
| **Azure** | `AzureOpenAIClient` | Experimental | Implemented but NOT in factory, deployment-specific |
| **Bedrock** | `BedrockAPIClient` | Planned | Explicitly raises `NotImplementedError` |
| **DIAL** | `AnthropicAPIClient` | Experimental | Wrapper mode, endpoint configurable |

### 1.3 Factory Function Gap Analysis

**Current `get_api_client()` mappings (api_clients.py:641-656):**
```python
clients = {
    'xai': GrokAPIClient,
    'openai': OpenAIAPIClient,
    'google': GoogleAPIClient,
    'anthropic': AnthropicAPIClient,
    'dial': lambda: AnthropicAPIClient(use_dial=True),
    'local': LocalModelClient,
}
```

**Missing mappings:**
- `azure` → `AzureOpenAIClient` (class exists but not in factory)
- `bedrock` → `BedrockAPIClient` (class exists but raises NotImplementedError)
- `ollama` → `LocalModelClient` (enum uses "ollama", factory uses "local")

---

## 2. Bedrock Decision

### 2.1 Options Analysis

| Option | Pros | Cons | Effort |
|--------|------|------|--------|
| **A: Implement minimal client** | Full functionality | Requires boto3, AWS auth complexity | 2-3 days |
| **B: Experimental + feature flag** | Honest about status | Still fails at runtime without flag | 1 day |
| **C: Remove from registry** | Clean, no runtime errors | Reduces claimed model count | 2 hours |

### 2.2 Recommendation: Option B - Experimental with Feature Flag

**Rationale:**
1. **Honest Status**: Users know Bedrock is experimental before encountering errors
2. **Preserves Roadmap**: Bedrock models remain in registry for future implementation
3. **Graceful Degradation**: Fails fast with clear error message, not cryptic `NotImplementedError`
4. **Low Effort**: Can be implemented quickly while proper boto3 integration is planned

**Implementation:**
```python
# In api_clients.py
class BedrockAPIClient(BaseAPIClient):
    def __init__(self, region: str = "us-east-1"):
        if not os.getenv('LATTICE_ENABLE_EXPERIMENTAL_BEDROCK'):
            raise ProviderNotAvailableError(
                "Bedrock is experimental. Set LATTICE_ENABLE_EXPERIMENTAL_BEDROCK=1 to enable."
            )
        # ... existing init
```

---

## 3. Required Environment Variables

### 3.1 Provider Credential Matrix

| Provider | Required Variables | Optional Variables |
|----------|-------------------|-------------------|
| **OpenAI** | `OPENAI_API_KEY` | `OPENAI_ORG_ID` |
| **Anthropic** | `ANTHROPIC_API_KEY` | - |
| **Google** | `GOOGLE_API_KEY` | `GOOGLE_PROJECT_ID` |
| **xAI** | `XAI_API_KEY` | - |
| **Ollama** | - | `CUSTOM_API_URL` (default: `localhost:11434`) |
| **Azure** | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` | `AZURE_OPENAI_API_VERSION` |
| **Bedrock** | AWS credentials (via boto3/env) | `AWS_REGION` |
| **DIAL** | `DIAL_API_KEY` | `DIAL_ENDPOINT` |

### 3.2 Validation Behavior

**Current Behavior:** Clients raise `ValueError` on missing credentials at instantiation.

**Recommended Behavior:**

```python
class ProviderNotConfiguredError(Exception):
    """Raised when provider credentials are missing."""
    def __init__(self, provider: str, missing_vars: List[str]):
        self.provider = provider
        self.missing_vars = missing_vars
        super().__init__(
            f"Provider '{provider}' not configured. "
            f"Missing environment variables: {', '.join(missing_vars)}"
        )

class ProviderNotAvailableError(Exception):
    """Raised when provider is not available (experimental, disabled, etc)."""
    pass
```

### 3.3 Error Messages

| Scenario | Error Type | Message |
|----------|------------|---------|
| Missing API key | `ProviderNotConfiguredError` | "Provider 'openai' not configured. Missing: OPENAI_API_KEY" |
| Experimental disabled | `ProviderNotAvailableError` | "Bedrock is experimental. Set LATTICE_ENABLE_EXPERIMENTAL_BEDROCK=1" |
| Provider unavailable | `ProviderNotAvailableError` | "Provider 'bedrock' is not available in this version" |
| Network error | `ProviderConnectionError` | "Failed to connect to provider 'openai': Connection timeout" |

---

## 4. Fallback Behavior

### 4.1 Current Fallback Logic (core.py:198-231)

```
1. Primary model fails → Log error
2. Get fallback chain from guide for task type
3. If no chain: Score all models, try top 3
4. Try each fallback model until success
5. If all fail: Raise RuntimeError("All fallback models failed")
```

### 4.2 Recommended Fallback Strategy

#### 4.2.1 Provider Availability Check

**Before model selection**, verify provider is available:

```python
def _is_provider_available(self, provider: str) -> bool:
    """Check if provider is configured and available."""
    try:
        client = self._get_client(provider)
        return True
    except (ProviderNotConfiguredError, ProviderNotAvailableError):
        return False
```

#### 4.2.2 Filter Unavailable Providers from Selection

```python
def _select_best_model(self, requirements: TaskRequirements) -> Optional[str]:
    # ... existing logic ...

    for model in self.registry.get_all_models():
        # Skip if provider not available
        if not self._is_provider_available(model.provider.value):
            logger.debug(f"Skipping {model.api_name}: provider {model.provider.value} not available")
            continue

        # ... rest of scoring logic ...
```

#### 4.2.3 Fallback Chain with Provider Awareness

| Scenario | Behavior |
|----------|----------|
| Primary model fails (API error) | Try fallback chain, skip unavailable providers |
| Primary model fails (missing credentials) | Skip to next provider in chain |
| All configured providers fail | Raise clear error with available options |
| No providers configured | Raise `NoProvidersAvailableError` |

#### 4.2.4 Silent Skip vs Hard Fail

**Recommendation: Silent skip for unavailable, hard fail for errors**

| Condition | Behavior |
|-----------|----------|
| Provider not configured (missing env vars) | Silent skip, log at DEBUG |
| Provider experimental and disabled | Silent skip, log at INFO |
| Provider returns API error (rate limit, etc) | Retry then fallback |
| Provider returns auth error | Hard fail (credentials invalid) |
| Network timeout | Retry with backoff, then fallback |

---

## 5. Provider Health Checks

### 5.1 Startup Health Check

```python
class ProviderHealthChecker:
    """Check provider availability at startup."""

    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self._health_cache: Dict[str, HealthStatus] = {}
        self._cache_ttl = 300  # 5 minutes

    async def check_all_providers(self) -> Dict[str, HealthStatus]:
        """Check health of all providers."""
        providers = set(m.provider.value for m in self.registry.get_all_models())

        results = {}
        for provider in providers:
            results[provider] = await self._check_provider(provider)

        return results

    async def _check_provider(self, provider: str) -> HealthStatus:
        """Check single provider health."""
        try:
            client = get_api_client(provider)
            # Minimal validation - just check we can instantiate
            return HealthStatus(
                provider=provider,
                available=True,
                tier=get_provider_tier(provider),
                message="Configured and available"
            )
        except ProviderNotConfiguredError as e:
            return HealthStatus(
                provider=provider,
                available=False,
                tier=get_provider_tier(provider),
                message=f"Not configured: {e.missing_vars}"
            )
        except ProviderNotAvailableError as e:
            return HealthStatus(
                provider=provider,
                available=False,
                tier="planned",
                message=str(e)
            )
```

### 5.2 Caching Strategy

| Cache Key | TTL | Invalidation |
|-----------|-----|--------------|
| Provider availability | 5 minutes | On credential change, manual refresh |
| Provider health status | 1 minute | On API error, manual refresh |
| Rate limit status | Until reset time | On rate limit response |

### 5.3 Retry Behavior for Transient Failures

**Current:** `tenacity` retry with 3 attempts, exponential backoff (2-10s)

**Recommended Enhancement:**

```python
RETRY_CONFIG = {
    "rate_limit": {
        "max_attempts": 5,
        "wait": "exponential",
        "max_wait": 60,
        "jitter": True
    },
    "network_error": {
        "max_attempts": 3,
        "wait": "exponential",
        "max_wait": 10,
        "jitter": True
    },
    "server_error": {
        "max_attempts": 2,
        "wait": "fixed",
        "wait_time": 5
    }
}
```

---

## 6. Implementation Tasks for Devin AI

### Task 6.1.4: Provider Hardening

**Priority:** High

#### 6.1 Add Custom Exceptions

**File:** `src/lattice_lock_orchestrator/exceptions.py` (new file)

```python
class LatticeOrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    pass

class ProviderNotConfiguredError(LatticeOrchestratorError):
    """Provider credentials missing."""
    def __init__(self, provider: str, missing_vars: List[str]):
        self.provider = provider
        self.missing_vars = missing_vars
        super().__init__(
            f"Provider '{provider}' not configured. "
            f"Missing environment variables: {', '.join(missing_vars)}"
        )

class ProviderNotAvailableError(LatticeOrchestratorError):
    """Provider not available (experimental, disabled, etc)."""
    pass

class NoProvidersAvailableError(LatticeOrchestratorError):
    """No providers are configured."""
    pass

class ProviderConnectionError(LatticeOrchestratorError):
    """Failed to connect to provider."""
    pass
```

#### 6.2 Update Factory Function

**File:** `src/lattice_lock_orchestrator/api_clients.py`

1. Add missing provider mappings:
   ```python
   clients = {
       'xai': GrokAPIClient,
       'openai': OpenAIAPIClient,
       'google': GoogleAPIClient,
       'anthropic': AnthropicAPIClient,
       'dial': lambda: AnthropicAPIClient(use_dial=True),
       'local': LocalModelClient,
       'ollama': LocalModelClient,  # ADD: alias for enum value
       'azure': AzureOpenAIClient,  # ADD: was missing
       'bedrock': BedrockAPIClient, # ADD: will raise if experimental disabled
   }
   ```

2. Add experimental feature flag check to `BedrockAPIClient.__init__`:
   ```python
   def __init__(self, region: str = "us-east-1"):
       if not os.getenv('LATTICE_ENABLE_EXPERIMENTAL_BEDROCK'):
           raise ProviderNotAvailableError(
               "Bedrock is experimental. Set LATTICE_ENABLE_EXPERIMENTAL_BEDROCK=1 to enable."
           )
       # ... rest of init
   ```

#### 6.3 Update ModelOrchestrator

**File:** `src/lattice_lock_orchestrator/core.py`

1. Add provider availability check method:
   ```python
   def _is_provider_available(self, provider: str) -> bool:
       """Check if provider is configured and available."""
       try:
           self._get_client(provider)
           return True
       except (ProviderNotConfiguredError, ProviderNotAvailableError):
           return False
   ```

2. Update `_select_best_model` to filter unavailable providers

3. Update `_handle_fallback` to skip unavailable providers

#### 6.4 Add Provider Maturity Metadata

**File:** `src/lattice_lock_orchestrator/types.py`

```python
class ProviderTier(Enum):
    PRODUCTION = "production"
    BETA = "beta"
    EXPERIMENTAL = "experimental"
    PLANNED = "planned"

PROVIDER_TIERS: Dict[str, ProviderTier] = {
    "openai": ProviderTier.PRODUCTION,
    "anthropic": ProviderTier.PRODUCTION,
    "google": ProviderTier.BETA,
    "xai": ProviderTier.BETA,
    "ollama": ProviderTier.BETA,
    "azure": ProviderTier.EXPERIMENTAL,
    "bedrock": ProviderTier.PLANNED,
    "dial": ProviderTier.EXPERIMENTAL,
}
```

#### 6.5 Write Tests

**File:** `tests/test_provider_fallback.py` (new file)

```python
import pytest
from unittest.mock import patch, MagicMock
from lattice_lock_orchestrator.api_clients import get_api_client
from lattice_lock_orchestrator.exceptions import (
    ProviderNotConfiguredError,
    ProviderNotAvailableError
)

def test_missing_openai_key_raises_not_configured():
    """Test that missing OPENAI_API_KEY raises ProviderNotConfiguredError."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ProviderNotConfiguredError) as exc:
            get_api_client('openai')
        assert 'OPENAI_API_KEY' in exc.value.missing_vars

def test_bedrock_experimental_disabled():
    """Test that Bedrock raises when experimental flag not set."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ProviderNotAvailableError) as exc:
            get_api_client('bedrock')
        assert 'experimental' in str(exc.value).lower()

def test_bedrock_experimental_enabled():
    """Test that Bedrock can be instantiated with flag."""
    with patch.dict('os.environ', {'LATTICE_ENABLE_EXPERIMENTAL_BEDROCK': '1'}):
        # Should not raise ProviderNotAvailableError
        # (will still raise NotImplementedError on _call_api, which is expected)
        client = get_api_client('bedrock')
        assert client is not None

def test_factory_includes_azure():
    """Test that azure is in factory mapping."""
    with patch.dict('os.environ', {
        'AZURE_OPENAI_API_KEY': 'test',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com'
    }):
        client = get_api_client('azure')
        assert client is not None

def test_ollama_alias():
    """Test that 'ollama' maps to LocalModelClient."""
    client = get_api_client('ollama')
    assert client is not None
```

#### 6.6 Update Documentation

**File:** `docs/providers.md` (new file)

Document:
- Provider tiers and what they mean
- Required environment variables per provider
- How to enable experimental providers
- Fallback behavior explanation

---

## 7. Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bedrock handling | Experimental + feature flag | Preserves roadmap, fails gracefully |
| Missing credentials | Silent skip in selection | Allows partial provider configuration |
| API errors | Retry then fallback | Resilience to transient failures |
| Factory gaps | Add azure, bedrock, ollama alias | Complete enum coverage |
| Health checks | Startup + cached | Fast selection, avoids repeated failures |

**Files to Create:**
1. `src/lattice_lock_orchestrator/exceptions.py` - Custom exceptions
2. `tests/test_provider_fallback.py` - Fallback tests
3. `docs/providers.md` - Provider documentation

**Files to Modify:**
1. `src/lattice_lock_orchestrator/api_clients.py` - Factory + Bedrock flag
2. `src/lattice_lock_orchestrator/core.py` - Provider availability checks
3. `src/lattice_lock_orchestrator/types.py` - ProviderTier enum

**Estimated Implementation Time:** 4-6 hours
