# Configuration Inheritance Patterns

This document describes the inheritance patterns available in the Lattice Lock Framework configuration system.

## Overview

The configuration system uses a mix of single inheritance (`extends`) and composition (`mixins`) to reduce duplication.

### Key Concepts

- **Base Templates**: Abstract configurations that cannot be instantiated directly. Located in `config/inheritance/base/`.
- **Mixins**: reusable configuration fragments that add specific capabilities. Located in `config/inheritance/mixins/`.
- **Inheritance Chain**: `Base -> Mixins -> Concrete Config`.

## Patterns

### 1. The Standard Agent

Use this pattern for most agents.

```yaml
---
extends: base/base_agent.yaml
mixins:
  - mixins/agents/tool_access.yaml
  - mixins/agents/memory_enabled.yaml
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

### 2. The Specialist Agent

For agents with specific capabilities like coding.

```yaml
---
extends: base/base_agent.yaml
mixins:
  - mixins/agents/code_capabilities.yaml
  - mixins/agents/delegation_enabled.yaml
vars:
  sandbox_type: docker
---
agent:
  identity:
    name: coder_agent
  # ...
```

### 3. Model Definition

Defining a specific model instance.

```yaml
---
extends: base/base_model.yaml
mixins:
  - mixins/models/openai_provider.yaml
vars:
  provider: openai
  context: 128000
---
model:
  id: gpt-4o-custom
  parameters:
    temperature: 0.5
```

## Directives

When overriding lists in `mixins` or `extends`, use directives:

- `+append`: Add to the list.
- `+remove`: Remove from the list.
- `+replace`: Replace the list (default behavior, but explicit is better).

Example:
```yaml
tools:
  +append:
    - name: new_tool
```
