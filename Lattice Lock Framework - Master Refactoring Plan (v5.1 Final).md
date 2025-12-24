
**Execution Protocol:**

- **Critical Path:** Chunk 0 → Chunk 1 → Chunk 2 → Chunk 3 → Chunk 4 → Chunk 5 → Chunk 6 → Chunk 7.
    
- **Rationale:** Chunk 3 (`ModelOrchestrator` decomposition) depends on `ModelScorer` being migrated in Chunk 2.
    

---

# Lattice Lock Framework - Master Refactoring Plan (v5.1 Final)

## Initiative 1: Core Framework Refactoring

**Objective:** Decompose the monolithic codebase into a modular, maintainable, and testable architecture.

### Work Chunk 0: Prerequisites, Configuration & Standards

**Objective:** Establish the foundation for refactoring by securing dependencies, defining logging standards, creating custom exceptions, and finalizing the configuration loader.

#### LLM Prompt

Python

````
You are preparing the Lattice Lock Framework for a major refactoring.

## Task 1: Update Dependencies
Update `pyproject.toml` (or `requirements.txt`) to include these specific versions. **Do this first** to ensure availability for later chunks.

```toml
[project.dependencies]
# ... existing dependencies ...
PyYAML >= 6.0        # For Task Analysis patterns (Work Chunk 2)
PyJWT >= 2.8.0       # Replaces python-jose (Work Chunk 4)
bcrypt >= 4.0.0      # For password hashing (Work Chunk 4)
````

**Explicitly Remove:** `python-jose` (if present) to prevent confusion.

## Task 2: Create Custom Exception Classes

Create `src/lattice_lock/exceptions.py`:

Python

```
"""Framework-wide custom exceptions."""

class LatticeError(Exception):
    """Base exception for Lattice Lock framework."""
    pass

class BillingIntegrityError(LatticeError):
    """Token aggregation or billing data corruption detected."""
    pass

class SecurityConfigurationError(LatticeError):
    """Security requirements not met for current environment."""
    pass

class BackgroundTaskError(LatticeError):
    """Background task failed to complete within timeout."""
    pass

class ProviderUnavailableError(LatticeError):
    """Provider credentials missing or provider unreachable."""
    pass
```

## Task 3: Define Logging Standards

Create `src/lattice_lock/utils/logging.py`:

Python

```
"""Logging configuration and standards."""
import logging
import re

LOG_LEVELS = {
    "cache_hit": logging.DEBUG,
    "model_selection": logging.INFO,
    "provider_failover": logging.WARNING,
    "security_violation": logging.CRITICAL,
    "billing_integrity": logging.CRITICAL,
}

# Patterns to redact from logs
REDACT_PATTERNS = [
    re.compile(r"(api[_-]?key[\"']?\s*[:=]\s*[\"']?)([^\"'\s]+)", re.I),
    re.compile(r"(secret[_-]?key[\"']?\s*[:=]\s*[\"']?)([^\"'\s]+)", re.I),
    re.compile(r"(bearer\s+)([^\s]+)", re.I),
]

def redact_sensitive(message: str) -> str:
    """Redact sensitive data from log messages."""
    for pattern in REDACT_PATTERNS:
        message = pattern.sub(r"\1[REDACTED]", message)
    return message

def get_logger(name: str) -> logging.Logger:
    """Get a logger with standard configuration."""
    return logging.getLogger(name)
```

## Task 4: Central Configuration Loader

Create `src/lattice_lock/config/app_config.py` with expanded fields.

Python

```
"""
Central Application Configuration.
Aggregates specific configs from Auth, Analysis, and Execution modules.
"""
import os
from typing import Optional

class AppConfig:
    def __init__(self):
        self.env = os.environ.get("LATTICE_ENV", "dev")
        
        # Analyzer Configuration
        self.analyzer_cache_size: int = int(os.environ.get("ANALYZER_CACHE_SIZE", 1024))
        
        # Executor Configuration
        self.max_function_calls: int = int(os.environ.get("MAX_FUNCTION_CALLS", 10))
        self.background_task_timeout: float = float(os.environ.get("BACKGROUND_TASK_TIMEOUT", "5.0"))
        
        # Auth Configuration
        self.token_expiry_minutes: int = int(os.environ.get("TOKEN_EXPIRY_MINUTES", 30))
        
        # Security Configuration
        self.jwt_algorithm = "HS256"
        self.secret_key = os.environ.get("LATTICE_LOCK_SECRET_KEY")

        # Validation logic for production security
        if self.env == "production" and not self.secret_key:
             raise ValueError("LATTICE_LOCK_SECRET_KEY must be set in production")

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from environment."""
        return cls()
```

````

---

### Work Chunk 1: Provider Architecture Unification

**Objective:** Split `api_clients.py` into a clean `providers/` package with strict circular import management.

#### LLM Prompt

```python
You are refactoring the Lattice Lock Framework.

## Context
The file `src/lattice_lock/orchestrator/api_clients.py` is a monolithic module.

## Plan

### Step 1: Create package structure
Create `src/lattice_lock/orchestrator/providers/` containing:
- `__init__.py`
- `base.py`
- `openai.py`, `anthropic.py`, `google.py`, `xai.py`, `azure.py`, `bedrock.py`, `local.py`, `dial.py`
- `factory.py`

### Step 2: Extract base.py
Move `BaseAPIClient`, `ProviderAvailability`, `ProviderStatus`, and `ProviderUnavailableError` here.
Ensure `BaseAPIClient` defines the abstract interface:

```python
class BaseAPIClient(ABC):
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify provider connectivity and credential validity.
        Implementation Requirements:
        - Verify API credentials are valid (not just present)
        - Confirm provider endpoint is reachable
        - Cache results for max 60 seconds
        - Must not consume significant billable quota
        """
        pass
    
    @abstractmethod
    async def chat_completion(self, ...): pass
