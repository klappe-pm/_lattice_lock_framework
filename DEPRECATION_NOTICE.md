# Vibelocity Orchestrator Deprecation Notice

> **This document is intended to be placed in the vibelocity-orchestrator repository.**

---

## DEPRECATED

**This repository (`vibelocity-orchestrator`) is deprecated and no longer actively maintained.**

All functionality has been migrated to the [Lattice Lock Framework](https://github.com/klappe-pm/lattice-lock-framework).

---

## Migration Guide

### For New Projects

Use Lattice Lock Framework directly:

```bash
pip install lattice-lock
```

```python
from lattice_lock import ModelOrchestrator, TaskType

orchestrator = ModelOrchestrator()
response = await orchestrator.route_request(
    prompt="Your prompt here",
    task_type=TaskType.CODE_GENERATION
)
```

### For Existing Projects

1. **Update your dependencies:**

   Replace:
   ```
   vibelocity-orchestrator
   ```

   With:
   ```
   lattice-lock
   ```

2. **Update your imports:**

   | Old Import | New Import |
   |------------|------------|
   | `from model_orchestrator import ...` | `from lattice_lock import ...` |
   | `from vibelocity_orchestrator import ...` | `from lattice_lock import ...` |
   | `from model_orchestrator.types import ...` | `from lattice_lock.types import ...` |

3. **API Changes:**

   Most APIs are backwards compatible. Key changes:

   - `ModelOrchestrator` is now imported from `lattice_lock`
   - Type definitions are in `lattice_lock.types`
   - Registry is accessible via `lattice_lock.ModelRegistry`

### Feature Mapping

| Vibelocity Feature | Lattice Lock Equivalent |
|--------------------|------------------------|
| Model routing | `ModelOrchestrator.route_request()` |
| Cost estimation | `ModelScorer.estimate_cost()` |
| Task analysis | `TaskAnalyzer.analyze()` |
| Model registry | `ModelRegistry` |
| Consensus groups | Coming in v2.2 |

---

## Timeline

- **2025-12-01**: Final vibelocity-orchestrator release
- **2025-12-01**: Lattice Lock Framework v2.1 released (migration complete)
- **2026-06-01**: vibelocity-orchestrator archived (read-only)

---

## Getting Help

- **Documentation**: [Lattice Lock Docs](https://github.com/klappe-pm/lattice-lock-framework/tree/main/developer_documentation)
- **Issues**: [Lattice Lock Issues](https://github.com/klappe-pm/lattice-lock-framework/issues)
- **Migration Questions**: Open an issue with the `migration` label

---

## Why the Migration?

The Lattice Lock Framework provides:

1. **Governance-First Architecture**: Built-in validation and policy enforcement
2. **Extended Model Support**: 63+ models from 8 providers
3. **Better Tooling**: Sheriff AST validator, compile-time schema validation
4. **Active Development**: Regular updates and community support
5. **Enterprise Features**: Rollback support, audit logging, cost telemetry

---

*Last updated: 2024-12-14*
