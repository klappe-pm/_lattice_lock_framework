# Configuration Reference

Complete reference for `lattice.yaml` configuration files.

## Overview

The `lattice.yaml` file is the central configuration for Lattice Lock projects. It defines project metadata, entity schemas, validation rules, and governance policies.

## File Location

Lattice Lock searches for configuration in this order:
1. Path specified via `--lattice` flag
2. `lattice.yaml` in current directory
3. `lattice.yaml` in parent directories (recursively)

## Schema Versions

| Version | Description |
|---------|-------------|
| `1.0` | Legacy format with basic project metadata |
| `v2.1` | Current version with full entity schema support |

## Top-Level Structure

```yaml
# Schema version (required)
version: "v2.1"

# Generated module name
generated_module: my_project_types

# Database configuration (optional)
database:
  backend: postgresql
  connection_string: ${DATABASE_URL}

# Project metadata (v1.0 format)
project:
  name: my_project
  description: "Project description"

# Module definitions (v1.0 format)
modules:
  - name: my_module
    path: src/my_module
    type: service

# Entity definitions (required)
entities:
  EntityName:
    description: "Entity description"
    fields: {}
    constraints: {}
    ensures: []
    indexes: []

# Governance configuration
config:
  forbidden_imports: []
  required_patterns: []
  validation:
    strict_mode: false
    fail_on_warning: false

# Validation settings
validation:
  strict_mode: true
  fail_fast: false
  generate_contracts: true
```

## Configuration Sections

### version

**Type:** `string`
**Required:** Yes

Schema version identifier.

```yaml
version: "v2.1"
```

### generated_module

**Type:** `string`
**Required:** No

Name of the Python module to generate for type definitions.

```yaml
generated_module: api_service_types
```

### database

**Type:** `object`
**Required:** No

Database connection configuration.

| Field | Type | Description |
|-------|------|-------------|
| `backend` | string | Database type: `postgresql`, `mysql`, `sqlite` |
| `connection_string` | string | Connection URL (supports `${ENV_VAR}` syntax) |

```yaml
database:
  backend: postgresql
  connection_string: ${DATABASE_URL}
```

### project

**Type:** `object`
**Required:** No (v1.0 format)

Project metadata for v1.0 schema format.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Project name |
| `description` | string | Project description |

```yaml
project:
  name: my_project
  description: "A Lattice Lock managed project"
```

### modules

**Type:** `array`
**Required:** No (v1.0 format)

Module definitions for v1.0 schema format.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Module name |
| `path` | string | Path to module source |
| `type` | string | Module type: `service`, `agent`, `library` |

```yaml
modules:
  - name: api_module
    path: src/api
    type: service
```

## Entity Definitions

### entities

**Type:** `object`
**Required:** Yes

Map of entity names to entity definitions.

```yaml
entities:
  User:
    description: "User account entity"
    fields:
      id: int
      email: str
      created_at: datetime
    constraints:
      id: {primary_key: true, auto_increment: true}
      email: {unique: true, max_length: 255}
    ensures:
      - "email contains '@'"
    indexes:
      - {fields: [email], unique: true}
```

### Entity Fields

#### fields

**Type:** `object`
**Required:** Yes

Map of field names to field types.

**Supported Types:**

| Type | Python Type | Description |
|------|-------------|-------------|
| `int` | `int` | Integer |
| `str` | `str` | String |
| `bool` | `bool` | Boolean |
| `float` | `float` | Floating point |
| `datetime` | `datetime` | Date and time |
| `date` | `date` | Date only |
| `time` | `time` | Time only |
| `bytes` | `bytes` | Binary data |
| `list` | `list` | List/array |
| `dict` | `dict` | Dictionary/object |

```yaml
fields:
  id: int
  name: str
  price: float
  is_active: bool
  created_at: datetime
  metadata: dict
```

#### constraints

**Type:** `object`
**Required:** No

Map of field names to constraint definitions.

**Available Constraints:**

| Constraint | Type | Description |
|------------|------|-------------|
| `primary_key` | bool | Mark as primary key |
| `auto_increment` | bool | Auto-increment integer field |
| `unique` | bool | Enforce uniqueness |
| `foreign_key` | string | Foreign key reference (format: `Entity.field`) |
| `max_length` | int | Maximum string length |
| `min_length` | int | Minimum string length |
| `gt` | number | Greater than |
| `gte` | number | Greater than or equal |
| `lt` | number | Less than |
| `lte` | number | Less than or equal |
| `enum` | array | Allowed values |

```yaml
constraints:
  id: {primary_key: true, auto_increment: true}
  email: {unique: true, max_length: 255}
  status: {enum: [pending, active, inactive]}
  user_id: {foreign_key: User.id}
  quantity: {gt: 0, lte: 1000}
  password: {min_length: 8, max_length: 128}
```

#### ensures

**Type:** `array`
**Required:** No

List of business logic conditions that must be true.

**Supported Expressions:**

