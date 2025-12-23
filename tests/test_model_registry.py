"""Tests for the ModelRegistry and registry validation.

This module validates that:
1. ModelRegistry loads models from YAML correctly
2. Registry validation catches errors and warnings
3. Model lookup by ID and provider works correctly
4. Fallback to defaults works when YAML is missing
"""

from pathlib import Path

from lattice_lock.orchestrator.registry import ModelRegistry, RegistryValidationResult
from lattice_lock.orchestrator.types import ModelProvider

PROJECT_ROOT = Path(__file__).parent.parent


class TestRegistryValidationResult:
    """Tests for the RegistryValidationResult dataclass."""

    def test_initial_state_is_valid(self):
        """Test that a new result starts as valid."""
        result = RegistryValidationResult()
        assert result.valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error_marks_invalid(self):
        """Test that adding an error marks the result as invalid."""
        result = RegistryValidationResult()
        result.add_error("Test error")

        assert not result.valid
        assert "Test error" in result.errors

    def test_add_warning_keeps_valid(self):
        """Test that adding a warning keeps the result valid."""
        result = RegistryValidationResult()
        result.add_warning("Test warning")

        assert result.valid
        assert "Test warning" in result.warnings


class TestModelRegistryLoading:
    """Tests for ModelRegistry loading functionality."""

    def test_loads_from_yaml(self):
        """Test that registry loads models from YAML file."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        assert len(registry.models) >= 55, "Should load models from YAML"

    def test_loads_all_providers(self):
        """Test that registry loads models from all providers."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        providers_with_models = set()
        for model in registry.get_all_models():
            providers_with_models.add(model.provider)

        assert len(providers_with_models) >= 5, "Should have models from at least 5 providers"

    def test_fallback_to_defaults_when_yaml_missing(self):
        """Test that registry falls back to defaults when YAML is missing."""
        registry = ModelRegistry(registry_path="nonexistent_file.yaml")

        assert len(registry.models) > 0, "Should fall back to default models"

    def test_fallback_to_defaults_when_path_is_none(self):
        """Test that registry falls back to defaults when path is None."""
        registry = ModelRegistry(registry_path=None)

        assert len(registry.models) > 0, "Should fall back to default models"


