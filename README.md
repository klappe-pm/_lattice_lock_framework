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
from src.lattice_lock_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()
response = await orchestrator.route_request(
    prompt="Implement a REST API endpoint",
    task_type=TaskType.CODE_GENERATION
)
```

### CLI Usage

```bash
# Route a request
./scripts/orchestrator_cli.py route "Your prompt" --strategy balanced

# Analyze a task
./scripts/orchestrator_cli.py analyze "Your prompt"

# List available models
./scripts/orchestrator_cli.py list --verbose
```

## Repository Structure

```
lattice-lock-framework/
├── version.txt                      # Framework version (2.1.0)
├── specifications/                  # Authoritative specifications
│   ├── lattice_lock_framework_specifications.md
│   └── lattice_lock_versioning_strategy.md
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
├── agent_definitions/               # Agent YAML specifications
├── agent_specifications/            # Agent format specifications
├── agent_workflows/                 # Workflow templates
├── agent_memory/                    # Memory directives
├── developer_documentation/         # How-to guides
├── models/                          # Model configuration and guides
└── directory/                       # Repository standards
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

- [Lattice-Lock Specification](specifications/lattice_lock_framework_specifications.md) - Authoritative reference
- [Agent Specification v2.1](agent_specifications/agent_instructions_file_format_v2_1.md) - Agent definition format
- [Repository Structure Standards](directory/repository_structure_standards.md) - File organization rules
- [Model Usage Guide](models/MODEL_USAGE_GUIDE.md) - Model selection guidance

## License

MIT License - see [LICENSE.md](LICENSE.md)