| Expression | Example | Description |
|------------|---------|-------------|
| Comparison | `"price >= 0"` | Numeric comparison |
| Membership | `"status in ['a', 'b']"` | Value in list |
| Contains | `"email contains '@'"` | String contains |
| Length | `"len(name) >= 1"` | Length check |
| Equality | `"a == b"` | Equality check |

```yaml
ensures:
  - "price_cents >= 0"
  - "quantity > 0"
  - "status in ['pending', 'confirmed', 'shipped']"
  - "email contains '@'"
  - "len(sku) >= 3"
```

#### indexes

**Type:** `array`
**Required:** No

List of index definitions for database optimization.

| Field | Type | Description |
|-------|------|-------------|
| `fields` | array | List of field names to index |
| `unique` | bool | Whether index enforces uniqueness |

```yaml
indexes:
  - {fields: [email], unique: true}
  - {fields: [status]}
  - {fields: [created_at]}
  - {fields: [user_id, status]}  # Composite index
```

#### description

**Type:** `string`
**Required:** No

Human-readable description of the entity.

```yaml
description: "User account with authentication credentials"
```

## Governance Configuration

### config

**Type:** `object`
**Required:** No

Governance rules for code validation.

#### forbidden_imports

**Type:** `array`
**Required:** No

List of import paths that should never be used.

```yaml
config:
  forbidden_imports:
    - os.system
    - subprocess.call
    - subprocess.Popen
    - eval
    - exec
    - pickle.loads
    - marshal.loads
```

#### required_patterns

**Type:** `array`
**Required:** No

List of required code patterns.

| Pattern | Description |
|---------|-------------|
| `type_hints` | Function parameters and returns must have type hints |
| `docstrings` | Functions and classes must have docstrings |

```yaml
config:
  required_patterns:
    - type_hints
    - docstrings
```

#### validation

**Type:** `object`
**Required:** No

Validation behavior settings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `strict_mode` | bool | `false` | Treat warnings as errors |
| `fail_on_warning` | bool | `false` | Fail validation on warnings |

```yaml
config:
  validation:
    strict_mode: false
    fail_on_warning: false
```

### validation (top-level)

**Type:** `object`
**Required:** No

Schema validation settings (v2.1 format).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `strict_mode` | bool | `false` | Enable strict validation |
| `fail_fast` | bool | `false` | Stop on first error |
| `generate_contracts` | bool | `false` | Generate contract test files |

```yaml
validation:
  strict_mode: true
  fail_fast: false
  generate_contracts: true
```

## Environment Variable Substitution

Configuration values can reference environment variables using `${VAR_NAME}` syntax:

```yaml
database:
  connection_string: ${DATABASE_URL}

config:
  api_key: ${API_KEY}
```

## Complete Examples

### Service Project (v1.0 format)

```yaml
version: "1.0"

project:
  name: my_api_service
  description: "REST API service for user management"

modules:
  - name: my_api_service
    path: src/my_api_service
    type: service

entities:
  - name: user_service
    type: service
    module: my_api_service
    description: "User management service"

config:
  forbidden_imports:
    - os.system
    - subprocess.call
    - eval
    - exec

  required_patterns:
    - type_hints
    - docstrings

  validation:
    strict_mode: false
    fail_on_warning: false
```

### Data Pipeline (v2.1 format)

```yaml
version: v2.1
generated_module: pipeline_types

database:
  backend: postgresql
  connection_string: ${DATABASE_URL}

entities:
  DataSource:
    description: "Configuration for a data extraction source"
    fields:
      id: int
      name: str
      source_type: str
      connection_config: str
      is_active: bool
      created_at: datetime
    constraints:
      id: {primary_key: true, auto_increment: true}
      name: {unique: true, max_length: 100}
      source_type: {enum: [database, api, file, stream]}
    ensures:
      - "source_type in ['database', 'api', 'file', 'stream']"
      - "len(name) >= 1"
    indexes:
      - {fields: [name], unique: true}
      - {fields: [source_type]}
      - {fields: [is_active]}

  PipelineRun:
    description: "Record of a complete pipeline execution"
    fields:
      id: int
      source_id: int
      records_processed: int
      status: str
      started_at: datetime
      completed_at: datetime
    constraints:
      id: {primary_key: true, auto_increment: true}
      source_id: {foreign_key: DataSource.id}
      records_processed: {gte: 0}
      status: {enum: [pending, running, completed, failed]}
    ensures:
      - "records_processed >= 0"
      - "status in ['pending', 'running', 'completed', 'failed']"
    indexes:
      - {fields: [source_id]}
      - {fields: [status]}

validation:
  strict_mode: true
  fail_fast: false
  generate_contracts: true
```

## Validation

Validate your configuration with:

```bash
lattice-lock validate --schema-only
```

## See Also

- [CLI Overview](cli/index.md)
- [init](cli/init.md) - Generate lattice.yaml with scaffolding
- [validate](cli/validate.md) - Validate configuration
- [sheriff](cli/sheriff.md) - AST validation using config
- [gauntlet](cli/gauntlet.md) - Generate tests from entities
