"""
Benchmarks for Lattice Lock Core Components.
"""

import pytest

from lattice_lock.orchestrator.core import ModelOrchestrator


@pytest.mark.benchmark(group="orchestrator")
def test_orchestrator_instantiation_benchmark(benchmark):
    """Benchmark the instantiation of ModelOrchestrator."""

    def _instantiate():
        return ModelOrchestrator()

    benchmark(_instantiate)


@pytest.mark.benchmark(group="orchestrator")
def test_route_request_overhead_benchmark(benchmark):
    """Benchmark overhead of route_request (mocked)."""
    # This is a stub benchmarks as actual routing involves network
    pass
