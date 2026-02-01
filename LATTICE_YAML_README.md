# lattice.yaml Configuration Guide

## Overview

The `lattice.yaml` file is the central configuration file for Lattice Lock projects. It defines the project's entity schemas, validation rules, type generation, and governance policies. This file serves as the contract between your project structure and the Lattice Lock framework.

## Quick Start

```yaml
version: v2.1
generated_module: my_project_types

entities:
  User:
    description: "User account entity"
    fields:
      id:
        type: uuid
        primary_key: true
      name:
        type: str
        unique: true

config:
  forbidden_imports:
    - os.system
    - eval
```

## Top-Level Structure

### Required Sections

#### `version`
- **Type:** String
- **Required:** Yes
- **Format:** `vX.Y` or `vX.Y.Z` (e.g., `v2.1`, `v1.0`)
- **Description:** Specifies the schema version. Currently supported versions are `v1.0` (legacy) and `v2.1` (current).

```yaml
version: v2.1
```

#### `generated_module`
- **Type:** String
- **Required:** Yes
- **Description:** Name of the Python module to generate for type definitions. This module will contain generated types based on your entity definitions.
- **Naming Convention:** Use snake_case format, typically `<project_name>_types`

```yaml
generated_module: my_service_types
```

#### `entities`
- **Type:** Object (dictionary)
- **Required:** Yes
- **Description:** Map of entity names to entity definitions. Entities represent the data contracts and business objects in your system.

```yaml
entities:
  User:
    fields: {}
  Product:
    fields: {}
```

### Optional Sections

#### `config`
- **Type:** Object
- **Required:** No
- **Description:** Governance and validation rules for the project

```yaml
config:
  forbidden_imports: []
  required_patterns: []
  validation:
    strict_mode: false
    fail_on_warning: false
```

#### `database`
- **Type:** Object
- **Required:** No
- **Description:** Database connection configuration

```yaml
database:
  backend: postgresql
  connection_string: ${DATABASE_URL}
```

#### `project`
- **Type:** Object
- **Required:** No (v1.0 format)
- **Description:** Project metadata (legacy format)

```yaml
project:
  name: my_project
  description: "Project description"
```

#### `modules`
- **Type:** Array
- **Required:** No (v1.0 format)
- **Description:** Module definitions (legacy format)

```yaml
modules:
  - name: my_module
    path: src/my_module
    type: service
```

#### `validation`
- **Type:** Object
- **Required:** No
- **Description:** Schema validation settings (v2.1 format)

```yaml
validation:
  strict_mode: true
  fail_fast: false
  generate_contracts: true
```

## Entity Definitions

Entities are the core building blocks of Lattice Lock. Each entity represents a data contract with defined fields, constraints, and business rules.

### Entity Structure

```yaml
entities:
  EntityName:
    description: "Human-readable entity description"
    persistence: table        # optional
    fields:
      # field definitions
    ensures:
      # business logic constraints
    indexes:                   # optional
      # index definitions
```

### Fields

Each entity must have a `fields` section defining the data structure.

#### Supported Field Types

| Type | Description | Python Type |
|------|-------------|------------|
| `uuid` | Universally unique identifier | `str` |
| `str` | String/text | `str` |
| `int` | Integer number | `int` |
| `decimal` | Decimal/fixed-point number | `Decimal` |
| `bool` | Boolean | `bool` |
| `enum` | Enumerated values | `str` |

#### Field Definition Example

```yaml
fields:
  id:
    type: uuid
    primary_key: true
  
  name:
    type: str
    unique: true
  
  score:
    type: int
    gt: 0
    lt: 100
  
  rating:
    type: decimal
    gte: 0
    lte: 5
    scale: 2
  
  is_active:
    type: bool
    default: true
  
  status:
    type: enum
    enum: [pending, active, completed]
    default: pending
```

### Field Constraints

Constraints define validation rules and metadata for fields.

#### Available Constraints

| Constraint | Type | Description | Valid For |
|-----------|------|-------------|-----------|
| `primary_key` | bool | Marks field as primary key | All types |
| `unique` | bool | Enforces uniqueness | All types |
| `default` | mixed | Default value if not provided | All types |
| `nullable` | bool | Allows null/None values | All types |
| `gt` | number | Greater than | `int`, `decimal` |
| `gte` | number | Greater than or equal | `int`, `decimal` |
| `lt` | number | Less than | `int`, `decimal` |
| `lte` | number | Less than or equal | `int`, `decimal` |
| `scale` | int | Decimal precision (digits after decimal point) | `decimal` |
| `enum` | array | List of allowed values | `enum` type |

