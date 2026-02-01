---
title: sheriff
type: reference
status: stable
categories: [reference, cli]
sub_categories: [commands]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [cli-sheriff-001]
tags: [cli, sheriff, validation, governance]
---

# cmd_sheriff

## lattice sheriff

Enforces lattice schema rules and validates code compliance. Automatically checks semantic contracts, relationships, and entity definitions against lattice.yaml specifications. Provides automated fixing capabilities.

```bash
lattice sheriff [OPTIONS]
```

**Basic Examples:**

```bash
# Validate all contracts
lattice sheriff
```

```bash
# Auto-fix violations
lattice sheriff --fix
```

```bash
# Check with custom schema
lattice sheriff --lattice custom.yaml
```

#### --lattice

Path to lattice.yaml file (default: lattice.yaml).

```bash
# Use custom schema
lattice sheriff --lattice schemas/production.yaml
```

```bash
# Different directory
lattice sheriff --lattice /path/to/lattice.yaml
```

```bash
# Named configuration
lattice sheriff --lattice configs/strict.yaml
```

#### --fix

Automatically fix violations where possible.

```bash
# Auto-fix all issues
lattice sheriff --fix
```

```bash
# Fix with custom schema
lattice sheriff --fix --lattice custom.yaml
```

```bash
# Fix and ignore patterns
lattice sheriff --fix --ignore "tests/**"
```

#### --ignore

Patterns to ignore (glob syntax).

```bash
# Ignore test files
lattice sheriff --ignore "tests/**"
```

```bash
# Multiple patterns
lattice sheriff --ignore "tests/**" --ignore "**/__pycache__/**"
```

```bash
# Ignore with fix
lattice sheriff --fix --ignore "generated/**"
```

#### --format

Output format: text, json, github, junit.

```bash
# JSON output
lattice sheriff --format json
```

```bash
# GitHub Actions format
lattice sheriff --format github
```

```bash
# JUnit XML for CI
lattice sheriff --format junit
```

#### --cache/--no-cache

Enable or disable caching (default: enabled).

```bash
# Disable caching
lattice sheriff --no-cache
```

```bash
# Explicit enable
lattice sheriff --cache
```

```bash
# Force fresh check
lattice sheriff --no-cache --fix
```

#### --cache-dir

Directory for cache files (default: .lattice-cache).

```bash
# Custom cache directory
lattice sheriff --cache-dir /tmp/lattice-cache
```

```bash
# Project-specific cache
lattice sheriff --cache-dir .cache/sheriff
```

```bash
# Shared cache location
lattice sheriff --cache-dir ~/.lattice/cache
```

#### --clear-cache

Clear the cache before running.

```bash
# Clear and run
lattice sheriff --clear-cache
```

```bash
# Clear then fix
lattice sheriff --clear-cache --fix
```

```bash
# Fresh validation
lattice sheriff --clear-cache --no-cache
```

**Use Cases:**
- Pre-commit hook validation
- CI/CD contract enforcement
- Code review automation
- Migration validation
- Compliance auditing

### Process Flow Diagrams: lattice sheriff

#### Decision Flow: Validation and Fixing
This diagram shows the sheriff's decision-making process for validating and fixing violations. Use this to understand when automatic fixes are applied versus when manual intervention is required.

```mermaid
graph TD
    A[Start Sheriff] --> B[Load Schema]
    B --> C[Discover Source Files]
    C --> D{Use Cache?}
    D -->|Yes| E{Cache Valid?}
    D -->|No| F[Scan All Files]
    E -->|Yes| G[Load Cached Results]
    E -->|No| F
    G --> H[Scan Changed Files]
    H --> I[Merge Results]
    F --> J[Parse Each File]
    I --> J
    J --> K[Extract Contracts]
    K --> L[Validate Against Schema]
    L --> M{Violations?}
    M -->|No| N[Success]
    M -->|Yes| O{Fix Flag?}
    O -->|No| P[Report Violations]
    O -->|Yes| Q{Auto-Fixable?}
    Q -->|Yes| R[Apply Fixes]
    Q -->|No| P
    R --> S[Re-validate]
    S --> T{Still Violations?}
    T -->|No| N
    T -->|Yes| P
    P --> U[Exit with Error]
```

