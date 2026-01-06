# Configuration Inheritance Patterns

This document describes the inheritance patterns available in the Lattice Lock Framework configuration system.

## Overview

The configuration system uses a mix of single inheritance (`extends`) and composition (`mixins`) to reduce duplication.

### Key Concepts

- **Base Templates**: Abstract configurations in `config/inheritance/base/`
- **Mixins**: Reusable configuration fragments in `config/inheritance/mixins/`
- **Inheritance Chain**: `Base -> Mixins -> Concrete Config`

## Example Usage

```yaml
---
extends: base/base_agent.yaml
mixins:
  - mixins/agents/code_capabilities.yaml
  - mixins/agents/delegation_enabled.yaml
vars:
  version: 1.0.0
---
agent:
  identity:
    name: my_agent
    description: "My Agent"
  directive:
    primary_goal: "Help user"
```

## Directives

- `+append`: Add items to a list
- `+remove`: Remove items from a list
- `+replace`: Replace the list entirely
