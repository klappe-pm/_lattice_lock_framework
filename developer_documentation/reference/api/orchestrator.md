# Orchestrator Module

The `lattice_lock_orchestrator` module provides intelligent model routing and orchestration capabilities. It analyzes user prompts and selects the best LLM based on task requirements, cost, and performance.

## Overview

The orchestrator serves as the central brain for dispatching tasks to various AI models.

## Modules

### Core Orchestration (`core.py`)

The main orchestration logic.

#### Classes

- `ModelOrchestrator`: The main orchestrator class.
    - `__init__(guide_path: Optional[str] = None)`: Initializes the orchestrator.
    - `route_request(prompt: str, model_id: Optional[str] = None, task_type: Optional[TaskType] = None, **kwargs) -> APIResponse`: Routes a request to the best model.
    - `register_function(name: str, func: Callable)`: Registers a tool function for models to use.

### Model Registry (`registry.py`)

Manages the available models and their capabilities.

#### Classes

- `ModelRegistry`: The registry of models.
    - `get_model(model_id: str) -> Optional[ModelCapabilities]`: Gets a model by ID.
    - `get_all_models() -> List[ModelCapabilities]`: Gets all registered models.
    - `get_models_by_provider(provider: ModelProvider) -> List[ModelCapabilities]`: Gets models by provider.

### Task Analysis & Scoring (`scorer.py`)

Analyzes prompts and scores models.

#### Classes

- `TaskAnalyzer`: Analyzes prompts.
    - `analyze(prompt: str) -> TaskRequirements`: Extracts requirements from a prompt.
- `ModelScorer`: Scores models.
    - `score(model: ModelCapabilities, requirements: TaskRequirements) -> float`: Calculates a fitness score (0.0 - 1.0).

### Guide (`guide.py`)

Parses external configuration (e.g., `MODELS.md`) for routing rules.

#### Classes

- `ModelGuideParser`: Parses the guide file.
    - `get_recommended_models(task_type: str) -> List[str]`: Gets recommended models for a task.
    - `get_fallback_chain(task_type: str) -> List[str]`: Gets fallback model chain.
    - `is_model_blocked(model_id: str) -> bool`: Checks if a model is blocked.

## Usage Examples

```python
import asyncio
from lattice_lock_orchestrator.core import ModelOrchestrator

async def main():
    orchestrator = ModelOrchestrator()
    
    # Simple routing
    response = await orchestrator.route_request("Write a Python script to sort a list")
    print(f"Response from {response.model_id}: {response.content}")

    # Force specific model
    response = await orchestrator.route_request("Hello", model_id="gpt-4o")

if __name__ == "__main__":
    asyncio.run(main())
```
