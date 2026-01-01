
# cli_orchestrator
## Usage
### CLI Commands

```bash
# List all models with details
./orchestrator_cli.py list --verbose
```

```bash
# Analyze a prompt to see model selection
./orchestrator_cli.py analyze "Write a Python web server"
```

```bash
# Route a request with specific strategy
./orchestrator_cli.py route "Explain quantum computing" --strategy quality_first
```

```bash
#Create consensus group
./orchestrator_cli.py consensus "What's the best database for this project?" --num 5

```

```bash
# Show cost report
./orchestrator_cli.py cost
```

```bash
# Test integration
./orchestrator_cli.py test
```

### Python API

```python
from model_orchestrator import ModelOrchestrator
from pal_mcp_bridge import ModelRouter
```

```python
#track costs
orchestrator.track_usage(model_id, input_tokens=1000, output_tokens=500, latency_ms=250)
report = orchestrator.get_cost_report()
```

```python
# Select best model
model_id, model = orchestrator.select_model(
    "Write a sorting algorithm",
    strategy="balanced"  # or cost_optimize, quality_first, speed_priority
)

```

```python
# Route through system
result = await router.route(
    "Analyze this complex problem",
    mode="consensus",  # or auto, chain, adaptive
    num_models=3
)
```

```python
# Initialize
orchestrator = ModelOrchestrator()
router = ModelRouter()
```
