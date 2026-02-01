---
title: orchestrator
type: reference
status: stable
categories: [reference, api]
sub_categories: [orchestrator]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [api-orch-001]
tags: [orchestrator, api, routing]
---

# Orchestrator API

The `lattice_lock.orchestrator` module manages LLM interactions, routing requests to the most appropriate model based on task requirements.

## Overview

The Orchestrator analyzes prompts, scores available models, and routes requests. It handles fallback logic and function calling.

## Classes

### `ModelOrchestrator`

Intelligent model orchestration system.

```python
class ModelOrchestrator:
    def __init__(self, guide_path: Optional[str] = None): ...
```

**Methods:**

#### `route_request`

```python
async def route_request(
    self,
    prompt: str,
    model_id: Optional[str] = None,
    task_type: Optional[TaskType] = None,
    **kwargs
) -> APIResponse:
```

Route a request to the appropriate model.

**Arguments:**
- `prompt` (str): The user prompt.
- `model_id` (Optional[str]): Specific model ID to force use.
- `task_type` (Optional[TaskType]): Manual task type override.
- `**kwargs`: Additional arguments passed to the API client.

**Returns:**
- `APIResponse`: The response from the model.

#### `register_function`

```python
def register_function(self, name: str, func: Callable):
```

Registers a function for the model to call.

## Usage Example

```python
import asyncio
from lattice_lock.orchestrator import ModelOrchestrator

async def main():
    orchestrator = ModelOrchestrator()

    response = await orchestrator.route_request(
        prompt="Write a Python function to calculate fibonacci numbers."
    )

    print(response.content)

if __name__ == "__main__":
    asyncio.run(main())
```
