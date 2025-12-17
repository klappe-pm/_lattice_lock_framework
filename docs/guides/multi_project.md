# Multi-Project Guide

Managing multiple projects with Lattice Lock requires careful organization of schemas and dependencies. This guide covers monorepo setups and shared definitions.

## Monorepo Setup

In a monorepo, you can centralize your Lattice Lock configuration or maintain separate configs per service.

### Directory Structure

```
my-monorepo/
├── shared/
│   ├── lattice-shared.yaml  # Shared types and rules
│   └── schemas/             # Common domain models
├── service-a/
│   ├── lattice.yaml         # Service-specific config
│   └── src/
└── service-b/
    ├── lattice.yaml
    └── src/
```

### Configuration Inheritance

Service-level configurations can inherit from a shared base.

**service-a/lattice.yaml**
```yaml
extends: ../shared/lattice-shared.yaml

project:
  name: service-a

models:
  # Service-specific models
```

## Shared Schema Definitions

Define common data types and models in a shared location to ensure consistency across services.

**shared/lattice-shared.yaml**
```yaml
types:
  UserId: String
  Timestamp: Integer

models:
  User:
    fields:
      id: UserId
      createdAt: Timestamp
```

## Cross-Project Validation

When services interact, you may need to validate data against another service's schema.

### Schema Registry

Publish your schemas to a central registry (e.g., an S3 bucket or artifact repository) during your CI/CD pipeline.

### Remote Schema Loading

Configure Lattice Lock to load schemas from the registry.

```yaml
validation:
  external_schemas:
    - url: https://schemas.internal/service-b/latest.yaml
      prefix: ServiceB
```

Usage in Service A:

```yaml
models:
  Order:
    fields:
      userId: ServiceB.User.id
```

## Dependency Management

Ensure that all services use compatible versions of the Lattice Lock framework and shared rules.

- **Lock Files**: Use `poetry.lock` or `requirements.txt` in the root or per service to pin versions.
- **CI Checks**: Run a "schema compatibility check" in CI to detect breaking changes in shared models that affect dependent services.
