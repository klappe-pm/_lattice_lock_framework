# Deprecation Notice: vibelocity-orchestrator

**Effective Date:** 2025-12-01
**Successor Repository:** [Lattice Lock Framework](https://github.com/klappe-pm/lattice-lock-framework)

---

## Summary

The `vibelocity-orchestrator` project has been deprecated and all functionality has been migrated to the **Lattice Lock Framework**. New users should use Lattice Lock Framework directly. Existing users of vibelocity-orchestrator should migrate to Lattice Lock Framework.

---

## Why This Change?

The Lattice Lock Framework represents a significant evolution:

1. **Governance-First Design**: Built-in schema validation, AST analysis (Sheriff), and semantic testing (Gauntlet)
2. **Unified Packaging**: Single package structure with clear import paths (`from lattice_lock import ModelOrchestrator`)
3. **Engineering Framework**: Scaffolding CLI, validation tools, and CI/CD integration
4. **Better Maintenance**: Consolidated codebase with consistent code quality standards

---

## Migration Guide

### Quick Migration

**Before (vibelocity-orchestrator):**
```python
from model_orchestrator import ModelOrchestrator
from model_orchestrator.types import TaskType, ModelCapabilities
```

**After (Lattice Lock Framework):**
```python
from lattice_lock_orchestrator import ModelOrchestrator
from lattice_lock_orchestrator.types import TaskType, ModelCapabilities
```

Or using the public API:
```python
from lattice_lock import ModelOrchestrator
```

### Installation

```bash
# Remove old package
pip uninstall vibelocity-orchestrator

# Install Lattice Lock
pip install lattice-lock
# Or for development:
git clone https://github.com/klappe-pm/lattice-lock-framework
cd lattice-lock-framework
pip install -e .
```

### Import Changes

| Old Import (vibelocity) | New Import (Lattice Lock) |
|-------------------------|---------------------------|
| `from model_orchestrator import *` | `from lattice_lock_orchestrator import *` |
| `from model_orchestrator.types import *` | `from lattice_lock_orchestrator.types import *` |
| `from model_orchestrator_v2 import *` | `from lattice_lock_orchestrator import *` |
| `from zen_mcp_bridge import *` | *Removed* - MCP integration now handled via standard providers |
| `from api_clients import *` | `from lattice_lock_orchestrator.api_clients import *` |

### Configuration Changes

**Old style (`config.yaml`):**
```yaml
provider: openai
model: gpt-4
```

**New style (`lattice.yaml` + environment):**
```yaml
version: "2.0"
entities:
  model_config:
    provider: openai
    model: gpt-4
```

### Feature Mapping

| vibelocity-orchestrator Feature | Lattice Lock Equivalent |
|---------------------------------|-------------------------|
| Model routing | `ModelOrchestrator.route_request()` |
| Provider clients | `lattice_lock_orchestrator.api_clients` |
| Task analysis | `lattice_lock_orchestrator.scorer` |
| CLI tools | `lattice-lock` CLI |
| Concurrent execution | Built into ModelOrchestrator |

---

## Timeline

- **2025-12-01**: Deprecation announced
- **2025-12-31**: Last maintenance releases for vibelocity-orchestrator
- **2026-03-01**: Repository archived (read-only)

---

## Support

For migration assistance:
- Open an issue at [Lattice Lock Framework Issues](https://github.com/klappe-pm/lattice-lock-framework/issues)
- Reference the [Lattice Lock Documentation](https://github.com/klappe-pm/lattice-lock-framework/tree/main/developer_documentation)

---

## Acknowledgments

Thank you to all contributors to vibelocity-orchestrator. Your work forms the foundation of Lattice Lock Framework.
