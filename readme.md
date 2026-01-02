# Lattice Lock Framework

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-82%25-green)
![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-2.1.0-orange)

A comprehensive governance and validation framework for software projects that keeps humans and AI agents in perfect sync.

## Overview

Lattice Lock is a **governance-first framework** designed to enforce code quality, architecture rules, and validation policies across your codebase. It bridges the gap between static analysis and runtime testing, ensuring your project adheres to its define structure ("The Lattice").

### Key Features

*   **Sheriff:** AST-based static analysis to catch architecture violations in milliseconds.
*   **Gauntlet:** Runtime test generator that creates pytest suites from your governance rules.
*   **Orchestrator:** Intelligent multi-model routing for AI agents (OpenAI, Anthropic, Google, xAI).
*   **Consensus:** Multi-model voting engine for high-stakes decision making.
*   **Lattice Policy:** Declarative `lattice.yaml` configuration for all project rules.

## Architecture

```mermaid
graph TD
    User[User / CLI] --> API[Lattice Lock API]
    API --> Orch[Model Orchestrator]
    API --> Sheriff[Sheriff (Static Analysis)]
    API --> Gauntlet[Gauntlet (Runtime Tests)]
    
    Orch --> Provider1[OpenAI]
    Orch --> Provider2[Anthropic]
    Orch --> Provider3[Google]
    Orch --> Consensus[Consensus Engine]
    
    Sheriff --> Rules[lattice.yaml Rules]
    Gauntlet --> Rules
    
    subgraph Core Framework
        Orch
        Sheriff
        Gauntlet
        Consensus
    end
```

## Quick Start

### Installation

```bash
pip install lattice-lock
```

### 1. Initialize a Project

```bash
lattice-lock init
# Creates a default lattice.yaml and project structure
```

### 2. Define Rules (`lattice.yaml`)

```yaml
version: "2.1"
rules:
  - id: "no-print"
    description: "Use logger instead of print"
    severity: "error"
    forbids: "node.is_call_to('print')"
```

### 3. Validate Code

```bash
# Run static analysis
lattice-lock validate
```

### 4. Ask the Orchestrator

```bash
# ask a question using the configured models
lattice-lock ask "Explain the architecture of this project"
```

## Documentation

Documentation is organized in the `docs/` directory:

* **[In-Depth Guides](docs/guides/)** - Tutorials and workflows
* **[API Reference](docs/reference/)** - Detailed API docs
* **[Architecture](docs/architecture/)** - System design
* **[Contributing](contributing.md)** - **READ THIS FIRST** for development

## Feature Flags

Lattice Lock allows you to toggle features via `LATTICE_FEATURE_PRESET` or `LATTICE_DISABLED_FEATURES`.

**Presets (LATTICE_FEATURE_PRESET):**

* `full` (Default): All features enabled.
* `standard`: Orchestrator, Sheriff, Gauntlet enabled.
* `minimal`: Core Orchestrator only.

**Explicit Disable (LATTICE_DISABLED_FEATURES):**
Comma-separated list of features to disable (e.g., `sheriff,gauntlet`).
Available flags: `sheriff`, `gauntlet`, `feedback`, `rollback`, `consensus`, `mcp`.

## Configuration

Copy `.env.example` to `.env` to configure API keys and feature flags.

```bash
cp .env.example .env
# Edit .env with your keys
```

## Contributing

We welcome contributions! Please see **[contributing.md](contributing.md)** for our strict coding standards and workflow. `contributing.md` is the **SINGLE SOURCE OF TRUTH** for this project.

## License

This project is licensed under the terms in [LICENSE.md](LICENSE.md).
