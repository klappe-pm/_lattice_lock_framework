---
title: readme
type: reference
status: stable
categories: [reference, cli]
sub_categories: [index]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [cli-index-001]
tags: [cli, index, reference]
---

# CLI Reference

The `lattice-lock` command-line interface provides tools for scaffolding, validating, and managing Lattice Lock Framework projects.

## Synopsis

```bash
lattice-lock [OPTIONS] COMMAND [ARGS]...
```

## Global Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--version` | | flag | Show the version and exit |
| `--verbose` | `-v` | flag | Enable verbose output for all commands |
| `--help` | | flag | Show help message and exit |

## Commands

| Command | Description |
|---------|-------------|
| [`init`](init.md) | Initialize a new Lattice Lock project with scaffolding |
| [`validate`](validate.md) | Validate a Lattice Lock project against schemas and rules |
| [`doctor`](doctor.md) | Check environment health for Lattice Lock |
| [`sheriff`](docs/reference/cli/sheriff.md) | AST-based validation for import discipline and type hints |
| [`gauntlet`](docs/reference/cli/gauntlet.md) | Generate and run semantic tests from lattice.yaml |
| [`compile`](compile.md) | Compile and enforce lattice.yaml specifications |
| [`admin`](docs/reference/cli/admin.md) | Manage users, keys, and system configuration |
| [`orchestrator`](docs/reference/cli/orchestrator.md) | Manage model routing and analysis |
| [`feedback`](feedback.md) | Submit bugs and feature requests |

## Command Categories

### Project Setup
- **init** - Scaffold new projects with compliant directory structures and templates

### Validation
- **validate** - Run schema, environment, agent, and structure validators
- **sheriff** - Perform AST-based static analysis for code compliance
- **gauntlet** - Generate and execute semantic contract tests

### Environment
- **doctor** - Diagnose environment configuration and dependencies

## Exit Codes

All commands follow a consistent exit code convention:

| Code | Meaning |
|------|---------|
| `0` | Success - all operations completed without errors |
| `1` | Failure - validation errors, missing requirements, or command failures |
| `2` | Usage error - invalid arguments or options |

### Command-Specific Exit Codes

**validate**:
- `0` - All validations passed (may include warnings)
- `1` - One or more validation errors

**doctor**:
- `0` - All required checks passed
- `1` - One or more required checks failed

**sheriff**:
- `0` - No violations found
- `1` - One or more violations found
- `1` - Path or configuration errors

**gauntlet**:
- `0` - All tests passed
- Non-zero - pytest exit code (test failures or errors)

## Environment Variables

The CLI respects these environment variables:

| Variable | Description |
|----------|-------------|
| `LATTICE_LOCK_CONFIG` | Path to default lattice.yaml configuration |
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |

## Installation

```bash
pip install lattice-lock
```

## Quick Start

```bash
# Create a new project
lattice-lock init my_project --template service

# Navigate to project
cd my_project

# Validate project structure
lattice-lock validate

# Check environment health
lattice-lock doctor

# Run AST validation
lattice-lock sheriff src/

# Run semantic tests
lattice-lock gauntlet --generate --run
```

## See Also

- [Configuration Reference](docs/reference/configuration.md) - lattice.yaml schema documentation
- [Getting Started Guide](interactive_onboarding_guide.md)
- [Development Guide](development_guide.md)
