# Deprecation Notice

This document lists deprecated modules and APIs in the Lattice Lock Framework. Deprecated items will be removed in v2.0.

---

## Deprecated Modules

### `lattice_lock.orchestrator.api_clients`
**Deprecated since:** v1.x
**Use instead:** `lattice_lock.orchestrator.providers`

```python
# OLD (deprecated)
from lattice_lock.orchestrator.api_clients import OpenAIAPIClient, get_api_client

# NEW
from lattice_lock.orchestrator.providers import OpenAIAPIClient, get_api_client
```

---

### `lattice_lock.orchestrator.scorer`
**Deprecated since:** v1.x
**Use instead:** `lattice_lock.orchestrator.analysis` and `lattice_lock.orchestrator.scoring`

```python
# OLD (deprecated)
from lattice_lock.orchestrator.scorer import TaskAnalyzer, ModelScorer

# NEW
from lattice_lock.orchestrator.analysis import TaskAnalyzer
from lattice_lock.orchestrator.scoring import ModelScorer
```

---

## Deprecated Aliases

| Old Name | New Name | Module |
|----------|----------|--------|
| `GrokAPIClient` | `XAIAPIClient` | `providers` |

---

## Migration Guide

1. Search for deprecated imports in your codebase
2. Replace with new import paths
3. Run tests to verify functionality
4. Enable deprecation warnings: `python -W default::DeprecationWarning`