````

### Step 3: Extract Providers (Relative Imports & Logging)

For each provider file (e.g., `openai.py`):

1. Move the relevant client class.
    
2. **CRITICAL:** Use relative imports: `from .base import BaseAPIClient`.
    
3. **STANDARD:** Set up logging: `logger = logging.getLogger(__name__)`.
    

### Step 4: Factory & Aliasing

Move `get_api_client` to `factory.py`.

- Ensure "grok" string maps to `XAIAPIClient`.
    
- Ensure "gemini" string maps to `GoogleAPIClient`.
    

### Step 5: Shim with Explicit Aliasing

Replace `src/lattice_lock/orchestrator/api_clients.py` with:

Python

```
"""
DEPRECATED: Import from lattice_lock.orchestrator.providers instead.
"""
import warnings
from .providers import (
    BaseAPIClient, OpenAIAPIClient, # ... others
    XAIAPIClient,
    get_api_client
)

# Preserve old alias for backward compatibility explicitly
GrokAPIClient = XAIAPIClient 

warnings.warn(
    "Importing from api_clients is deprecated. Use lattice_lock.orchestrator.providers instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "BaseAPIClient", "OpenAIAPIClient", "GrokAPIClient", "XAIAPIClient", # ... all others
]
```

````

---

### Work Chunk 2: Task Analysis & Scoring Migration

**Objective:** Separate data from logic, optimize regex performance, and migrate ModelScorer.

#### LLM Prompt

```python
You are refactoring the Task Analysis module.

## Plan

### Step 1: Externalize Patterns
Create `src/lattice_lock/orchestrator/analysis/patterns.yaml`. Move all `KEYWORD_PATTERNS` and `REGEX_PATTERNS` here.

### Step 2: Create `analysis/analyzer.py`
Refactor `TaskAnalyzer` to use **pre-compiled regexes** and handle missing PyYAML.

```python
import re
from pathlib import Path
from typing import Optional

class TaskAnalyzer:
    def __init__(self, patterns_path: Path | None = None, cache_size: int = 1024):
        self._cache = {} 
        self._cache_size = cache_size
        self._regex_patterns = self._load_and_compile(patterns_path)

    def _load_and_compile(self, path: Path | None) -> dict:
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required. Install 'PyYAML>=6.0'")
            
        # Load YAML safely and pre-compile regexes immediately
        pass

    def reset_cache(self) -> None:
        """Clear analysis cache for testing."""
        self._cache.clear()
````

### Step 3: Extract `analysis/semantic_router.py`

Move `SemanticRouter` to its own file.

### Step 4: Extract `ModelScorer`

Create src/lattice_lock/orchestrator/scoring/model_scorer.py.

Move the ModelScorer class from scorer.py to here.

Create src/lattice_lock/orchestrator/scoring/__init__.py exporting it.

### Step 5: Shim `scorer.py`

Replace `scorer.py` with a re-export shim for `TaskAnalyzer`, `SemanticRouter`, and `ModelScorer`.

````

---

### Work Chunk 3: Model Orchestrator Decomposition

**Objective:** Split the orchestrator, implement ModelSelector, and ensure billing/tracing integrity.

#### LLM Prompt

```python
You are refactoring the Model Orchestrator.

## Plan

### Step 1: Create `selection/model_selector.py`
Create `ModelSelector` class that utilizes `ModelScorer` (from Chunk 2), `ModelRegistry`, and `ModelGuideParser`.
* Implement `select_best_model(requirements)`.
* Implement `get_fallback_chain(requirements)`.

### Step 2: Create `execution/conversation.py`
Implement `ConversationExecutor` with **Token Aggregation** and **Tracing**.

```python
from lattice_lock.tracing import AsyncSpanContext, get_current_trace_id

class ConversationExecutor:
    async def execute(self, client, model, messages, trace_id: str | None = None, **kwargs) -> APIResponse:
        request_trace_id = trace_id or get_current_trace_id()
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        async with AsyncSpanContext("conversation_execute", trace_id=request_trace_id):
            while function_call_count < self.max_function_calls:
                response = await client.chat_completion(...)
                
                # CRITICAL: AGGREGATE USAGE
                if response.usage:
                    total_usage["prompt_tokens"] += response.usage.get("prompt_tokens", 0)
                    total_usage["completion_tokens"] += response.usage.get("completion_tokens", 0)
                    total_usage["total_tokens"] += response.usage.get("total_tokens", 0)
                
                if not response.function_call:
                    response.usage = total_usage
                    return response
                
                # ... handle function execution ...
        return response
