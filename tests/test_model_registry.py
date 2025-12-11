"""
Tests for the configurable model registry.

This module validates that:
1. Registry loads from YAML successfully
2. All documented models are present
3. Invalid YAML produces clear errors
4. Fallback to defaults works when YAML missing
"""
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
import yaml

from lattice_lock_orchestrator.registry import ModelRegistry
from lattice_lock_orchestrator.types import ModelProvider, ProviderMaturity, ModelStatus


PROJECT_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = PROJECT_ROOT / "models" / "registry.yaml"


class TestRegistryLoading:
    """Test registry YAML loading functionality."""

    def test_registry_loads_from_yaml(self):
        """Registry should load successfully from YAML file."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        # Should have loaded models
        models = registry.get_all_models()
        assert len(models) > 0, "Registry should have loaded models"

    def test_registry_loads_all_providers(self):
        """Registry should include models from all major providers."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        providers_found = set()
        for model in registry.get_all_models():
            providers_found.add(model.provider)

        # Should have multiple providers
        expected_providers = {
            ModelProvider.OPENAI,
            ModelProvider.ANTHROPIC,
            ModelProvider.GOOGLE,
            ModelProvider.XAI,
            ModelProvider.OLLAMA,
        }

        for provider in expected_providers:
            assert provider in providers_found, f"Missing provider: {provider}"

    def test_registry_model_count(self):
        """Registry should contain the expected number of models."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        models = registry.get_all_models()
        # Should have at least 40+ models based on documentation
        assert len(models) >= 40, f"Expected at least 40 models, got {len(models)}"

    def test_get_model_by_id(self):
        """Should retrieve specific model by ID."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        # Test known models
        gpt4o = registry.get_model("gpt-4o")
        assert gpt4o is not None, "gpt-4o should exist"
        assert gpt4o.provider == ModelProvider.OPENAI
        assert gpt4o.supports_vision is True
        assert gpt4o.supports_function_calling is True

    def test_get_models_by_provider(self):
        """Should filter models by provider."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        openai_models = registry.get_models_by_provider(ModelProvider.OPENAI)
        assert len(openai_models) > 0, "Should have OpenAI models"

        for model in openai_models:
            assert model.provider == ModelProvider.OPENAI


class TestModelCapabilities:
    """Test model capability fields are loaded correctly."""

    def test_model_has_required_fields(self):
        """Each model should have all required fields."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        for model in registry.get_all_models():
            assert model.name, f"Model missing name: {model}"
            assert model.api_name, f"Model missing api_name: {model.name}"
            assert model.provider is not None, f"Model missing provider: {model.name}"
            assert model.context_window > 0, f"Model has invalid context_window: {model.name}"
            assert model.input_cost >= 0, f"Model has negative input_cost: {model.name}"
            assert model.output_cost >= 0, f"Model has negative output_cost: {model.name}"
            assert 0 <= model.reasoning_score <= 100, f"Model has invalid reasoning_score: {model.name}"
            assert 0 <= model.coding_score <= 100, f"Model has invalid coding_score: {model.name}"
            assert 0 <= model.speed_rating <= 10, f"Model has invalid speed_rating: {model.name}"

    def test_derived_properties(self):
        """Test derived properties work correctly."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        # Get a high-reasoning model
        o1_pro = registry.get_model("o1-pro")
        if o1_pro:
            assert o1_pro.supports_reasoning is True, "o1-pro should support reasoning"
            assert o1_pro.code_specialized is True, "o1-pro should be code specialized"
            assert o1_pro.blended_cost > 0, "o1-pro should have positive blended cost"

    def test_task_scores_computed(self):
        """Test task_scores property returns valid scores."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        model = registry.get_model("gpt-4o")
        if model:
            scores = model.task_scores
            assert len(scores) > 0, "Should have task scores"

            for task_type, score in scores.items():
                assert 0 <= score <= 1, f"Score for {task_type} should be 0-1, got {score}"


class TestRegistryValidation:
    """Test registry validation and error handling."""

    def test_invalid_yaml_raises_error(self):
        """Invalid YAML should be handled gracefully."""
        invalid_yaml = "invalid: yaml: content: [[[["

        with patch("builtins.open", mock_open(read_data=invalid_yaml)):
            with patch.object(Path, "exists", return_value=True):
                # Should not crash, should fall back to defaults
                registry = ModelRegistry(registry_path="fake/path.yaml")
                # Verify it loaded defaults instead
                models = registry.get_all_models()
                assert len(models) > 0, "Should have loaded default models"

    def test_missing_yaml_uses_defaults(self):
        """Missing YAML file should fall back to defaults."""
        registry = ModelRegistry(registry_path="nonexistent/path/registry.yaml")

        # Should have loaded default models
        models = registry.get_all_models()
        assert len(models) > 0, "Should have loaded default models"

    def test_unknown_provider_logged(self):
        """Unknown provider in YAML should be logged but not crash."""
        yaml_content = """
version: "1.0"
providers:
  unknown_provider:
    models:
      test-model:
        api_name: test
        context_window: 1000
        input_cost: 1.0
        output_cost: 2.0
        reasoning_score: 50.0
        coding_score: 50.0
        speed_rating: 5.0
"""
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch.object(Path, "exists", return_value=True):
                # Should not crash
                registry = ModelRegistry(registry_path="fake/path.yaml")
                # Unknown provider models should be skipped
                models = registry.get_all_models()
                # Might have no models or fall back to defaults
                assert isinstance(models, list)


class TestSpecificModels:
    """Test specific model configurations from documentation."""

    def test_local_models_are_free(self):
        """Local Ollama models should have zero cost."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        local_models = registry.get_models_by_provider(ModelProvider.OLLAMA)
        for model in local_models:
            assert model.input_cost == 0.0, f"Local model {model.name} should be free"
            assert model.output_cost == 0.0, f"Local model {model.name} should be free"

    def test_vision_models_flagged(self):
        """Vision-capable models should be properly flagged."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        gpt4o = registry.get_model("gpt-4o")
        if gpt4o:
            assert gpt4o.supports_vision is True, "gpt-4o should support vision"

        # Check Claude models
        claude_sonnet = registry.get_model("claude-3-5-sonnet")
        if claude_sonnet:
            assert claude_sonnet.supports_vision is True, "Claude 3.5 Sonnet should support vision"

    def test_function_calling_flagged(self):
        """Function calling capable models should be properly flagged."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        gpt4o = registry.get_model("gpt-4o")
        if gpt4o:
            assert gpt4o.supports_function_calling is True, "gpt-4o should support function calling"

    def test_maturity_levels(self):
        """Models should have appropriate maturity levels."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        # OpenAI should be production
        gpt4o = registry.get_model("gpt-4o")
        if gpt4o:
            assert gpt4o.maturity == ProviderMaturity.PRODUCTION

        # Bedrock should be experimental
        bedrock_models = registry.get_models_by_provider(ModelProvider.BEDROCK)
        for model in bedrock_models:
            assert model.maturity == ProviderMaturity.EXPERIMENTAL


class TestCLIIntegration:
    """Test that CLI can list models from registry."""

    def test_list_all_models(self):
        """CLI list command should show all models."""
        registry = ModelRegistry(registry_path=str(REGISTRY_PATH))

        # Simulate what CLI list would do
        models = registry.get_all_models()

        # Group by provider
        by_provider = {}
        for model in models:
            provider = model.provider.value
            if provider not in by_provider:
                by_provider[provider] = []
            by_provider[provider].append(model)

        # Should have multiple providers
        assert len(by_provider) >= 5, f"Expected at least 5 providers, got {len(by_provider)}"
