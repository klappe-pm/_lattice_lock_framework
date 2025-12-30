from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from lattice_lock.cli.__main__ import cli
from lattice_lock.orchestrator.types import APIResponse, TaskType, TokenUsage


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_response():
    return APIResponse(
        content="Hello world",
        model="gpt-4o",
        provider="openai",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15, cost=0.001),
        latency_ms=100,
    )


@patch("lattice_lock.cli.commands.ask.ModelOrchestrator")
def test_ask_basic(mock_orchestrator_cls, runner, mock_response):
    mock_orchestrator = mock_orchestrator_cls.return_value

    async def mock_route(*args, **kwargs):
        return mock_response

    mock_orchestrator.route_request.side_effect = mock_route

    result = runner.invoke(cli, ["ask", "Hello"])

    assert result.exit_code == 0
    assert "Hello world" in result.output
    assert "gpt-4o" in result.output


@patch("lattice_lock.cli.commands.ask.ModelOrchestrator")
def test_ask_verbose(mock_orchestrator_cls, runner, mock_response):
    mock_orchestrator = mock_orchestrator_cls.return_value

    async def mock_route(*args, **kwargs):
        return mock_response

    mock_orchestrator.route_request.side_effect = mock_route

    result = runner.invoke(cli, ["--verbose", "ask", "Hello"])

    assert result.exit_code == 0
    assert "Metadata" in result.output
    assert "openai" in result.output
    assert "0.0010" in result.output


@patch("lattice_lock.cli.commands.ask.ModelOrchestrator")
def test_ask_compare(mock_orchestrator_cls, runner, mock_response):
    mock_orchestrator = mock_orchestrator_cls.return_value

    # Mock analyzer
    mock_req = MagicMock()
    mock_req.task_type = TaskType.GENERAL

    async def mock_analyze(*args, **kwargs):
        return mock_req

    mock_orchestrator.analyzer.analyze_async.side_effect = mock_analyze

    # Mock registry and scorer
    mock_orchestrator.registry.models = {"gpt-4o": MagicMock()}
    mock_orchestrator.scorer.score.return_value = 0.9

    async def mock_route(*args, **kwargs):
        return mock_response

    mock_orchestrator.route_request.side_effect = mock_route

    result = runner.invoke(cli, ["ask", "Hello", "--compare"])

    assert result.exit_code == 0
    assert "Comparing 1 models" in result.output
    assert "Hello world" in result.output
    assert "gpt-4o" in result.output