class TestModelRegistryValidation:
    """Tests for ModelRegistry validation functionality."""

    def test_validates_registry_yaml(self):
        """Test that registry validates the YAML file on load."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        assert registry.validation_result is not None, "Should have validation result"
        assert (
            registry.validation_result.valid
        ), f"Registry should be valid. Errors: {registry.validation_result.errors}"

    def test_validation_counts_models(self):
        """Test that validation counts models correctly."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        assert registry.validation_result.model_count > 0, "Should count models"
        assert registry.validation_result.model_count == len(
            registry.models
        ), "Model count should match loaded models"

    def test_validation_counts_providers(self):
        """Test that validation counts providers correctly."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        assert registry.validation_result.provider_count > 0, "Should count providers"

    def test_validates_missing_providers_section(self):
        """Test that validation catches missing providers section."""
        registry = ModelRegistry(registry_path=None)
        result = registry.validate_registry({"version": "1.0"})

        assert not result.valid
        assert any("providers" in e.lower() for e in result.errors)

    def test_validates_missing_required_fields(self):
        """Test that validation catches missing required fields."""
        registry = ModelRegistry(registry_path=None)
        result = registry.validate_registry(
            {
                "version": "1.0",
                "providers": {"openai": {"models": {"test-model": {"api_name": "test"}}}},
            }
        )

        assert not result.valid
        assert len(result.errors) > 0

    def test_validates_invalid_maturity(self):
        """Test that validation catches invalid maturity values."""
        registry = ModelRegistry(registry_path=None)
        result = registry.validate_registry(
            {
                "version": "1.0",
                "providers": {
                    "openai": {
                        "models": {
                            "test-model": {
                                "api_name": "test",
                                "context_window": 8000,
                                "input_cost": 1.0,
                                "output_cost": 2.0,
                                "reasoning_score": 80.0,
                                "coding_score": 80.0,
                                "speed_rating": 7.0,
                                "maturity": "INVALID_MATURITY",
                            }
                        }
                    }
                },
            }
        )

        assert not result.valid
        assert any("maturity" in e.lower() for e in result.errors)

    def test_validates_negative_cost(self):
        """Test that validation catches negative costs."""
        registry = ModelRegistry(registry_path=None)
        result = registry.validate_registry(
            {
                "version": "1.0",
                "providers": {
                    "openai": {
                        "models": {
                            "test-model": {
                                "api_name": "test",
                                "context_window": 8000,
                                "input_cost": -1.0,
                                "output_cost": 2.0,
                                "reasoning_score": 80.0,
                                "coding_score": 80.0,
                                "speed_rating": 7.0,
                            }
                        }
                    }
                },
            }
        )

        assert not result.valid
        # Pydantic error says "greater than or equal to 0" instead of "negative"
        assert any("input_cost" in e.lower() or "greater than" in e.lower() for e in result.errors)

    def test_warns_on_unknown_provider(self):
        """Test that validation warns on unknown providers."""
        registry = ModelRegistry(registry_path=None)
        result = registry.validate_registry(
            {
                "version": "1.0",
                "providers": {
                    "unknown_provider": {
                        "models": {
                            "test-model": {
                                "api_name": "test",
                                "context_window": 8000,
                                "input_cost": 1.0,
                                "output_cost": 2.0,
                                "reasoning_score": 80.0,
                                "coding_score": 80.0,
                                "speed_rating": 7.0,
                            }
                        }
                    }
                },
            }
        )

        assert any("unknown" in w.lower() for w in result.warnings)


class TestModelRegistryLookup:
    """Tests for ModelRegistry lookup functionality."""

    def test_get_model_by_id(self):
        """Test getting a model by its ID."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        model = registry.get_model("gpt-4o")
        assert model is not None, "Should find gpt-4o model"
        assert model.api_name == "gpt-4o"

    def test_get_model_returns_none_for_unknown(self):
        """Test that get_model returns None for unknown model ID."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        model = registry.get_model("nonexistent-model")
        assert model is None

    def test_get_models_by_provider(self):
        """Test getting all models for a provider."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        openai_models = registry.get_models_by_provider(ModelProvider.OPENAI)
        assert len(openai_models) > 0, "Should have OpenAI models"

        for model in openai_models:
            assert model.provider == ModelProvider.OPENAI

    def test_get_all_models(self):
        """Test getting all registered models."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        all_models = registry.get_all_models()
        assert len(all_models) > 0, "Should have models"
        assert len(all_models) == len(registry.models)


class TestModelCapabilitiesFromYAML:
    """Tests for model capabilities loaded from YAML."""

    def test_model_has_required_attributes(self):
        """Test that loaded models have all required attributes."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        for model_id, model in registry.models.items():
            assert model.name is not None, f"Model {model_id} should have name"
            assert model.api_name is not None, f"Model {model_id} should have api_name"
            assert model.provider is not None, f"Model {model_id} should have provider"
            assert model.context_window > 0, f"Model {model_id} should have positive context_window"
            assert model.input_cost >= 0, f"Model {model_id} should have non-negative input_cost"
            assert model.output_cost >= 0, f"Model {model_id} should have non-negative output_cost"

    def test_model_capabilities_are_booleans(self):
        """Test that model capabilities are boolean values."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        for model_id, model in registry.models.items():
            assert isinstance(
                model.supports_function_calling, bool
            ), f"Model {model_id} supports_function_calling should be bool"
            assert isinstance(
                model.supports_vision, bool
            ), f"Model {model_id} supports_vision should be bool"


class TestRegistryModelCount:
    """Tests for verifying the expected number of models in the registry."""

    def test_registry_has_expected_model_count(self):
        """Test that registry has a reasonable number of models."""

        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        assert (
            len(registry.models) >= 55
        ), f"Expected at least 60 models, got {len(registry.models)}"

    def test_registry_has_models_from_major_providers(self):
        """Test that registry has models from major providers."""
        registry = ModelRegistry(
            registry_path=str((PROJECT_ROOT / "docs" / "models" / "registry.yaml").resolve())
        )

        major_providers = [
            ModelProvider.OPENAI,
            ModelProvider.ANTHROPIC,
            ModelProvider.GOOGLE,
            ModelProvider.OLLAMA,
        ]

        for provider in major_providers:
            models = registry.get_models_by_provider(provider)
            assert len(models) > 0, f"Should have models from {provider.value}"
