
# cli_orchestrator
## Usage
### CLI Commands

```bash
# List all models with details
lattice-lock orchestrator list --verbose
```

```bash
# Analyze a prompt to see model selection
lattice-lock orchestrator analyze "Write a Python web server"
```

```bash
# Route a request with specific strategy
lattice-lock orchestrator route "Explain quantum computing" --strategy quality_first
```

```bash
# Create consensus group
lattice-lock orchestrator consensus "What's the best database for this project?" --num 5
```

```bash
# Show cost report
lattice-lock orchestrator cost
```

```bash
# Test integration
lattice-lock gauntlet
```

### Python API

```python
from lattice_lock_orchestrator import ModelOrchestrator
# ModelRouter may be deprecated or integrated, assuming core usage for now:
# from lattice_lock_orchestrator.core import ModelOrchestrator
```

```python
# Initialize
orchestrator = ModelOrchestrator()
```

```python
# track costs
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
