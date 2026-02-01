---
title: test
type: reference
status: stable
categories: [reference, cli]
sub_categories: [commands]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [cli-test-001]
tags: [cli, test, gauntlet, contracts]
---

# cmd_test

## lattice test

Generates and runs semantic contract tests from lattice.yaml schemas. Automatically creates comprehensive test suites that validate code against schema definitions. Alias: `lattice gauntlet`.

```bash
lattice test [OPTIONS]
```

**Basic Examples:**

```bash
# Generate and run tests
lattice test
```

```bash
# Generate tests without running
lattice test --generate --no-run
```

```bash
# Run existing tests with coverage
lattice test --coverage
```

#### --generate

Generate tests from lattice.yaml without running them.

```bash
# Just generate tests
lattice test --generate --no-run
```

```bash
# Generate to custom directory
lattice test --generate --output tests/contracts
```

```bash
# Regenerate existing tests
lattice test --generate
```

#### --run/--no-run

Run the tests (default: True).

```bash
# Skip running tests
lattice test --generate --no-run
```

```bash
# Explicitly run tests
lattice test --run
```

```bash
# Generate and run
lattice test --generate --run
```

#### --output

Directory to output generated tests.

```bash
# Custom output directory
lattice test --generate --output tests/gauntlet
```

```bash
# Different location
lattice test --output contracts/tests
```

```bash
# Specific path
lattice test --generate --output /path/to/tests
```

#### --lattice

Path to lattice.yaml file.

```bash
# Use specific schema
lattice test --lattice custom.yaml
```

```bash
# Different schema location
lattice test --lattice /path/to/lattice.yaml
```

```bash
# Named schema
lattice test --lattice schemas/production.yaml
```

#### --coverage

Enable coverage reporting.

```bash
# Run with coverage
lattice test --coverage
```

```bash
# Coverage with custom output
lattice test --coverage --output tests/contracts
```

```bash
# Generate coverage report
lattice test --coverage --format json
```

#### --format

Output format(s): json, junit, github.

```bash
# JSON format
lattice test --format json
```

```bash
# JUnit XML
lattice test --format junit
```

```bash
# GitHub Actions
lattice test --format github
```

#### --parallel

Run tests in parallel with pytest-xdist.

```bash
# Auto-detect workers
lattice test --parallel
```

```bash
# Specific worker count
lattice test --parallel 4
```

```bash
# Parallel with coverage
lattice test --parallel --coverage
```

**Use Cases:**
- Contract verification testing
- Regression testing
- CI/CD integration
- Test-driven development
- Coverage analysis

### Process Flow Diagrams: lattice test

#### Decision Flow: Test Generation and Execution
This diagram shows the dual-mode operation of Gauntlet: test generation and/or execution. Use this to understand when tests are generated from schemas versus executed from existing test files.

```mermaid
graph TD
    A[Start Gauntlet] --> B{Generate Flag?}
    B -->|Yes| C[Load Schema]
    B -->|No| D{Tests Exist?}
    C --> E[Parse Entities]
    E --> F[Generate Test Contracts]
    F --> G[Write Test Files]
    G --> H{Run Flag?}
    D -->|No| I[Error: No tests]
    D -->|Yes| H
    H -->|Yes| J[Configure pytest]
    H -->|No| K[Complete]
    J --> L{Parallel?}
    L -->|Yes| M[Run with xdist]
    L -->|No| N[Run sequential]
    M --> O[Collect Results]
    N --> O
    O --> P{Format Output?}
    P -->|Yes| Q[Format Reports]
    P -->|No| R[Display Results]
    Q --> R
    R --> K
```

#### Sequence Flow: Test Generation Pipeline
This diagram illustrates the step-by-step process of parsing a lattice schema and generating test files. Use this to understand the transformation from schema definitions to executable tests.

```mermaid
sequenceDiagram
    participant CLI as Test Command
    participant Parser as Schema Parser
    participant Generator as Test Generator
    participant FS as File System
    participant Pytest as Test Runner
    
    CLI->>FS: Load lattice.yaml
    FS-->>Parser: Schema content
    Parser->>Parser: Parse entities
    Parser->>Parser: Parse relationships
    Parser-->>Generator: Schema model
    Generator->>Generator: Create test contracts
    Generator->>Generator: Generate assertions
    Generator->>FS: Write test files
    FS-->>CLI: Generation complete
    CLI->>Pytest: Run tests
    Pytest->>Pytest: Discover tests
    Pytest->>Pytest: Execute contracts
    Pytest-->>CLI: Test results
```

#### Data Flow: Contract Coverage
This diagram shows how schema coverage information flows through the testing system. Use this when analyzing which schema elements are validated by your test suite.

```mermaid
graph LR
    A[lattice.yaml] --> B[Schema Parser]
    B --> C[Entity Definitions]
    B --> D[Relationship Rules]
    C --> E[Test Generator]
    D --> E
    E --> F[Contract Tests]
    F --> G[pytest Runner]
    G --> H[Coverage Analyzer]
    H --> I[Coverage Report]
    I --> J{All Covered?}
    J -->|No| K[Gap Analysis]
    J -->|Yes| L[Complete]
    K --> M[Additional Tests]
    M --> F
```

#### Detailed Flowchart: Parallel Execution
This flowchart details the parallel test execution process using pytest-xdist. Use this to understand how tests are distributed across worker processes for faster execution.

```mermaid
flowchart TD
    A[Start with parallel] --> B[Detect CPU Cores]
    B --> C[Spawn Worker Processes]
    C --> D[Distribute Test Files]
    D --> E{Worker Available?}
    E -->|Yes| F[Assign Test File]
    E -->|No| G[Queue Test]
    F --> H[Execute Tests]
    H --> I[Collect Results]
    G --> E
    I --> J{More Tests?}
    J -->|Yes| E
    J -->|No| K[Aggregate Results]
    K --> L{Coverage Enabled?}
    L -->|Yes| M[Merge Coverage Data]
    L -->|No| N[Format Report]
    M --> N
    N --> O[Display Results]
```

#### State Diagram: Test Lifecycle
This state diagram shows the different states of generated test files and their transitions. Use this to understand test file management and regeneration scenarios.

```mermaid
stateDiagram-v2
    [*] --> NoTests: Initial State
    NoTests --> Generated: lattice test generate
    Generated --> Running: lattice test run
    Running --> Passed: All tests pass
    Running --> Failed: Tests fail
    Passed --> [*]
    Failed --> Updated: Fix code
    Updated --> Running: Re-run tests
    Generated --> Stale: Schema modified
    Stale --> Regenerated: lattice test generate
    Regenerated --> Running
    Passed --> Stale: Schema updated
```
