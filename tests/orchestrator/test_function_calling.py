from unittest.mock import AsyncMock, MagicMock

import pytest

from lattice_lock.orchestrator.core import ModelOrchestrator
from lattice_lock.orchestrator.types import (
    APIResponse,
    FunctionCall,
    ModelCapabilities,
    ModelProvider,
    TaskType,
)


# Define a mock function that the model can call
async def mock_get_weather(location: str) -> str:
    """Gets the current weather for a given location."""
    if location == "London":
        return "Sunny, 20°C"
    elif location == "New York":
        return "Cloudy, 15°C"
    else:
        return "Unknown weather"


@pytest.fixture
def orchestrator():
    """Fixture for a ModelOrchestrator instance."""
    return ModelOrchestrator()


@pytest.fixture
def mock_openai_model_cap():
    """Mock ModelCapabilities for an OpenAI model that supports function calling."""
    return ModelCapabilities(
        name="gpt-4-0613",
        api_name="gpt-4-0613",
        provider=ModelProvider.OPENAI,
        context_window=8192,
        input_cost=0.03,
        output_cost=0.06,
        reasoning_score=90.0,
        coding_score=80.0,
        speed_rating=5.0,
        supports_function_calling=True,
    )


@pytest.mark.asyncio
async def test_model_orchestrator_function_calling(orchestrator, mock_openai_model_cap):
    """
    Test that ModelOrchestrator correctly handles a function call from a model.
    """
    # Register the mock function
    orchestrator.register_function("get_weather", mock_get_weather)
    orchestrator.registry.models[mock_openai_model_cap.api_name] = mock_openai_model_cap

    # Mock the API client's chat_completion to return a function call
    mock_api_client = AsyncMock()
    # First response: Request function call
    first_response = APIResponse(
        content=None,
        model="gpt-4-0613",
        provider="openai",
        usage={"input_tokens": 100, "output_tokens": 50},
        latency_ms=200,
        raw_response={
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "call_abc123",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "London"}',
                                },
                            }
                        ],
                    }
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        },
        function_call=FunctionCall(name="get_weather", arguments={"location": "London"}),
    )

    # Second response: Final answer after function execution
    second_response = APIResponse(
        content="The weather in London is Sunny, 20°C.",
        model="gpt-4-0613",
        provider="openai",
        usage={"input_tokens": 150, "output_tokens": 20},
        latency_ms=150,
        raw_response={
             "choices": [{"message": {"content": "The weather in London is Sunny, 20°C."}}],
             "usage": {"prompt_tokens": 150, "completion_tokens": 20, "total_tokens": 170}
        }
    )

    mock_api_client = AsyncMock()
    mock_api_client.chat_completion.side_effect = [first_response, second_response]
    # Temporarily replace the orchestrator's client_pool.get_client method to return our mock client
    orchestrator.client_pool.get_client = MagicMock(return_value=mock_api_client)

    # Route a request that should trigger the function call
    response = await orchestrator.route_request(
        prompt="What's the weather in London?", model_id="gpt-4-0613", task_type=TaskType.GENERAL
    )

    # Assertions
    assert mock_api_client.chat_completion.call_count == 2

    # Verify first call received the user prompt
    first_call_args = mock_api_client.chat_completion.call_args_list[0]
    first_call_messages = first_call_args.kwargs["messages"]
    assert first_call_messages[0]["role"] == "user"
    assert "weather in London" in first_call_messages[0]["content"]

    # Assert the arguments of the second call to chat_completion
    second_call_args = mock_api_client.chat_completion.call_args_list[1]
    second_call_messages = second_call_args.kwargs["messages"]

    # The last message in the second call should be the tool output
    assert second_call_messages[-1]["role"] == "tool"
    assert second_call_messages[-1]["content"] == "Sunny, 20°C"
    assert (
        second_call_messages[-1]["tool_call_id"] == "call_abc123"
    )  # Should match the ID from the mock raw_response

    # The final response should contain the answer, not the function call itself
    assert response.content == "The weather in London is Sunny, 20°C."
    assert response.function_call is None
    
    # To verify the function call happened, we check the history passed to the model
    # The second call's messages list contains the assistant's tool call and the tool's response
    history = mock_api_client.chat_completion.call_args_list[1].kwargs["messages"]
    
    # 1. User prompt
    # 2. Assistant tool call
    # 3. Tool output
    
    assistant_msg = history[-2]
    # tool_msg check is covered by lines 121-125
    
    assert assistant_msg["role"] == "assistant"
    assert assistant_msg["tool_calls"][0]["function"]["name"] == "get_weather"
    assert assistant_msg["tool_calls"][0]["function"]["arguments"] == '{"location": "London"}'
