# Model Orchestration Guide

Lattice Lock's orchestrator allows you to manage multiple LLMs, optimize costs, and define complex workflows.

## Model Selection Strategies

Choose the right model for the right task based on capability, cost, and latency.

### Static Routing

Assign specific models to specific tasks in your configuration.

```yaml
orchestrator:
  routes:
    - task: "code_generation"
      model: "claude-3-opus"
    - task: "summarization"
      model: "gpt-3.5-turbo"
```

### Dynamic Routing

Use a router model to decide which model to call based on prompt complexity.

```yaml
orchestrator:
  router:
    model: "gpt-4o-mini"
    thresholds:
      complexity:
        high: "claude-3-opus"
        low: "gpt-3.5-turbo"
```

## Cost Optimization

### Token Budgeting

Set limits on token usage per project or user.

```yaml
orchestrator:
  budgets:
    daily_limit_usd: 50.00
    alert_threshold: 0.8
```

### Caching Responses

Cache LLM responses for identical prompts to save costs and reduce latency.

```yaml
orchestrator:
  cache:
    enabled: true
    ttl: 3600  # 1 hour
```

## Custom Routing Rules

Implement custom logic to route requests.

```python
from lattice_lock.orchestrator import Router

class MyRouter(Router):
    def route(self, prompt: str) -> str:
        if "urgent" in prompt:
            return "fast-model"
        return "smart-model"
```

## Multi-Model Workflows

Chain multiple models together to solve complex problems.

### Chain of Thought

1. **Planner**: Generates a plan (High capability model).
2. **Executor**: Executes steps (Specialized coding model).
3. **Reviewer**: Checks the output (High reasoning model).

```yaml
workflows:
  feature_implementation:
    steps:
      - name: plan
        model: claude-3-opus
        prompt: "Create a plan for..."
      - name: code
        model: deepseek-coder
        input: ${plan.output}
        prompt: "Implement the following plan..."
      - name: review
        model: gpt-4
        input: ${code.output}
        prompt: "Review this code..."
```
