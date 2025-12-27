# Reset Methods for Test Isolation

All stateful components implement reset functionality to ensure test isolation.

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
```

## Conftest Integration

All reset methods are called automatically via the `reset_global_state` fixture in `tests/conftest.py`.
