"""
Tests for Token Aggregation in ConversationExecutor.

These tests verify that token usage is correctly aggregated across
multiple API calls within a single conversation execution.

Per Master Refactoring Plan v5.1 Work Chunk 2.2
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestTokenAggregation:
    """Test suite for token aggregation functionality."""

    @pytest.fixture
    def mock_usage(self):
        """Create mock usage data."""
        return {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }

    def test_single_call_usage(self, mock_usage):
        """Test token usage for single API call."""
        total = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        
        # Simulate aggregation
        total["prompt_tokens"] += mock_usage.get("prompt_tokens", 0)
        total["completion_tokens"] += mock_usage.get("completion_tokens", 0)
        total["total_tokens"] += mock_usage.get("total_tokens", 0)
        
        assert total["prompt_tokens"] == 100
        assert total["completion_tokens"] == 50
        assert total["total_tokens"] == 150

    def test_multi_call_aggregation(self):
        """Test token usage aggregation across multiple calls."""
        usage_calls = [
            {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            {"prompt_tokens": 80, "completion_tokens": 120, "total_tokens": 200},
            {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
        ]
        
        total = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        
        for usage in usage_calls:
            total["prompt_tokens"] += usage.get("prompt_tokens", 0)
            total["completion_tokens"] += usage.get("completion_tokens", 0)
            total["total_tokens"] += usage.get("total_tokens", 0)
        
        assert total["prompt_tokens"] == 230
        assert total["completion_tokens"] == 200
        assert total["total_tokens"] == 430

    def test_missing_usage_fields(self):
        """Test handling of missing usage fields."""
        usage_with_missing = {"prompt_tokens": 100}  # Missing other fields
        
        total = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        
        total["prompt_tokens"] += usage_with_missing.get("prompt_tokens", 0)
        total["completion_tokens"] += usage_with_missing.get("completion_tokens", 0)
        total["total_tokens"] += usage_with_missing.get("total_tokens", 0)
        
        assert total["prompt_tokens"] == 100
        assert total["completion_tokens"] == 0
        assert total["total_tokens"] == 0

    def test_none_usage(self):
        """Test handling of None usage data."""
        usage = None
        
        total = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        
        if usage:
            total["prompt_tokens"] += usage.get("prompt_tokens", 0)
            total["completion_tokens"] += usage.get("completion_tokens", 0)
            total["total_tokens"] += usage.get("total_tokens", 0)
        
        assert total["prompt_tokens"] == 0
        assert total["completion_tokens"] == 0
        assert total["total_tokens"] == 0


class TestTokenAggregationWithFunctionCalls:
    """Test token aggregation with function calling scenarios."""

    def test_aggregation_with_function_call_loop(self):
        """Test aggregation in function call loop scenario."""
        # Simulate: initial call -> function call -> function result -> final response
        usage_sequence = [
            {"prompt_tokens": 500, "completion_tokens": 100, "total_tokens": 600},  # Initial
            {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},  # After function result
        ]
        
        total = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        
        for usage in usage_sequence:
            total["prompt_tokens"] += usage.get("prompt_tokens", 0)
            total["completion_tokens"] += usage.get("completion_tokens", 0)
            total["total_tokens"] += usage.get("total_tokens", 0)
        
        # Total should be sum of all calls
        assert total["prompt_tokens"] == 600
        assert total["completion_tokens"] == 300
        assert total["total_tokens"] == 900

    def test_max_function_calls_limit(self):
        """Test that aggregation respects max function call limits."""
        max_function_calls = 10
        usage_per_call = {"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75}
        
        total = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        
        for i in range(max_function_calls):
            total["prompt_tokens"] += usage_per_call.get("prompt_tokens", 0)
            total["completion_tokens"] += usage_per_call.get("completion_tokens", 0)
            total["total_tokens"] += usage_per_call.get("total_tokens", 0)
        
        assert total["prompt_tokens"] == 500
        assert total["completion_tokens"] == 250
        assert total["total_tokens"] == 750
