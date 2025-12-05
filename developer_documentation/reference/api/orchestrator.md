# Orchestrator Module

The `lattice_lock_orchestrator` module provides intelligent model routing and orchestration capabilities, allowing the framework to dynamically select the best AI model for a given task.

## Overview

The Orchestrator analyzes prompts, determines task requirements (e.g., coding, reasoning, debugging), and routes the request to the most suitable model based on capabilities, cost, and performance. It supports multiple providers including OpenAI, Anthropic, Google, xAI, and local models.

## Classes

### ModelOrchestrator

The main entry point for model interaction.

```python
class ModelOrchestrator:
    def __init__(self, guide_path: Optional[str] = None):
        ...

    async def route_request(
        self, 
        prompt: str, 
        model_id: Optional[str] = None, 
        task_type: Optional[TaskType] = None,
        **kwargs
    ) -> APIResponse:
        ...

    def register_function(self, name: str, func: Callable):
        ...
```

**Methods:**

-   `route_request(...)`: Routes a prompt to the best model.
    -   `prompt` (str): The user's input prompt.
    -   `model_id` (Optional[str]): Force a specific model ID (e.g., "gpt-4-turbo").
    -   `task_type` (Optional[TaskType]): Manually specify the task type.
    -   `**kwargs`: Additional arguments passed to the underlying API client (e.g., `temperature`, `max_tokens`).
    -   **Returns**: `APIResponse` object.

-   `register_function(name: str, func: Callable)`: Registers a Python function for the model to call (Function Calling).

### APIResponse

Standardized response object returned by all model calls.

```python
@dataclass
class APIResponse:
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    latency_ms: int
    raw_response: Optional[Dict] = None
    error: Optional[str] = None
    function_call: Optional[FunctionCall] = None
    function_call_result: Optional[Any] = None
```

**Attributes:**

-   `content` (str): The text response from the model.
-   `model` (str): The ID of the model that generated the response.
-   `provider` (str): The provider name (e.g., "openai", "anthropic").
-   `usage` (Dict[str, int]): Token usage statistics (`input_tokens`, `output_tokens`).
-   `latency_ms` (int): Request latency in milliseconds.
-   `function_call` (Optional[FunctionCall]): Details of a function call if the model requested one.

### TaskType

Enum defining the types of tasks the orchestrator can identify.

```python
class TaskType(Enum):
    CODE_GENERATION = auto()
    DEBUGGING = auto()
    ARCHITECTURAL_DESIGN = auto()
    DOCUMENTATION = auto()
    TESTING = auto()
    DATA_ANALYSIS = auto()
    GENERAL = auto()
    REASONING = auto()
```

## Usage Example

### Basic Routing

```python
import asyncio
from lattice_lock_orchestrator import ModelOrchestrator

async def main():
    orchestrator = ModelOrchestrator()
    
    response = await orchestrator.route_request(
        prompt="Write a Python function to calculate the Fibonacci sequence."
    )
    
    print(f"Model used: {response.model}")
    print(f"Response: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Function Calling

```python
async def get_weather(location: str):
    return {"temp": 72, "condition": "Sunny"}

orchestrator.register_function("get_weather", get_weather)

response = await orchestrator.route_request(
    prompt="What's the weather in San Francisco?"
)
```
