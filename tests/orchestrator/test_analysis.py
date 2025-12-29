"""
Tests for Task Analyzer.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from lattice_lock.config import AppConfig
from lattice_lock.orchestrator.analysis.analyzer import TaskAnalyzer
from lattice_lock.orchestrator.analysis.types import TaskAnalysis
from lattice_lock.orchestrator.types import TaskType


@pytest.fixture
def mock_config():
    return Mock(spec=AppConfig, analyzer_cache_size=100)


def test_analyzer_initialization(mock_config):
    """Test analyzer loads patterns correctly."""
    analyzer = TaskAnalyzer(config=mock_config)
    assert analyzer._keyword_patterns
    assert analyzer._regex_patterns


def test_analyze_simple_code(mock_config):
    """Test analyzing a simple coding task."""
    analyzer = TaskAnalyzer(config=mock_config)
    prompt = "Write a python function to Fibonacci sequence"
    
    analysis = analyzer.analyze_full(prompt)
    assert analysis.primary_type == TaskType.CODE_GENERATION
    assert analysis.features["has_code_blocks"] is False # No backticks
    assert "function" in prompt


def test_analyze_with_code_block(mock_config):
    """Test analyzing prompt with code block."""
    analyzer = TaskAnalyzer(config=mock_config)
    prompt = """Debug this code:
    ```python
    def foo(): pass
    ```
    It has an error.
    """
    
    analysis = analyzer.analyze_full(prompt)
    assert analysis.features["has_code_blocks"] is True
    # Should probably match debugging or code gen
    assert analysis.primary_type in (TaskType.DEBUGGING, TaskType.CODE_GENERATION)


@pytest.mark.asyncio
async def test_analyze_async(mock_config):
    """Test async analysis entry point."""
    analyzer = TaskAnalyzer(config=mock_config)
    prompt = "Explain quantum physics"
    
    requirements = await analyzer.analyze_async(prompt)
    # Explanation -> Reasoning likely
    assert requirements.task_type in (TaskType.REASONING, TaskType.GENERAL)


def test_caching_behavior(mock_config):
    """Test that results are cached."""
    analyzer = TaskAnalyzer(config=mock_config)
    prompt = "Repeatable prompt"
    
    # First call
    _ = analyzer.analyze_full(prompt)
    assert analyzer._cache_hits == 0
    assert analyzer._cache_misses == 1
    
    # Second call
    _ = analyzer.analyze_full(prompt)
    assert analyzer._cache_hits == 1
    assert analyzer._cache_misses == 1
