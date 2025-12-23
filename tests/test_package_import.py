"""
Tests for package imports and exports.

Verifies that the lattice_lock package exports all expected symbols
and that the version is correctly read from version.txt.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestPackageVersion:
    """Tests for package version management."""

    def test_version_is_string(self):
        """Version should be a string."""
        from lattice_lock import __version__

        assert isinstance(__version__, str)

    def test_version_matches_version_txt(self):
        """Version should match the content of version.txt."""
        from lattice_lock import __version__

        version_file = Path(__file__).parent.parent / "version.txt"
        expected_version = version_file.read_text().strip()
        assert __version__ == expected_version

    def test_version_format(self):
        """Version should follow semantic versioning format."""
        from lattice_lock import __version__

        parts = __version__.split(".")
        assert len(parts) >= 2, "Version should have at least major.minor"
        for part in parts:
            cleaned = part.replace("-", "").replace("alpha", "")
            cleaned = cleaned.replace("beta", "").replace("rc", "")
            assert part.isdigit() or cleaned.isdigit()


class TestPackageExports:
    """Tests for package exports from lattice_lock."""

    def test_model_orchestrator_export(self):
        """ModelOrchestrator should be importable from lattice_lock."""
        from lattice_lock import ModelOrchestrator

        assert ModelOrchestrator is not None

    def test_task_type_export(self):
        """TaskType should be importable from lattice_lock."""
        from lattice_lock import TaskType

        assert TaskType is not None

    def test_model_provider_export(self):
        """ModelProvider should be importable from lattice_lock."""
        from lattice_lock import ModelProvider

        assert ModelProvider is not None

    def test_api_response_export(self):
        """APIResponse should be importable from lattice_lock."""
        from lattice_lock import APIResponse

        assert APIResponse is not None

    def test_model_registry_export(self):
        """ModelRegistry should be importable from lattice_lock."""
        from lattice_lock import ModelRegistry

        assert ModelRegistry is not None

    def test_model_scorer_export(self):
        """ModelScorer should be importable from lattice_lock."""
        from lattice_lock import ModelScorer

        assert ModelScorer is not None

    def test_task_analyzer_export(self):
        """TaskAnalyzer should be importable from lattice_lock."""
        from lattice_lock import TaskAnalyzer

        assert TaskAnalyzer is not None


class TestTypesModuleExports:
    """Tests for exports from lattice_lock.types module."""

    def test_task_type_from_types(self):
        """TaskType should be importable from lattice_lock.types."""
        from lattice_lock.types import TaskType

        assert TaskType is not None

    def test_task_requirements_from_types(self):
        """TaskRequirements should be importable from lattice_lock.types."""
        from lattice_lock.types import TaskRequirements

        assert TaskRequirements is not None

    def test_model_provider_from_types(self):
        """ModelProvider should be importable from lattice_lock.types."""
        from lattice_lock.types import ModelProvider

        assert ModelProvider is not None

    def test_model_capabilities_from_types(self):
        """ModelCapabilities should be importable from lattice_lock.types."""
        from lattice_lock.types import ModelCapabilities

        assert ModelCapabilities is not None

    def test_api_response_from_types(self):
        """APIResponse should be importable from lattice_lock.types."""
        from lattice_lock.types import APIResponse

        assert APIResponse is not None


class TestAllExports:
    """Tests for __all__ exports."""

    def test_lattice_lock_all_exports(self):
        """All items in __all__ should be importable."""
        import lattice_lock

        for name in lattice_lock.__all__:
            assert hasattr(lattice_lock, name), f"{name} in __all__ but not accessible"

    def test_types_all_exports(self):
        """All items in types.__all__ should be importable."""
        from lattice_lock import types

        for name in types.__all__:
            assert hasattr(types, name), f"{name} in types.__all__ but not accessible"


class TestOrchestratorPackageExports:
    """Tests for exports from lattice_lock.orchestrator package."""

    def test_orchestrator_version_matches(self):
        """Orchestrator version should match lattice_lock version."""
        from lattice_lock import __version__ as lattice_version
        from lattice_lock.orchestrator import __version__ as orchestrator_version

        assert lattice_version == orchestrator_version

    def test_orchestrator_exports(self):
        """Core exports should be available from lattice_lock.orchestrator."""
        from lattice_lock.orchestrator import (
            APIResponse,
            ModelOrchestrator,
            ModelProvider,
            ModelRegistry,
            ModelScorer,
            TaskAnalyzer,
            TaskType,
        )

        assert ModelOrchestrator is not None
        assert TaskType is not None
        assert ModelProvider is not None
        assert APIResponse is not None
        assert ModelRegistry is not None
        assert ModelScorer is not None
        assert TaskAnalyzer is not None