#### Sequence Flow: Cache-Optimized Validation
This diagram illustrates how the sheriff uses caching to optimize repeated validations. Use this to understand performance characteristics and when cache invalidation occurs.

```mermaid
sequenceDiagram
    participant CLI as Sheriff Command
    participant Cache as Cache Layer
    participant Scanner as File Scanner
    participant Validator as Contract Validator
    participant Fixer as Auto-Fixer
    
    CLI->>Cache: Check cache
    alt Cache valid
        Cache-->>CLI: Cached results
        CLI->>Scanner: Scan modified files
    else Cache invalid
        CLI->>Scanner: Scan all files
    end
    Scanner->>Scanner: Discover source files
    Scanner->>Scanner: Apply ignore patterns
    Scanner-->>Validator: File list
    loop Each file
        Validator->>Validator: Extract contracts
        Validator->>Validator: Check schema
        Validator-->>CLI: Violations
    end
    alt Fix enabled
        CLI->>Fixer: Apply fixes
        Fixer->>Validator: Re-validate
        Validator-->>CLI: Updated results
    end
    CLI->>Cache: Update cache
    Cache-->>CLI: Complete
```

#### Data Flow: Violation Detection
This diagram shows how violations flow from source files through the validation pipeline. Use this when debugging why certain violations are detected or missed.

```mermaid
graph LR
    A[Source Files] --> B[File Scanner]
    B --> C{Ignore Pattern?}
    C -->|No| D[AST Parser]
    C -->|Yes| E[Skip]
    D --> F[Contract Extractor]
    F --> G[Entity Contracts]
    F --> H[Relationship Contracts]
    G --> I[Schema Validator]
    H --> I
    I --> J{Match Schema?}
    J -->|Yes| K[Valid]
    J -->|No| L[Violation Record]
    L --> M[Severity Assessment]
    M --> N{Auto-fixable?}
    N -->|Yes| O[Fix Queue]
    N -->|No| P[Manual Queue]
    O --> Q[Fix Report]
    P --> Q
    K --> R[Success Report]
```

#### Detailed Flowchart: Auto-Fix Logic
This flowchart details the automatic fixing process for different violation types. Use this to understand which violations can be automatically resolved and which require manual intervention.

```mermaid
flowchart TD
    A[Detected Violation] --> B{Violation Type}
    B -->|Missing Contract| C[Generate Contract]
    B -->|Invalid Type| D[Correct Type Annotation]
    B -->|Missing Field| E[Add Field Definition]
    B -->|Wrong Relationship| F{Can Infer Correct?}
    B -->|Other| G[Mark Manual]
    C --> H[Insert at Correct Location]
    D --> I[Update Type String]
    E --> J[Insert Field with Default]
    F -->|Yes| K[Update Relationship]
    F -->|No| G
    H --> L[Format Code]
    I --> L
    J --> L
    K --> L
    L --> M[Write File]
    M --> N[Re-validate]
    N --> O{Still Invalid?}
    O -->|Yes| G
    O -->|No| P[Mark Fixed]
    G --> Q[Add to Manual List]
```

#### State Diagram: Cache Lifecycle
This state diagram shows cache state transitions during sheriff operations. Use this to understand cache invalidation triggers and optimization strategies.

```mermaid
stateDiagram-v2
    [*] --> Empty: Initial
    Empty --> Valid: First run
    Valid --> Invalid: Schema changed
    Valid --> Stale: Files modified
    Valid --> Empty: clear-cache
    Invalid --> Valid: Re-scan
    Stale --> Partial: Incremental update
    Partial --> Valid: Scan complete
    Valid --> Valid: cache enabled
    Empty --> Empty: no-cache
    Invalid --> Empty: clear-cache
```
