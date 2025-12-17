# Orchestrator Command

The `orchestrator` command group manages model interactions, routing, and analysis within the Lattice Lock Framework.

## Usage

```bash
lattice-lock orchestrator [COMMAND] [OPTIONS]
```

## Commands

### `list`

List all available models and their capabilities.

```bash
# List all models
lattice-lock orchestrator list

# Show verbose details including context window and pricing
lattice-lock orchestrator list --verbose
```

### `analyze`

Analyze a prompt to determine the best model selection strategy without executing it.

```bash
lattice-lock orchestrator analyze "Write a Python web server"
```

### `route`

Route a prompt to the most appropriate model(s) based on strategy.

```bash
# Route with default strategy (balanced)
lattice-lock orchestrator route "Explain quantum computing"

# Route with specific strategy
lattice-lock orchestrator route "Explain quantum computing" --strategy quality_first
```

**Strategies:**
- `balanced` (Default): Balances cost, speed, and quality.
- `quality_first`: Prioritizes best possible output regardless of cost.
- `cost_optimize`: Prioritizes lowest cost.
- `speed_priority`: Prioritizes lowest latency.

### `consensus`

Execute a prompt using multiple models and aggregate their responses for better accuracy.

```bash
lattice-lock orchestrator consensus "What's the best database for this project?" --num 5
```

### `cost`

Display usage and cost reports.

```bash
lattice-lock orchestrator cost
```
