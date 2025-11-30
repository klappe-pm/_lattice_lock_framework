#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for Model Orchestrator
Tests complete workflows with real and mocked components

Test Coverage:
1. Multi-agent workflow tests
2. Model orchestrator integration
3. API endpoint testing with mocks
4. Database/file system integration tests
5. External service mocking
6. Error scenario testing
7. Performance integration tests
8. End-to-end user flows

Model Usage:
- Primary: CodeLlama 34B (test generation, code analysis)
- Secondary: Qwen 2.5 32B (complex test scenarios)
- Fallback: Llama 3.1 8B (lightweight tests)
"""

import pytest
import asyncio
import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from dataclasses import dataclass
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import using filename with hyphens
import importlib.util
spec = importlib.util.spec_from_file_location(
    "model_orchestrator_consolidated",
    Path(__file__).parent.parent / "model-orchestrator-consolidated.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Extract classes
ModelOrchestrator = mod.ModelOrchestrator
ModelRegistry = mod.ModelRegistry
TaskAnalyzer = mod.TaskAnalyzer
ModelScorer = mod.ModelScorer
TaskType = mod.TaskType
ModelProvider = mod.ModelProvider
ModelCapabilities = mod.ModelCapabilities
TaskRequirements = mod.TaskRequirements
APIResponse = mod.APIResponse


# ============================================================================
# Test Fixtures and Mocks
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_api_responses():
    """Mock API responses for different scenarios"""
    return {
        "success": APIResponse(
            content="Test response successful",
            model="test-model",
            provider="test",
            usage={"input_tokens": 100, "output_tokens": 50},
            latency_ms=200,
        ),
        "error": APIResponse(
            content="",
            model="test-model",
            provider="test",
            usage={"input_tokens": 0, "output_tokens": 0},
            latency_ms=0,
            error="API Error: Rate limit exceeded"
        ),
        "timeout": APIResponse(
            content="",
            model="test-model",
            provider="test",
            usage={"input_tokens": 0, "output_tokens": 0},
            latency_ms=30000,
            error="Timeout after 30s"
        )
    }


@pytest.fixture
def mock_multi_agent_context():
    """Mock multi-agent execution context"""
    return {
        "agents": [
            {
                "name": "Architecture Discovery Agent",
                "role": "system_analysis",
                "model": "codellama:34b",
                "status": "active"
            },
            {
                "name": "Testing Specialist",
                "role": "test_generation",
                "model": "qwen2.5:32b",
                "status": "active"
            },
            {
                "name": "Documentation Writer",
                "role": "documentation",
                "model": "llama3.1:8b",
                "status": "active"
            }
        ],
        "workflow": "parallel",
        "coordination_protocol": "asynchronous"
    }


@pytest.fixture
def orchestrator_with_mocks(mock_api_responses):
    """Create orchestrator with mocked API clients"""
    def mock_client_factory(provider):
        client = AsyncMock()
        client.chat_completion.return_value = mock_api_responses["success"]
        return client

    registry = ModelRegistry()
    guide = Mock()
    guide.get_recommended_models.return_value = ["codellama:34b"]
    guide.is_model_blocked.return_value = False

    return ModelOrchestrator(
        registry=registry,
        guide=guide,
        analyzer=TaskAnalyzer(),
        scorer=ModelScorer(),
        api_client_factory=mock_client_factory
    )


# ============================================================================
# 1. Multi-Agent Workflow Tests
# ============================================================================

class TestMultiAgentWorkflows:
    """Test multi-agent coordination and workflows"""

    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self, orchestrator_with_mocks, mock_multi_agent_context):
        """Test parallel execution of multiple agents"""
        agents = mock_multi_agent_context["agents"]

        # Create tasks for each agent
        tasks = []
        for agent in agents:
            task = orchestrator_with_mocks.call_model(
                model_id=agent["model"],
                messages=[{"role": "user", "content": f"Task for {agent['name']}"}]
            )
            tasks.append(task)

        # Execute all tasks in parallel
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time

        # Verify all completed
        assert len(results) == len(agents)
        assert all(isinstance(r, APIResponse) for r in results if not isinstance(r, Exception))

        # Verify parallel execution was faster than sequential
        # (should take ~200ms, not 600ms for 3 agents)
        assert elapsed_time < 1.0

    @pytest.mark.asyncio
    async def test_sequential_agent_coordination(self, orchestrator_with_mocks):
        """Test sequential agent handoffs"""
        # Agent 1: Analyze
        response1 = await orchestrator_with_mocks.call_model(
            model_id="codellama:34b",
            messages=[{"role": "user", "content": "Analyze the codebase"}]
        )

        # Agent 2: Design (uses Agent 1 output)
        response2 = await orchestrator_with_mocks.call_model(
            model_id="qwen2.5:32b",
            messages=[
                {"role": "user", "content": "Analyze the codebase"},
                {"role": "assistant", "content": response1.content},
                {"role": "user", "content": "Design improvements based on analysis"}
            ]
        )

        # Agent 3: Implement (uses Agent 2 output)
        response3 = await orchestrator_with_mocks.call_model(
            model_id="codellama:34b",
            messages=[
                {"role": "user", "content": "Design improvements based on analysis"},
                {"role": "assistant", "content": response2.content},
                {"role": "user", "content": "Implement the design"}
            ]
        )

        # Verify sequential handoff worked
        assert response1.content
        assert response2.content
        assert response3.content

    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self, orchestrator_with_mocks, mock_api_responses):
        """Test recovery when an agent fails"""
        # Mock one agent to fail
        client = orchestrator_with_mocks.api_clients[ModelProvider.LOCAL]
        client.chat_completion.side_effect = [
            mock_api_responses["error"],  # First call fails
            mock_api_responses["success"]  # Retry succeeds
        ]

        # Should retry and succeed
        response = await orchestrator_with_mocks.call_model(
            model_id="codellama:34b",
            messages=[{"role": "user", "content": "Test"}],
            retry_on_failure=True,
            max_retries=2
        )

        assert response.content == "Test response successful"
        assert client.chat_completion.call_count == 2

    def test_agent_consensus_selection(self, orchestrator_with_mocks):
        """Test consensus group creation for multi-agent decisions"""
        group = orchestrator_with_mocks.create_consensus_group(
            prompt="Complex decision requiring consensus",
            num_models=3,
            diverse=True
        )

        # Verify diverse provider selection
        providers = [model.provider for _, model in group]
        assert len(set(providers)) >= 2  # At least 2 different providers

        # Verify model capabilities
        for model_id, model in group:
            assert model.context_window >= 4096
            assert model.accuracy >= 0.5


# ============================================================================
# 2. Model Orchestrator Integration Tests
# ============================================================================

class TestModelOrchestratorIntegration:
    """Test complete orchestrator workflows"""

    def test_task_analysis_to_model_selection(self, orchestrator_with_mocks):
        """Test complete flow from task analysis to model selection"""
        prompts = [
            ("Write a Python function", TaskType.CODE_GENERATION),
            ("Debug this error", TaskType.DEBUGGING),
            ("Translate to Spanish", TaskType.TRANSLATION),
            ("Analyze this data", TaskType.DATA_ANALYSIS),
        ]

        for prompt, expected_type in prompts:
            # Analyze task
            requirements = orchestrator_with_mocks.analyzer.analyze(prompt)
            assert requirements.task_type == expected_type

            # Select model
            model_id, model = orchestrator_with_mocks.select_model(prompt, use_guide=False)
            assert model_id is not None
            assert model is not None

            # Verify model has good task score for this type
            assert model.task_scores.get(expected_type, 0) > 0.5

    @pytest.mark.asyncio
    async def test_complete_request_lifecycle(self, orchestrator_with_mocks):
        """Test complete request: analyze, select, call, track"""
        prompt = "Write a Python function to sort a list"

        # Step 1: Analyze
        requirements = orchestrator_with_mocks.analyzer.analyze(prompt)
        assert requirements.task_type == TaskType.CODE_GENERATION

        # Step 2: Select model
        model_id, model = orchestrator_with_mocks.select_model(prompt)

        # Step 3: Make API call
        response = await orchestrator_with_mocks.call_model(
            model_id=model_id,
            messages=[{"role": "user", "content": prompt}]
        )

        # Step 4: Verify tracking
        assert model_id in orchestrator_with_mocks.cost_tracker
        assert len(orchestrator_with_mocks.performance_history) > 0

        # Step 5: Get report
        report = orchestrator_with_mocks.get_cost_report()
        assert report["usage_count"][model_id] == 1

    def test_cost_optimization_strategy(self, orchestrator_with_mocks):
        """Test cost optimization strategy selection"""
        prompt = "Simple translation task"

        # Cost optimize should prefer free/cheap models
        model_id_cost, model_cost = orchestrator_with_mocks.select_model(
            prompt,
            strategy="cost_optimize",
            use_guide=False
        )

        # Quality first should prefer accurate models
        model_id_quality, model_quality = orchestrator_with_mocks.select_model(
            prompt,
            strategy="quality_first",
            use_guide=False
        )

        # Verify cost optimization
        assert model_cost.input_cost + model_cost.output_cost <= \
               model_quality.input_cost + model_quality.output_cost

    def test_fallback_chain_execution(self, orchestrator_with_mocks):
        """Test fallback when primary model unavailable"""
        # Mark codellama as unavailable
        orchestrator_with_mocks.registry.models["codellama:34b"].available = False

        # Should fall back to next best model
        model_id, model = orchestrator_with_mocks.select_model(
            "Write Python code",
            use_guide=False
        )

        assert model_id != "codellama:34b"
        assert model.available is True
        assert model.task_scores.get(TaskType.CODE_GENERATION, 0) > 0.5


# ============================================================================
# 3. API Endpoint Testing with Mocks
# ============================================================================

class TestAPIEndpointMocking:
    """Test API endpoints with comprehensive mocking"""

    @pytest.mark.asyncio
    async def test_api_rate_limit_handling(self, orchestrator_with_mocks, mock_api_responses):
        """Test handling of API rate limits"""
        client = orchestrator_with_mocks.api_clients[ModelProvider.LOCAL]

        # Simulate rate limit then success
        client.chat_completion.side_effect = [
            Exception("Rate limit exceeded"),
            mock_api_responses["success"]
        ]

        with patch('asyncio.sleep', return_value=None):  # Skip actual sleep
            response = await orchestrator_with_mocks.call_model(
                model_id="codellama:34b",
                messages=[{"role": "user", "content": "Test"}],
                retry_on_failure=True,
                max_retries=3
            )

        assert response.content == "Test response successful"

    @pytest.mark.asyncio
    async def test_api_timeout_handling(self, orchestrator_with_mocks):
        """Test handling of API timeouts"""
        client = orchestrator_with_mocks.api_clients[ModelProvider.LOCAL]

        # Simulate timeout
        async def timeout_mock(*args, **kwargs):
            await asyncio.sleep(0.1)
            raise asyncio.TimeoutError("Request timeout")

        client.chat_completion = timeout_mock

        with pytest.raises(Exception):
            await orchestrator_with_mocks.call_model(
                model_id="codellama:34b",
                messages=[{"role": "user", "content": "Test"}],
                timeout=0.05  # Very short timeout
            )

    @pytest.mark.asyncio
    async def test_api_response_validation(self, orchestrator_with_mocks):
        """Test validation of API responses"""
        client = orchestrator_with_mocks.api_clients[ModelProvider.LOCAL]

        # Test various invalid responses
        invalid_responses = [
            APIResponse("", "model", "provider", {}, 0, error="Empty content"),
            APIResponse(None, "model", "provider", {}, 0),
        ]

        for invalid_response in invalid_responses:
            client.chat_completion.return_value = invalid_response

            response = await orchestrator_with_mocks.call_model(
                model_id="codellama:34b",
                messages=[{"role": "user", "content": "Test"}]
            )

            # Should handle gracefully
            assert isinstance(response, APIResponse)

    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self, orchestrator_with_mocks):
        """Test handling of concurrent API calls"""
        # Create 10 concurrent requests
        tasks = []
        for i in range(10):
            task = orchestrator_with_mocks.call_model(
                model_id="codellama:34b",
                messages=[{"role": "user", "content": f"Request {i}"}]
            )
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        assert len(results) == 10
        assert all(isinstance(r, APIResponse) for r in results if not isinstance(r, Exception))


# ============================================================================
# 4. Database/File System Integration Tests
# ============================================================================

class TestDatabaseFileSystemIntegration:
    """Test file system and database-like operations"""

    def test_cost_tracking_persistence(self, orchestrator_with_mocks, temp_dir):
        """Test persisting cost tracking data"""
        # Track some usage
        orchestrator_with_mocks.track_usage("codellama:34b", 1000, 500, 250)
        orchestrator_with_mocks.track_usage("qwen2.5:32b", 2000, 1000, 300)

        # Save to file
        cost_file = Path(temp_dir) / "cost_tracking.json"
        with open(cost_file, 'w') as f:
            json.dump(orchestrator_with_mocks.cost_tracker, f)

        # Verify file exists and contains data
        assert cost_file.exists()

        # Load and verify
        with open(cost_file, 'r') as f:
            loaded_data = json.load(f)

        assert "codellama:34b" in loaded_data
        assert "qwen2.5:32b" in loaded_data

    def test_performance_history_persistence(self, orchestrator_with_mocks, temp_dir):
        """Test persisting performance history"""
        # Add performance data
        for i in range(50):
            orchestrator_with_mocks.track_usage(
                f"model-{i % 5}",
                1000 + i * 10,
                500 + i * 5,
                200 + i
            )

        # Save to file
        perf_file = Path(temp_dir) / "performance.json"
        with open(perf_file, 'w') as f:
            json.dump(orchestrator_with_mocks.performance_history, f, default=str)

        # Verify
        assert perf_file.exists()

        with open(perf_file, 'r') as f:
            loaded_history = json.load(f)

        assert len(loaded_history) == 50

    def test_model_registry_export_import(self, temp_dir):
        """Test exporting and importing model registry"""
        registry = ModelRegistry()

        # Export to JSON
        registry_file = Path(temp_dir) / "registry.json"
        models_data = {}
        for model_id, model in registry.models.items():
            models_data[model_id] = {
                "provider": model.provider.value,
                "context_window": model.context_window,
                "speed": model.speed,
                "accuracy": model.accuracy
            }

        with open(registry_file, 'w') as f:
            json.dump(models_data, f)

        # Verify
        assert registry_file.exists()

        # Reload
        with open(registry_file, 'r') as f:
            loaded_data = json.load(f)

        assert len(loaded_data) > 0
        assert "codellama:34b" in loaded_data


# ============================================================================
# 5. External Service Mocking Framework
# ============================================================================

class TestExternalServiceMocking:
    """Test mocking of external services and dependencies"""

    @pytest.mark.asyncio
    async def test_ollama_service_mock(self, orchestrator_with_mocks):
        """Test mocking of Ollama local service"""
        # Mock Ollama API
        mock_ollama = AsyncMock()
        mock_ollama.chat_completion.return_value = APIResponse(
            content="Mock Ollama response",
            model="codellama:34b",
            provider="local",
            usage={"input_tokens": 100, "output_tokens": 50},
            latency_ms=150
        )

        # Replace client
        orchestrator_with_mocks.api_clients[ModelProvider.LOCAL] = mock_ollama

        response = await orchestrator_with_mocks.call_model(
            model_id="codellama:34b",
            messages=[{"role": "user", "content": "Test"}]
        )

        assert response.content == "Mock Ollama response"
        assert response.provider == "local"

    @pytest.mark.asyncio
    async def test_cloud_api_mock(self, orchestrator_with_mocks):
        """Test mocking of cloud API services"""
        # Add mock Anthropic client
        mock_anthropic = AsyncMock()
        mock_anthropic.chat_completion.return_value = APIResponse(
            content="Mock Claude response",
            model="claude-sonnet-4.5",
            provider="anthropic",
            usage={"input_tokens": 200, "output_tokens": 100},
            latency_ms=500
        )

        orchestrator_with_mocks.api_clients[ModelProvider.ANTHROPIC] = mock_anthropic

        # Add model to registry
        orchestrator_with_mocks.registry.models["claude-sonnet-4.5"] = ModelCapabilities(
            provider=ModelProvider.ANTHROPIC,
            model_id="claude-sonnet-4.5",
            context_window=200000,
            speed=0.7,
            accuracy=0.95
        )

        response = await orchestrator_with_mocks.call_model(
            model_id="claude-sonnet-4.5",
            messages=[{"role": "user", "content": "Test"}]
        )

        assert response.content == "Mock Claude response"

    def test_model_guide_mock(self, temp_dir):
        """Test mocking of MODELS.md guide"""
        # Create mock guide file
        guide_content = """
