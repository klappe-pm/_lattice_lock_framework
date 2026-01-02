# Model Orchestrator

The **Model Orchestrator** is the core routing engine of Lattice Lock. it intelligently directs prompts to the most suitable LLM based on cost, performance, and capability requirements.

## Key Features

- **Smart Routing**: Dynamically selects models based on `complexity` and `priority`.
- **Failover**: Automatically tries fallback models if the primary provider fails.
- **Cost Tracking**: Logs token usage and estimated costs for every request.
- **Unified API**: Single interface (`orchestrator.route_request`) for all providers (OpenAI, Anthropic, Google, etc.).

## Usage

```python
from lattice_lock.orchestrator.core import ModelOrchestrator

orchestrator = ModelOrchestrator()
response = await orchestrator.route_request(
    "Explain quantum entanglement",
    model_id="claude-3-opus"
)
print(response.content)
```

## Configuration

Models are defined in `src/lattice_lock/orchestrator/models.yaml`. You can override this path with `LATTICE_MODELS_CONFIG_PATH`.
