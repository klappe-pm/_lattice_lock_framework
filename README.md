# Lattice-Lock Framework

A governance-first framework for AI-assisted software development that provides deterministic, policy-enforced code generation and agent orchestration.

## Overview

Lattice-Lock combines three integrated layers:

1. **Governance Core** - Schema-driven code generation with compile-time enforcement (`lattice.yaml` → Compiler → Sheriff → Gauntlet)
2. **Model Orchestrator** - Intelligent routing of AI tasks across 63 models from 8 providers
3. **Engineering Framework** - Standardized tooling for repo scaffolding, CI/CD, and validation

## Quick Start

### Using the Model Orchestrator

```python
from lattice_lock_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()
response = await orchestrator.route_request(
    prompt="Implement a REST API endpoint",
    task_type=TaskType.CODE_GENERATION
)
```

### CLI Usage

```bash
# Route a request
lattice-lock orchestrator route "Your prompt" --strategy balanced

# Analyze a task
lattice-lock orchestrator analyze "Your prompt"

# List available models
lattice-lock orchestrator list --verbose
```

## Repository Structure

```
lattice-lock-framework/
├── version.txt                      # Framework version (2.1.0)
├── docs/                            # Developer guides, Agent Definitions, Models, Specs
│   ├── agents/                      # Agent Definitions and Memory
│   │   ├── agent_definitions/       # Agent YAML specifications
│   │   ├── agent_workflows/         # Workflow templates
│   │   └── agent_memory/            # Memory directives
│   ├── models/                      # Model configurations and registry
│   └── specifications/              # Authoritative specifications
├── src/
│   └── lattice_lock_orchestrator/   # Core library
│       ├── core.py                  # ModelOrchestrator class
│       ├── types.py                 # Type definitions
│       ├── registry.py              # Model registry
│       ├── scorer.py                # Task analysis and scoring
│       ├── api_clients.py           # Provider clients
│       └── guide.py                 # Model selection guide parser
├── scripts/
│   ├── setup/                       # Setup and initialization scripts
│   ├── validation/                  # Validation tools
│   └── utilities/                   # Utility scripts
├── tests/                           # Test suite
└── docs/                            # Documentation site source
```

## Supported Providers

| Provider | Models | Key Strengths |
|----------|--------|---------------|
| Local/Ollama | 20 | Privacy, offline, zero cost |
| OpenAI | 11 | GPT-4o, O1 reasoning |
| Anthropic | 7 | Claude 4.1 Opus |
| Google | 6 | Gemini 2.0, 2M context |
| xAI Grok | 5 | 2M context, vision |
| Azure | 4 | Enterprise compliance |
| Bedrock | 8 | AWS managed service |
| DIAL | 2 | Enterprise gateway |

## Documentation

- [Lattice-Lock Specification](lattice_lock_framework_specifications.md) - Authoritative reference
- [Agent Specification](docs/agents/agent_definitions/agents_glossary/agent_instructions_file_format.md) - Agent definition format


## License

MIT License - see [LICENSE.md](LICENSE.md)