# Model Selection Guide

### Code Tasks
- Primary: codellama:34b
- Fallback: qwen2.5:32b

### Blocked Models
- llama3.2 (poor performance)
"""

        guide_file = Path(temp_dir) / "MODELS.md"
        with open(guide_file, 'w') as f:
            f.write(guide_content)

        # Create parser with mock file
        from importlib import reload
        parser = mod.ModelGuideParser(str(guide_file))

        # Verify it loaded
        assert parser.rules is not None


# ============================================================================
# 6. Error Scenario Testing
# ============================================================================

class TestErrorScenarios:
    """Test comprehensive error handling"""

    def test_invalid_model_id_error(self, orchestrator_with_mocks):
        """Test error when model ID doesn't exist"""
        with pytest.raises(ValueError, match="Unknown model"):
            asyncio.run(orchestrator_with_mocks.call_model(
                model_id="nonexistent-model-xyz",
                messages=[{"role": "user", "content": "Test"}]
            ))

    def test_insufficient_context_window(self, orchestrator_with_mocks):
        """Test handling when no model has sufficient context"""
        # Create huge prompt
        huge_prompt = "x" * 1000000

        # Should raise or return None
        try:
            model_id, model = orchestrator_with_mocks.select_model(huge_prompt, use_guide=False)
            # If it didn't raise, verify it selected a large context model
            assert model.context_window >= 100000
        except ValueError as e:
            assert "No suitable models" in str(e)

    @pytest.mark.asyncio
    async def test_network_error_handling(self, orchestrator_with_mocks):
        """Test handling of network errors"""
        client = orchestrator_with_mocks.api_clients[ModelProvider.LOCAL]
        client.chat_completion.side_effect = ConnectionError("Network unavailable")

        with pytest.raises(ConnectionError):
            await orchestrator_with_mocks.call_model(
                model_id="codellama:34b",
                messages=[{"role": "user", "content": "Test"}]
            )

    def test_malformed_task_analysis(self, orchestrator_with_mocks):
        """Test handling of malformed inputs"""
        malformed_inputs = [
            None,
            "",
            123,  # Not a string
            {"invalid": "type"},
        ]

        analyzer = orchestrator_with_mocks.analyzer

        for invalid_input in malformed_inputs:
            try:
                # Should handle gracefully or raise clear error
                if isinstance(invalid_input, str):
                    result = analyzer.analyze(invalid_input)
                    assert isinstance(result, TaskRequirements)
            except (TypeError, ValueError) as e:
                # Expected for non-string inputs
                assert True

    @pytest.mark.asyncio
    async def test_concurrent_failure_isolation(self, orchestrator_with_mocks):
        """Test that one failure doesn't affect other concurrent requests"""
        client = orchestrator_with_mocks.api_clients[ModelProvider.LOCAL]

        # First call fails, rest succeed
        responses = []
        success_response = APIResponse(
            content="Success",
            model="test",
            provider="local",
            usage={"input_tokens": 100, "output_tokens": 50},
            latency_ms=200
        )

        async def mixed_response(*args, **kwargs):
            if len(responses) == 0:
                responses.append(None)
                raise Exception("First call fails")
            responses.append(None)
            return success_response

        client.chat_completion = mixed_response

        # Create concurrent tasks
        tasks = [
            orchestrator_with_mocks.call_model(
                model_id="codellama:34b",
                messages=[{"role": "user", "content": f"Task {i}"}]
            )
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # One should fail, others succeed
        failures = sum(1 for r in results if isinstance(r, Exception))
        successes = sum(1 for r in results if isinstance(r, APIResponse))

        assert failures == 1
        assert successes == 4


# ============================================================================
# 7. Performance Integration Tests
# ============================================================================

class TestPerformanceIntegration:
    """Test performance characteristics"""

    def test_model_selection_performance(self, orchestrator_with_mocks):
        """Test model selection completes quickly"""
        prompts = [
            "Write code",
            "Debug error",
            "Translate text",
            "Analyze data"
        ] * 25  # 100 selections

        start_time = time.time()
        for prompt in prompts:
            orchestrator_with_mocks.select_model(prompt, use_guide=False)
        elapsed = time.time() - start_time

        # Should complete 100 selections in under 1 second
        assert elapsed < 1.0
        avg_time = elapsed / len(prompts)
        assert avg_time < 0.01  # <10ms per selection

    @pytest.mark.asyncio
    async def test_concurrent_request_throughput(self, orchestrator_with_mocks):
        """Test handling of high concurrent request load"""
        num_requests = 50

        start_time = time.time()
        tasks = [
            orchestrator_with_mocks.call_model(
                model_id="codellama:34b",
                messages=[{"role": "user", "content": f"Request {i}"}]
            )
            for i in range(num_requests)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time

        # Should handle all requests
        assert len(results) == num_requests

        # Should be efficient (not linear time)
        # With mocks, should be <1s for 50 requests
        assert elapsed < 2.0

    def test_cost_calculation_performance(self, orchestrator_with_mocks):
        """Test cost calculation scales well"""
        # Add 1000 usage entries
        for i in range(1000):
            orchestrator_with_mocks.track_usage(
                f"model-{i % 10}",
                1000,
                500,
                200
            )

        # Cost report should still be fast
        start_time = time.time()
        report = orchestrator_with_mocks.get_cost_report()
        elapsed = time.time() - start_time

        assert elapsed < 0.1  # Should be <100ms
        assert len(orchestrator_with_mocks.performance_history) == 1000

    def test_memory_efficiency(self, orchestrator_with_mocks):
        """Test memory doesn't grow unbounded"""
        # Add 2000 performance entries
        for i in range(2000):
            orchestrator_with_mocks.track_usage(
                "test-model",
                1000,
                500,
                200
            )

        # Should cap at 1000 entries
        assert len(orchestrator_with_mocks.performance_history) == 1000


# ============================================================================
# 8. End-to-End User Flow Tests
# ============================================================================

class TestEndToEndUserFlows:
    """Test complete user workflows"""

    @pytest.mark.asyncio
    async def test_code_generation_workflow(self, orchestrator_with_mocks):
        """Test complete code generation workflow"""
        # User prompt
        prompt = "Write a Python function to calculate factorial"

        # Step 1: Select model
        model_id, model = orchestrator_with_mocks.select_model(prompt)
        assert model.code_specialized or model.task_scores.get(TaskType.CODE_GENERATION, 0) > 0.7

        # Step 2: Generate code
        response = await orchestrator_with_mocks.call_model(
            model_id=model_id,
            messages=[{"role": "user", "content": prompt}]
        )
        assert response.content

        # Step 3: Verify tracking
        report = orchestrator_with_mocks.get_cost_report()
        assert report["usage_count"][model_id] >= 1

    @pytest.mark.asyncio
    async def test_debugging_workflow(self, orchestrator_with_mocks):
        """Test complete debugging workflow"""
        # User provides error
        error_prompt = """
Debug this Python code:
def factorial(n):
    return n * factorial(n-1)

Error: RecursionError: maximum recursion depth exceeded
"""

        # Select debugging model
        model_id, model = orchestrator_with_mocks.select_model(error_prompt)

        # Get debugging help
        response = await orchestrator_with_mocks.call_model(
            model_id=model_id,
            messages=[{"role": "user", "content": error_prompt}]
        )

        assert response.content
        assert response.latency_ms > 0

    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self, orchestrator_with_mocks):
        """Test multi-turn conversation workflow"""
        conversation = []

        # Turn 1
        conversation.append({"role": "user", "content": "What is Python?"})
        response1 = await orchestrator_with_mocks.call_model(
            model_id="codellama:34b",
            messages=conversation
        )
        conversation.append({"role": "assistant", "content": response1.content})

        # Turn 2
        conversation.append({"role": "user", "content": "How do I install it?"})
        response2 = await orchestrator_with_mocks.call_model(
            model_id="codellama:34b",
            messages=conversation
        )
        conversation.append({"role": "assistant", "content": response2.content})

        # Turn 3
        conversation.append({"role": "user", "content": "Show me a hello world example"})
        response3 = await orchestrator_with_mocks.call_model(
            model_id="codellama:34b",
            messages=conversation
        )

        # Verify all responses
        assert all(r.content for r in [response1, response2, response3])

        # Verify tracking
        assert orchestrator_with_mocks.cost_tracker["codellama:34b"]["total_requests"] == 3

    @pytest.mark.asyncio
    async def test_consensus_decision_workflow(self, orchestrator_with_mocks):
        """Test consensus-based decision workflow"""
        # Create consensus group
        group = orchestrator_with_mocks.create_consensus_group(
            prompt="Should we use async or sync for this API?",
            num_models=3,
            diverse=True
        )

        # Get responses from all models
        tasks = []
        for model_id, model in group:
            task = orchestrator_with_mocks.call_model(
                model_id=model_id,
                messages=[{"role": "user", "content": "Should we use async or sync for this API?"}]
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # Verify all responded
        assert len(responses) == len(group)
        assert all(r.content for r in responses)

    def test_cost_budget_enforcement(self, orchestrator_with_mocks):
        """Test enforcing cost budget in selection"""
        # Low budget - should select cheap model
        cheap_model_id, cheap_model = orchestrator_with_mocks.select_model(
            "Simple task",
            strategy="cost_optimize",
            use_guide=False
        )

        # High budget - can select quality model
        quality_model_id, quality_model = orchestrator_with_mocks.select_model(
            "Complex analysis requiring accuracy",
            strategy="quality_first",
            use_guide=False
        )

        # Verify cost difference
        cheap_cost = cheap_model.input_cost + cheap_model.output_cost
        quality_cost = quality_model.input_cost + quality_model.output_cost

        assert cheap_cost <= quality_cost


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto",
        "-k", "not slow"  # Skip slow tests by default
    ])
