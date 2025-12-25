# Deprecation Schedule

This document tracks deprecated APIs and their removal timeline.

## Deprecation Policy

- **Deprecated**: Feature is marked for removal, emits warnings
- **Removal Target**: Version when feature will be removed
- **Migration**: Where to migrate to

---

## Active Deprecations

### Import Paths (Deprecated in v2.1)

| Old Import | New Import | Removal |
|-----------|------------|---------|
| `lattice_lock.orchestrator.api_clients.GrokAPIClient` | Use `get_api_client("xai")` | v3.0 |
| `lattice_lock.orchestrator.api_clients.*` | `lattice_lock.orchestrator.providers.*` (future) | v3.0 |

### Provider Aliases

The following provider aliases are supported for convenience:

| Alias | Canonical Provider |
|-------|-------------------|
| `grok` | `xai` |
| `gemini` | `google` |
| `claude` | `anthropic` |
| `ollama` | `local` |

These aliases are **NOT deprecated** and will continue to work.

---

## Removed in v2.0

| Feature | Replacement |
|---------|-------------|
| `grok_api.py` standalone module | Use `api_clients.GrokAPIClient` |
| Direct provider instantiation without factory | Use `get_api_client()` factory |

---

## Future Deprecations (v3.0 Roadmap)

1. **Provider Architecture**: Monolithic `api_clients.py` will be split into `providers/` package
2. **Config Loading**: Custom config loading will migrate to `config.AppConfig`
3. **Direct Exception Imports**: Migrate to `lattice_lock.errors.types`
