# Model Orchestrator - Consolidated Production Version

**Version**: 3.0.0
**Status**: ✅ Production Ready
**Test Coverage**: 78% (42/42 tests passing)

## Quick Start

```python
from model_orchestrator_consolidated import ModelOrchestrator

# Initialize orchestrator
orchestrator = ModelOrchestrator()

# Select best model for task
model_id, model = orchestrator.select_model("Write Python code to sort a list")

print(f"Selected: {model_id}")
print(f"Provider: {model.provider.value}")
print(f"Context: {model.context_window:,} tokens")
```

## Features

✅ **52 Models** across 6 providers (Anthropic, OpenAI, Google, xAI, Local, Cloud)
✅ **Intelligent Routing** with cost optimization and capability matching
✅ **Real API Integration** with async support and automatic fallback
✅ **Dependency Injection** for easy testing and customization
✅ **Comprehensive Testing** with 42 unit tests (100% pass rate)
✅ **MODELS.md Integration** for custom routing rules
✅ **Cost Tracking** with detailed usage reports

## Installation

```bash
# Install dependencies
pip install aiohttp requests tenacity

# Optional: Install test dependencies
pip install pytest pytest-cov pytest-asyncio
```

## Basic Usage

### Model Selection

```python
# Basic selection
model_id, model = orchestrator.select_model("Your prompt here")

# With strategy
model_id, model = orchestrator.select_model(
    "Your prompt",
    strategy="cost_optimize"  # or "quality_first", "speed_priority"
)

# With guide disabled
model_id, model = orchestrator.select_model(
    "Your prompt",
    use_guide=False
)
```

### API Calls (Async)

```python
import asyncio

async def main():
    response = await orchestrator.call_model(
        model_id="codellama:34b",
        messages="Write a sorting function",
        temperature=0.7
    )
    print(response.content)

asyncio.run(main())
```

### Cost Tracking

```python
# Track usage
orchestrator.track_usage(
    model_id="gpt-4o",
    input_tokens=1000,
    output_tokens=500,
    latency_ms=250
)

# Get cost report
report = orchestrator.get_cost_report()
print(f"Total cost: ${report['total_cost']:.4f}")
print(f"By provider: {report['by_provider']}")
```

### Consensus Selection

```python
# Select multiple models for consensus
group = orchestrator.create_consensus_group(
    prompt="What is 2+2?",
    num_models=3,
    diverse=True  # Diverse providers
)

for model_id, model in group:
    print(f"- {model_id} ({model.provider.value})")
```

## Running Tests

```bash
# Run all tests
pytest tests/test_orchestrator.py -v

# With coverage
pytest tests/test_orchestrator.py --cov=model_orchestrator_consolidated

# Run demo
python3 model-orchestrator-consolidated.py
```

## Architecture

### Components

- **ModelRegistry**: Centralized model definitions (52 models)
- **TaskAnalyzer**: Prompt analysis and requirement detection
- **ModelScorer**: Model fitness scoring algorithm
- **ModelGuideParser**: MODELS.md guidance integration
- **ModelOrchestrator**: Main orchestration and coordination

### Dependency Injection

```python
from model_orchestrator_consolidated import (
    ModelOrchestrator,
    ModelRegistry,
    ModelGuideParser,
    TaskAnalyzer,
    ModelScorer
)

# Custom components
registry = ModelRegistry()
guide = ModelGuideParser("custom/path/to/guide.md")
analyzer = TaskAnalyzer()
scorer = ModelScorer()

# Inject dependencies
orchestrator = ModelOrchestrator(
    registry=registry,
    guide=guide,
    analyzer=analyzer,
    scorer=scorer
)
```

## Supported Models

### Local Models (Ollama)
- **Code**: codellama:34b, magicoder:7b, codellama:13b, deepseek-coder:1.3b
- **General**: qwen2.5:32b-instruct, qwen3:8b, llama3.1:8b, llama3.2:3b
- **Advanced**: deepseek-r1:70b

### Cloud Models
- **xAI**: grok-4-fast-reasoning, grok-code-fast-1, grok-3
- **OpenAI**: o1-pro, gpt-4o, gpt-4-turbo, gpt-3.5-turbo, o3, o3-mini
- **Google**: gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-pro
- **Anthropic**: claude-opus-4.1, claude-sonnet-4.5, claude-3.5-sonnet

## Configuration

### Environment Variables

```bash
# Required for API access
export XAI_API_KEY="your-xai-key"
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export DIAL_API_KEY="your-dial-key"  # Optional for DIAL models
```

### MODELS.md Guide (Optional)

Create a `MODELS.md` file for custom routing rules:

```markdown
### Code Tasks
- **code generation**: codellama:34b > magicoder:7b > grok-code-fast-1

### Fallback Chains
- code: grok-code-fast-1 → codellama:34b → magicoder:7b

### Blocked Models
- llama3.2: Not suitable for production
```