#### Constraint Examples

```yaml
fields:
  # Primary key
  id:
    type: uuid
    primary_key: true
  
  # Uniqueness constraint
  email:
    type: str
    unique: true
  
  # Numeric ranges
  quantity:
    type: int
    gte: 1
    lte: 1000
  
  # Decimal with precision
  price:
    type: decimal
    gte: 0
    scale: 2
  
  # Enum values
  status:
    type: enum
    enum: [draft, published, archived]
    default: draft
  
  # Nullable field with default
  metadata:
    type: str
    nullable: true
    default: null
```

### Ensures: Business Logic Constraints

The `ensures` section defines business logic constraints that validate entity state. These are conditions that must always be true for valid entity instances.

#### Ensures Syntax

```yaml
ensures:
  - name: rule_name
    field: field_name
    constraint: constraint_type
    value: constraint_value
    description: "Human-readable description"
```

#### Constraint Types

- `gt` - Greater than
- `lt` - Less than
- `gte` - Greater than or equal
- `lte` - Less than or equal
- `lt` - Less than
- `unique` - Unique constraint

#### Ensures Examples

```yaml
entities:
  Product:
    fields:
      id:
        type: uuid
        primary_key: true
      price:
        type: decimal
        gte: 0
        scale: 2
      quantity:
        type: int
      status:
        type: enum
        enum: [active, inactive]
    
    ensures:
      - name: positive_price
        field: price
        constraint: gte
        value: 0
        description: "Product price must be non-negative"
      
      - name: valid_quantity
        field: quantity
        constraint: gte
        value: 0
        description: "Quantity cannot be negative"
```

### Indexes (Optional)

Indexes optimize database query performance on specific fields.

#### Index Definition

```yaml
indexes:
  - fields: [field_name]
    unique: false
  
  - fields: [field1, field2]  # Composite index
    unique: false
```

#### Index Examples

```yaml
entities:
  User:
    fields:
      id:
        type: uuid
        primary_key: true
      email:
        type: str
      status:
        type: str
      created_at:
        type: str
    
    indexes:
      # Single field index
      - fields: [email]
        unique: true
      
      # Composite index
      - fields: [status, created_at]
        unique: false
```

## Interfaces (Optional)

Interfaces define service or API contracts with method signatures and dependencies.

### Interface Structure

```yaml
interfaces:
  IServiceName:
    file: src/services/service_name.py
    scaffold: repository_pattern
    depends_on: []
    methods:
      method_name:
        params:
          param_name: EntityName
        returns: EntityName
        ensures:
          - "result.id is not None"
```

### Interface Example

```yaml
interfaces:
  IUserService:
    file: src/services/user_service.py
    scaffold: repository_pattern
    depends_on: []
    
    methods:
      get_user:
        params:
          user_id: str
        returns: User
      
      create_user:
        params:
          data: User
        returns: User
        ensures:
          - "result.id is not None"
      
      delete_user:
        params:
          user_id: str
        returns: bool
```

## Governance Configuration

The `config` section defines project-wide governance rules and validation policies.

### forbidden_imports

**Type:** Array of strings  
**Description:** List of import paths that should never be used in the codebase. The Sheriff CLI tool validates against these.

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

### required_patterns

**Type:** Array of strings  
**Description:** Code patterns that must be present in all implementations.

**Supported Patterns:**
- `type_hints` - Function parameters and return types must have type annotations
- `docstrings` - Functions and classes must have docstrings

```yaml
config:
  required_patterns:
    - type_hints
    - docstrings
```

### validation

**Type:** Object  
**Description:** Validation behavior settings

```yaml
config:
  validation:
    strict_mode: false        # Treat warnings as errors
    fail_on_warning: false    # Fail on any warnings
```

## Database Configuration

Database settings configure the ORM and connection details.

### Structure

```yaml
database:
  backend: postgresql
  connection_string: ${DATABASE_URL}
```

### Supported Backends

- `postgresql` - PostgreSQL database
- `mysql` - MySQL database
- `sqlite` - SQLite database

### Environment Variable Substitution

