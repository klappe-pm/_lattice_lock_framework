# CLI Orchestrator

Command-line interface for the Lattice Lock AI Model Orchestration system. Routes requests to optimal models across 63+ models from 8 providers (OpenAI, Anthropic, Google, xAI, Ollama, Azure, Bedrock).

## CLI Commands

### List Models

List all available models in the registry with their capabilities and costs.

```bash
# List all models
lattice-lock orchestrator list

# Filter by provider
lattice-lock orchestrator list --provider openai

# Show detailed capabilities (vision, reasoning, code, functions)
lattice-lock orchestrator list --verbose
```

### Analyze Prompts

Analyze a prompt to see task classification and model recommendations.

```bash
# Analyze a prompt and see top 5 model recommendations
lattice-lock orchestrator analyze "Write a Python web server with async support"

# Output includes:
# - Task type detection (CODE_GENERATION, REASONING, etc.)
# - Context requirements
# - Vision/reasoning/function requirements
# - Ranked model recommendations with scores
```

### Route Requests

Route a request through the orchestration system with configurable mode and strategy.

```bash
# Basic routing (auto mode, balanced strategy)
lattice-lock orchestrator route "Explain quantum computing"

# Route with specific strategy
lattice-lock orchestrator route "Debug this code" --strategy quality_first

# Route with specific mode
lattice-lock orchestrator route "Complex analysis task" --mode adaptive
```

**Options:**
- `--mode`: Routing mode - `auto` (default), `consensus`, `chain`, `adaptive`
- `--strategy`: Selection strategy - `balanced` (default), `cost_optimize`, `quality_first`, `speed_priority`

> **Note:** The route command currently performs model selection and cost estimation. Actual API calls require programmatic usage via the Python API.

### Generate Prompts

Generate AI agent prompts from specifications and roadmaps using the Prompt Architect system.

```bash
# Generate from specification file
lattice-lock orchestrator generate-prompts --spec specs/feature.md --output-dir prompts/

# Generate from roadmap/WBS
lattice-lock orchestrator generate-prompts --roadmap implementation/roadmap.yaml

# Auto-discover from Project Agent
lattice-lock orchestrator generate-prompts --from-project

# Filter by phases and tools
lattice-lock orchestrator generate-prompts --spec specs/feature.md --phases "1,2" --tools "devin,claude"

# Dry run (simulate without writing files)
lattice-lock orchestrator generate-prompts --spec specs/feature.md --dry-run
```

**Options:**
- `--spec`: Path to specification file (Markdown, YAML, or JSON)
- `--roadmap`: Path to roadmap/WBS file
- `--output-dir`: Output directory for generated prompts
- `--dry-run`: Simulate without writing files
- `--from-project`: Auto-discover specs from Project Agent
- `--phases`: Comma-separated list of phases to generate
- `--tools`: Comma-separated list of tools to filter (devin, claude, gemini)

### Cost Tracking

View cost usage reports for API calls.

```bash
# Show session and 30-day cost summary
lattice-lock orchestrator cost

# Show detailed breakdown by provider and model
lattice-lock orchestrator cost --detailed
```

### Consensus Groups

Create consensus groups for multi-model verification (planned feature).

```bash
# Create consensus group (not yet implemented)
lattice-lock orchestrator consensus "What's the best database for this project?" --num 5
```

> **Note:** Consensus groups are planned for a future release.

## Python API

### Basic Usage

```python
import asyncio
from lattice_lock_orchestrator import ModelOrchestrator

# Initialize with optional guide path
orchestrator = ModelOrchestrator(guide_path="path/to/guide.yaml")

# Route a request (async)
async def main():
    response = await orchestrator.route_request(
        prompt="Write a sorting algorithm in Python",
        task_type=None,  # Auto-detect, or specify TaskType.CODE_GENERATION
        model_id=None,   # Auto-select, or force specific model
    )
    print(response.content)

asyncio.run(main())
```

### Function Calling

Register custom functions for models to call during execution.

```python
from lattice_lock_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()

# Register a function
def get_weather(location: str) -> str:
    return f"Weather in {location}: Sunny, 72°F"

orchestrator.register_function("get_weather", get_weather)

# The model can now call this function during route_request
```

### Provider Management

Check and manage available providers.

```python
from lattice_lock_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()

# Get list of providers with configured credentials
available = orchestrator.get_available_providers()
print(f"Available providers: {available}")

# Check detailed status of all providers
status = orchestrator.check_provider_status()
for provider, message in status.items():
    print(f"{provider}: {message}")
```

### Cost Tracking

Access cost tracking through the orchestrator's cost_tracker.

```python
from lattice_lock_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()

# After making API calls, check costs
session_cost = orchestrator.cost_tracker.get_session_cost()
print(f"Session cost: ${session_cost:.6f}")

# Get 30-day aggregated report
report = orchestrator.cost_tracker.get_report(days=30)
print(f"Total cost (30d): ${report['total_cost']:.6f}")
print(f"By provider: {report['by_provider']}")
print(f"By model: {report['by_model']}")
```

### Task Analysis

Analyze prompts to understand task requirements.

```python
from lattice_lock_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()

# Analyze a prompt
requirements = orchestrator.analyzer.analyze("Build a REST API with authentication")
print(f"Task type: {requirements.task_type.name}")
print(f"Min context: {requirements.min_context}")
print(f"Requires vision: {requirements.require_vision}")
print(f"Requires functions: {requirements.require_functions}")
```

### Model Registry Access

Query the model registry for capabilities.

```python
from lattice_lock_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()

# Get all models
for model_id, model in orchestrator.registry.models.items():
    print(f"{model_id}: {model.provider.value}, context={model.context_window}")

# Get specific model capabilities
model = orchestrator.registry.get_model("gpt-4-turbo")
if model:
    print(f"Supports vision: {model.supports_vision}")
    print(f"Supports reasoning: {model.supports_reasoning}")
    print(f"Input cost: ${model.input_cost}/1M tokens")
```

## Environment Variables

Configure provider credentials via environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google (Gemini)
export GOOGLE_API_KEY="..."

# xAI (Grok)
export XAI_API_KEY="..."

# Azure OpenAI
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://..."

# AWS Bedrock (uses AWS credentials)
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

## Related Commands

```bash
# Run semantic tests (Gauntlet)
lattice-lock gauntlet

# Validate project structure
lattice-lock validate

# Run static analysis (Sheriff)
lattice-lock sheriff src/
```
