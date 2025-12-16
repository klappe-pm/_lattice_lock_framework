# Lattice-Lock Framework Documentation

Welcome to the Lattice-Lock Framework documentation. This framework provides governance-first AI-assisted software development with deterministic, policy-enforced code generation and intelligent model orchestration.

## Quick Navigation

### Getting Started

If you're new to Lattice-Lock, start here:

- [Installation Guide](getting_started/installation.md) - Set up the framework
- [Quick Start](getting_started/quick_start.md) - Get running in 5 minutes
- [Configuration](getting_started/configuration.md) - Configure your project
- [Credentials Setup](getting_started/credentials_setup.md) - Set up API keys
- [Troubleshooting](getting_started/troubleshooting.md) - Common issues and solutions

### Tutorials

Step-by-step guides for common tasks:

- [Getting Started Tutorial](tutorials/getting_started.md) - Your first project
- [First Project](tutorials/first_project.md) - Build your first governed project
- [Adding Validation](tutorials/adding_validation.md) - Add governance rules
- [CI Integration](tutorials/ci_integration.md) - Integrate with CI/CD pipelines

### Guides

In-depth guides for specific features:

- [Governance Guide](guides/governance.md) - Understanding governance rules
- [Model Orchestration](guides/model_orchestration.md) - Using the Model Orchestrator
- [Advanced Validation](guides/advanced_validation.md) - Complex validation scenarios
- [Custom Rules](guides/custom_rules.md) - Creating custom governance rules
- [Production Deployment](guides/production_deployment.md) - Deploying to production
- [Multi-Project Setup](guides/multi_project.md) - Managing multiple projects

### Architecture

Understanding the system design:

- [High-Level Architecture](architecture/high_level_architecture.md) - System overview
- [System Design Diagram](architecture/system_design.md) - Visual architecture with component details
- [Sequence Diagrams](architecture/sequence_diagrams.md) - Key workflow sequences
- [Domain Model](architecture/domain_model.md) - Entity relationship diagram
- [Model Orchestrator Architecture](architecture/model_orchestrator_architecture.md) - Orchestrator internals
- [Data Flow](architecture/model_orchestrator_data_flow.md) - How data flows through the system

### Reference

API and CLI documentation:

#### CLI Commands

- [CLI Overview](reference/cli/index.md) - Command-line interface overview
- [validate](reference/cli/validate.md) - Validate project structure
- [sheriff](reference/cli/sheriff.md) - Run static analysis
- [gauntlet](reference/cli/gauntlet.md) - Generate contract tests
- [doctor](reference/cli/doctor.md) - Diagnose issues
- [init](reference/cli/init.md) - Initialize a new project
- [orchestrator](reference/cli/orchestrator.md) - Model orchestrator commands

#### API Reference

- [API Overview](reference/api/index.md) - Programmatic API overview
- [Compiler API](reference/api/compiler.md) - Lattice compiler
- [Validator API](reference/api/validator.md) - Schema validation
- [Sheriff API](reference/api/sheriff.md) - Static analysis
- [Gauntlet API](reference/api/gauntlet.md) - Test generation
- [Admin API](reference/api/admin.md) - Administration
- [Orchestrator API](reference/api/orchestrator.md) - Model orchestration

### Models

AI model configuration and usage:

- [Model Usage Guide](models/model_usage_guide.md) - How to use models
- [Model Capabilities](models/model_capabilities.md) - What each model can do
- [Model Registry](models/model_registry.md) - Available models
- [Model Selection Guidelines](models/model_selection_guidelines.md) - Choosing the right model
- [Local Models Setup](models/local_models_setup.md) - Running models locally with Ollama
- [Grok Models Setup](models/grok_models_setup.md) - Using xAI Grok models

### Agents

Agent definitions and workflows:

- [Agent Glossary](agents/glossary.md) - Agent terminology
- [Agent Instructions Format](agents/agent_instructions_format.md) - How to define agents
- [Agent Memory](agents/agent_memory_storage.md) - Persistent agent memory
- [Universal Memory Directive](agents/universal_memory_directive.md) - Memory guidelines

#### Workflow Templates

- [Parallel Execution](agents/workflows/parallel_execution.md) - Run agents in parallel
- [Sequential Execution](agents/workflows/sequential_execution.md) - Run agents in sequence
- [Hybrid Workflow](agents/workflows/hybrid_workflow.md) - Combined patterns

### Specifications

Authoritative specifications:

- [Framework Specifications](specifications/framework_specifications.md) - Complete framework spec
- [Versioning Strategy](specifications/versioning_strategy.md) - Version management
- [Repository Structure](specifications/repository_structure.md) - Project structure standards

### Design Documents

Design decisions and strategies:

- [Provider Strategy](design/provider_strategy.md) - AI provider integration
- [Cost Telemetry Strategy](design/6.3.3_cost_telemetry_strategy.md) - Cost tracking design
- [Provider Fallback Strategy](design/6.1.3_provider_fallback_strategy.md) - Fallback handling
- [Orchestrator Capabilities](design/6.1.1_orchestrator_capabilities_contract.md) - Capability contracts

### Development

Contributing and development guides:

- [Development Overview](development/overview.md) - Development setup
- [Development Guide](development/development_guide.md) - Contributing guidelines
- [Development Workflow](development/development_workflow.md) - Git workflow
- [API Documentation](development/api_documentation.md) - Internal APIs
- [Troubleshooting Guide](development/troubleshooting_guide.md) - Debugging issues
- [Agent Scripts](development/agent_scripts.md) - Script documentation

### Security

Security documentation:

- [Security Audit Report](security/security_audit_report.md) - Security assessment

### Archive

Historical documentation:

- [Project Prompts Archive](_archive/project_prompts/) - Implementation prompts history

## Framework Overview

Lattice-Lock combines three integrated layers:

1. **Governance Core** - Schema-driven code generation with compile-time enforcement
   - Schema Validator validates `lattice.yaml` configurations
   - Lattice Compiler compiles governance rules
   - Sheriff performs AST-based static analysis
   - Gauntlet generates contract tests

2. **Model Orchestrator** - Intelligent routing across 63 models from 8 providers
   - Task Analyzer classifies prompts
   - Capability Scorer ranks models
   - Request Router selects optimal models
   - Consensus Engine aggregates multi-model responses

3. **Prompt Architect** - Automated prompt generation from specifications
   - Spec Analyzer extracts requirements
   - Roadmap Parser builds task graphs
   - Tool Matcher selects appropriate tools
   - Prompt Generator creates optimized prompts

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

## Quick Start

```bash
# Install the framework
pip install -e .

# Validate a project
lattice-lock validate ./my-project

# Route a request to the optimal model
./scripts/orchestrator_cli.py route "Implement a REST API" --strategy balanced

# Analyze a task
./scripts/orchestrator_cli.py analyze "Write unit tests for the auth module"

# List available models
./scripts/orchestrator_cli.py list --verbose
```

## Getting Help

- [Troubleshooting Guide](getting_started/troubleshooting.md) - Common issues
- [GitHub Issues](https://github.com/klappe-pm/lattice-lock-framework/issues) - Report bugs
- [Discussions](https://github.com/klappe-pm/lattice-lock-framework/discussions) - Ask questions