````

### Step 3: Create `execution/client_pool.py`

Move lazy-loading client logic here. Implement `close_all()` and `reset()`.

### Step 4: Refactor `ModelOrchestrator` (core.py)

Rewrite the class to coordinate `ClientPool`, `ModelSelector`, and `ConversationExecutor`.

````

---

### Work Chunk 4: Admin Auth (Security & Storage Protocol)

**Objective:** Modernize Auth with `PyJWT` and abstract storage.

#### LLM Prompt

```python
You are refactoring the Admin Auth module.

## Plan

### Step 1: Secure Configuration (`auth/config.py`)
Implement `AuthConfig` using `src/lattice_lock/config/app_config.py` logic or Pydantic models with strict production validation.

### Step 2: Storage Abstraction (`auth/storage.py`)
Define `AuthStorage` Protocol explicitly.

```python
from typing import Protocol
class AuthStorage(Protocol):
    def get_user(self, username: str) -> User | None: ...
    def create_user(self, user: User) -> None: ...
    def clear_all(self) -> None: ... 
    # ... other methods ...

class InMemoryAuthStorage:
    # Implement protocol
    def clear_all(self):
        self._users.clear()
        self._revoked_tokens.clear()
        self._api_keys.clear()
````

### Step 3: Switch to PyJWT (`auth/tokens.py`)

Implement `create_access_token` and `verify_token` using `import jwt`.

### Step 4: Password Hashing (`auth/passwords.py`)

Use `bcrypt`.

### Step 5: Exports & Shim

Create `auth/__init__.py` and legacy shim at `admin/auth.py`.

````

---

### Work Chunk 5: Error Middleware & Async Compatibility

**Objective:** Reliable background tasks and unified error handling.

#### LLM Prompt

```python
You are fixing Error Middleware and Background Tasks.

## Plan

### Step 1: Create `utils/async_compat.py`
Implement `BackgroundTaskQueue` and `error_boundary` deduplication.

```python
def error_boundary(...):
    """Decorator with unified sync/async error handling logic."""
    # Extract shared retry logic to avoid code duplication
    # ... implementation ...
````

### Step 2: Update Error Middleware

In `ErrorMetrics.record_error`, use `get_background_queue().enqueue(...)`.

### Step 3: Update Application Lifespan

In the main FastAPI app file:

Python

```
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await get_background_queue().wait_all()
```

````

---

### Work Chunk 6: Testing Infrastructure & Isolation

**Objective:** Eliminate test pollution via strict global resets.

#### LLM Prompt

```python
You are standardizing the Testing Infrastructure.

## Plan

### Step 1: Implement Reset Methods
Ensure these methods exist:
1.  `ProviderAvailability.reset()`
2.  `AuthStorage.clear_all()`
3.  `ClientPool.reset()`
4.  `TaskAnalyzer.reset_cache()`
5.  `ErrorMetrics.reset_metrics()`

### Step 2: Update `conftest.py` with Isolation Validation
Update `tests/conftest.py`:

```python
def _capture_global_state() -> dict:
    # Capture counts of providers, errors, users to ensure 0
    pass

@pytest.fixture(autouse=True)
def isolation():
    from lattice_lock.tracing import reset_performance_metrics
    
    # Reset Before
    reset_all_globals()
    reset_performance_metrics()
    
    yield
    
    # Reset After
    reset_all_globals()
    reset_performance_metrics()
    
    # Validation
    state = _capture_global_state()
    assert state["error_count"] == 0 # etc...
````

````

---

### Work Chunk 7: Cleanup & Deprecation

**Objective:** Finalize the transition.

#### LLM Prompt

```python
Final Cleanup.

## Task 1: Delete Dead Code
Remove `orchestrator/grok_api.py` (check for imports first).

## Task 2: Create `DEPRECATIONS.md`
Track removal timeline (v2.2 deprecated -> v3.0 removal).

## Task 3: Test Shims
Verify that all shim files emit `DeprecationWarning`.
````

---

## Initiative 2: Test Suite Refactoring

**Objective:** Adapt the existing test suite to the new modular architecture.

### Work Chunk 2.1: Update Existing Test Imports

- Update `test_api_clients.py` to target `lattice_lock.orchestrator.providers`.
    
- Update `test_orchestrator.py` to mock `TaskAnalyzer`, `ModelSelector`, `ConversationExecutor`.
    

### Work Chunk 2.2: Expand Unit Testing

- **Token Aggregation:** Create `tests/execution/test_token_aggregation.py` to verify `ConversationExecutor` sums usage correctly.
    
- **Selector:** Create `tests/selection/test_selector.py`.
    

### Work Chunk 2.3: CI/CD Validation

- Configure CI to run `pytest tests/execution/test_token_aggregation.py -v --strict-markers` as a blocking step.
    
- Configure CI to run `pytest tests/ --count=2 -x` to catch state leaks.