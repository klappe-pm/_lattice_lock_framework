---
title: readme
type: index
status: stable
categories: [concepts, reference]
sub_categories: [index]
date_created: 2026-01-31
date_revised: 2026-01-31
file_ids: [concepts-index-001]
tags: [concepts, index, architecture, models, governance]
---

# Core Concepts

This section explains the fundamental concepts behind Lattice Lock.

## Contents

| Document | Description |
|----------|-------------|
| [Components](./components.md) | Overview of Lattice Lock components |
| [Features](./features.md) | Key features and capabilities |
| [Governance](./governance.md) | Schema governance and enforcement |
| [Model Orchestration](./model_orchestration.md) | How AI models are selected and used |
| [Model Orchestrator Components](./model_orchestrator_components_descriptions.md) | Detailed orchestrator architecture |
| [Models](./models.md) | Supported AI models and providers |
| [Multi-Project](./multi_project.md) | Managing multiple projects |

## Key Concepts

### Schema-First Development

Lattice Lock uses a schema-first approach where your `lattice.yaml` file is the single source of truth. All code generation, validation, and testing flows from this schema.

### Contract Testing

Generated test contracts ensure your implementation matches your schema. This provides confidence that your code behaves as specified.

### Model Orchestration

The Model Orchestrator intelligently selects AI models based on task requirements, balancing quality, cost, and speed.

## Learning Path

1. Start with [Features](./features.md) for an overview
2. Understand [Governance](./governance.md) for quality enforcement
3. Learn [Model Orchestration](./model_orchestration.md) for AI-powered features

## Related Documentation

- [Guides](../guides/) - Practical how-to guides
- [Reference](../reference/) - Technical specifications
- [Advanced](../advanced/) - Advanced configuration
