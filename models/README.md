# Model Registry

This folder contains the model configuration for the Lattice Lock AI Model Orchestration system.

## Files

| File | Purpose |
|------|---------|
| `registry.yaml` | Canonical model registry used by `ModelOrchestrator` |
| `grok-models-config.yaml` | xAI Grok-specific configuration used by `GrokAPI` |

## Viewing Available Models

Use the CLI to see the current model list:

```bash
# List all registered models
lattice-lock orchestrator list

# Filter by provider
lattice-lock orchestrator list --provider openai

# Show detailed capabilities
lattice-lock orchestrator list --verbose
```

## Model Selection

The orchestrator automatically selects the best model based on your task. Use `analyze` to see recommendations:

```bash
lattice-lock orchestrator analyze "Write a Python REST API"
```

Or specify a selection strategy:

```bash
lattice-lock orchestrator route "Your prompt" --strategy balanced
# Strategies: balanced, cost_optimize, quality_first, speed_priority
```

## Supported Providers

The registry includes models from these providers:

| Provider | Env Variable | Notes |
|----------|--------------|-------|
| OpenAI | `OPENAI_API_KEY` | GPT-4, GPT-3.5, O1 reasoning models |
| Anthropic | `ANTHROPIC_API_KEY` | Claude 3.x and Claude 4.x |
| Google | `GOOGLE_API_KEY` | Gemini 2.x and 1.5 |
| xAI | `XAI_API_KEY` | Grok models (up to 2M context) |
| Ollama | (local) | Free local models via Ollama |
| Azure | `AZURE_OPENAI_API_KEY` | Enterprise Azure OpenAI |
| Bedrock | AWS credentials | AWS Bedrock managed models |

## Registry Schema

Models in `registry.yaml` follow this structure:

```yaml
providers:
  provider_name:
    models:
      model-id:
        api_name: "api-model-name"
        context_window: 128000
        input_cost: 5.0      # per million tokens
        output_cost: 15.0    # per million tokens
        reasoning_score: 90.0
        coding_score: 85.0
        speed_rating: 8.0
        maturity: PRODUCTION  # PRODUCTION, BETA, EXPERIMENTAL
        status: ACTIVE
        capabilities: [function_calling, vision]
```

## Adding or Updating Models

1. Edit `registry.yaml` with the new model configuration
2. Ensure all required fields are present (api_name, context_window, costs, scores)
3. Run validation: `lattice-lock validate`
4. Test with: `lattice-lock orchestrator list --verbose`

## Python API

```python
from lattice_lock_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()

# List all models
for model_id, model in orchestrator.registry.models.items():
    print(f"{model_id}: {model.provider.value}")

# Check available providers
available = orchestrator.get_available_providers()
print(f"Configured providers: {available}")
```

## Related Documentation

- [CLI Orchestrator Commands](../cli_commands/cli_orchestrator.md)
- [Provider Fallback Strategy](../developer_documentation/design/6.1.3_provider_fallback_strategy.md)