Configuration values can reference environment variables using `${VAR_NAME}` syntax:

```yaml
database:
  connection_string: ${DATABASE_URL}

config:
  orm_engine: sqlmodel
```

## Complete Examples

### Minimal Configuration

```yaml
version: v2.1
generated_module: types

entities:
  Item:
    fields:
      id:
        type: uuid
        primary_key: true
```

### E-Commerce Service

```yaml
version: v2.1
generated_module: ecommerce_types

config:
  forbidden_imports:
    - os.system
    - eval
  required_patterns:
    - type_hints
    - docstrings
  validation:
    strict_mode: false

entities:
  Product:
    description: "Product in the catalog"
    fields:
      id:
        type: uuid
        primary_key: true
      name:
        type: str
        unique: true
      price:
        type: decimal
        gte: 0
        scale: 2
      inventory_count:
        type: int
        gte: 0
      status:
        type: enum
        enum: [draft, published, discontinued]
        default: draft
    
    ensures:
      - name: positive_price
        field: price
        constraint: gte
        value: 0
        description: "Price must be non-negative"
    
    indexes:
      - fields: [name]
        unique: true
      - fields: [status]

  Order:
    description: "Customer order"
    fields:
      id:
        type: uuid
        primary_key: true
      customer_id:
        type: uuid
      product_id:
        type: uuid
      quantity:
        type: int
        gte: 1
      status:
        type: enum
        enum: [pending, confirmed, shipped, delivered, cancelled]
        default: pending
    
    ensures:
      - name: positive_quantity
        field: quantity
        constraint: gte
        value: 1
        description: "Quantity must be at least 1"
    
    indexes:
      - fields: [customer_id]
      - fields: [status]

interfaces:
  IProductService:
    file: src/services/product_service.py
    scaffold: repository_pattern
    depends_on: []
    
    methods:
      get_product:
        params:
          product_id: str
        returns: Product
      
      create_product:
        params:
          data: Product
        returns: Product
```

### Data Pipeline

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
      id:
        type: uuid
        primary_key: true
      name:
        type: str
        unique: true
      source_type:
        type: enum
        enum: [database, api, file, stream]
      is_active:
        type: bool
        default: true
    
    indexes:
      - fields: [name]
        unique: true
      - fields: [source_type]

  PipelineRun:
    description: "Record of a pipeline execution"
    fields:
      id:
        type: uuid
        primary_key: true
      source_id:
        type: uuid
      records_processed:
        type: int
        gte: 0
      status:
        type: enum
        enum: [pending, running, completed, failed]
      duration_seconds:
        type: decimal
        gte: 0
        scale: 2
    
    ensures:
      - name: non_negative_records
        field: records_processed
        constraint: gte
        value: 0
        description: "Records processed must be non-negative"
```

## Validation

### Validate Your Configuration

Use the Lattice Lock CLI to validate your configuration:

```bash
lattice-lock validate --schema-only
```

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing required section: version` | `version` field not specified | Add `version: v2.1` to top level |
| `Missing required section: entities` | No entities defined | Add at least one entity |
| `Invalid version format` | Version doesn't match `vX.Y` or `vX.Y.Z` | Use format like `v2.1` |
| `Unsupported field type` | Field type not in valid list | Use one of: uuid, str, int, decimal, bool, enum |
| `Numeric constraints on non-numeric field` | Using `gt`, `lt`, etc. on non-numeric field | Only use numeric constraints on `int` or `decimal` fields |
| `Enum values must be a list` | Enum values not formatted as array | Use `enum: [value1, value2]` |

## File Location

Lattice Lock searches for `lattice.yaml` in this order:

1. Path specified via `--lattice` CLI flag
2. `lattice.yaml` in current directory
3. `lattice.yaml` in parent directories (recursively)

## Related Documentation

- [Configuration Reference](./docs/reference/configuration.md) - Detailed API reference
- [CLI Overview](./docs/reference/cli/index.md) - Command-line interface guide
- [init Command](./docs/reference/cli/init.md) - Generate lattice.yaml with scaffolding
- [validate Command](./docs/reference/cli/validate.md) - Validation command reference
- [Sheriff CLI](./docs/reference/cli/sheriff.md) - AST-based validation tool
- [Gauntlet CLI](./docs/reference/cli/gauntlet.md) - Test generation tool
