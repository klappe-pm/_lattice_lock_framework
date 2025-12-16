# Lattice-Lock Framework

A governance-first framework for AI-assisted software development that provides deterministic, policy-enforced code generation and intelligent model orchestration across 63 AI models from 8 providers.

## Quick Start

```bash
# Install the framework
pip install -e .

# Validate a project
lattice-lock validate ./my-project

# Route a request to the optimal model
./scripts/orchestrator_cli.py route "Implement a REST API" --strategy balanced

# Analyze a task
./scripts/orchestrator_cli.py analyze "Write unit tests"

# List available models
./scripts/orchestrator_cli.py list --verbose
```

## Core Components

| Component | Description |
|-----------|-------------|
| **Governance Core** | Schema-driven code generation with compile-time enforcement via `lattice.yaml`, Sheriff (AST analysis), and Gauntlet (test generation) |
| **Model Orchestrator** | Intelligent routing across 63 models from 8 providers with task analysis, capability scoring, and cost tracking |
| **Prompt Architect** | Automated prompt generation from project specifications with quality scoring |

## Supported Providers

| Provider | Models | Key Strengths |
|----------|--------|---------------|
| Local/Ollama | 20 | Privacy, offline, zero cost |
| OpenAI | 11 | GPT-4o, O1 reasoning |
| Anthropic | 7 | Claude 4.1 Opus, safety |
| Google Gemini | 6 | 2M context window |
| xAI Grok | 5 | 2M context, vision |
| Azure OpenAI | 4 | Enterprise compliance |
| AWS Bedrock | 8 | AWS integration |
| DIAL | 2 | Enterprise gateway |

## Documentation

All documentation has been consolidated into the `docs/` folder:

- **[Documentation Index](docs/index.md)** - Start here for navigation
- **[Getting Started](docs/getting_started/installation.md)** - Installation and setup
- **[Quick Start Guide](docs/getting_started/quick_start.md)** - Get running in 5 minutes
- **[Architecture Overview](docs/architecture/high_level_architecture.md)** - System design
- **[System Design Diagram](docs/architecture/system_design.md)** - Visual architecture
- **[Sequence Diagrams](docs/architecture/sequence_diagrams.md)** - Key workflows
- **[Domain Model](docs/architecture/domain_model.md)** - Entity relationships
- **[Model Usage Guide](docs/models/model_usage_guide.md)** - Using AI models
- **[CLI Reference](docs/reference/cli/index.md)** - Command-line interface
- **[API Reference](docs/reference/api/index.md)** - Programmatic API

### Specifications

- [Framework Specifications](docs/specifications/framework_specifications.md) - Authoritative reference
- [Agent Instructions Format](docs/agents/agent_instructions_format.md) - Agent definition format
- [Versioning Strategy](docs/specifications/versioning_strategy.md) - Version management

## Repository Structure

```
lattice-lock-framework/
├── docs/                            # Consolidated documentation
│   ├── index.md                     # Documentation entry point
│   ├── getting_started/             # Installation and setup guides
│   ├── tutorials/                   # Step-by-step tutorials
│   ├── guides/                      # In-depth feature guides
│   ├── architecture/                # System design and diagrams
│   ├── reference/                   # CLI and API reference
│   ├── models/                      # Model configuration docs
│   ├── agents/                      # Agent definitions and workflows
│   └── specifications/              # Framework specifications
├── src/                             # Source code
│   ├── lattice_lock/                # Core governance library
│   ├── lattice_lock_orchestrator/   # Model orchestrator
│   ├── lattice_lock_agents/         # Agent implementations
│   └── lattice_lock_cli/            # CLI implementation
├── scripts/                         # Utility scripts
├── tests/                           # Test suite
└── models/                          # Model registry configuration
```

## License

MIT License - see [LICENSE.md](LICENSE.md)
