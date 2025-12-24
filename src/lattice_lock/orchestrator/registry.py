import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .types import ModelCapabilities, ModelProvider, ProviderMaturity, TaskType, ModelStatus
from .exceptions import APIClientError

logger = logging.getLogger(__name__)


REQUIRED_MODEL_FIELDS = [
    "api_name",
    "context_window",
    "input_cost",
    "output_cost",
    "reasoning_score",
    "coding_score",
    "speed_rating",
]

VALID_MATURITY_VALUES = ["PRODUCTION", "BETA", "EXPERIMENTAL", "DEPRECATED"]
VALID_STATUS_VALUES = ["ACTIVE", "INACTIVE", "DEPRECATED"]
VALID_CAPABILITIES = ["function_calling", "vision"]


@dataclass
class RegistryValidationResult:
    """Result of registry validation."""

    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_count: int = 0
    provider_count: int = 0

    def add_error(self, error: str):
        """Add a validation error."""
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str):
        """Add a validation warning."""
        self.warnings.append(warning)


class ModelRegistry:
    """Centralized model registry with all model definitions"""

    def __init__(self, registry_path: str | None = "docs/models/registry.yaml"):
        self.models: dict[str, ModelCapabilities] = {}
        self.registry_path = registry_path
        self._validation_result: RegistryValidationResult | None = None
        self._load_all_models()

    @property
    def validation_result(self) -> RegistryValidationResult | None:
        """Get the validation result from the last load operation."""
        return self._validation_result

    def validate_registry(self, data: dict) -> RegistryValidationResult:
        """Validate registry data structure and content.

        Args:
            data: The parsed YAML registry data

        Returns:
            RegistryValidationResult with validation status, errors, and warnings
        """
        result = RegistryValidationResult()

        if not isinstance(data, dict):
            result.add_error("Registry data must be a dictionary")
            return result

        if "version" not in data:
            result.add_warning("Registry missing 'version' field")

        if "providers" not in data:
            result.add_error("Registry missing required 'providers' section")
            return result

        providers = data.get("providers", {})
        if not isinstance(providers, dict):
            result.add_error("'providers' must be a dictionary")
            return result

        result.provider_count = len(providers)

        for provider_name, provider_data in providers.items():
            if not isinstance(provider_data, dict):
                result.add_error(f"Provider '{provider_name}' data must be a dictionary")
                continue

            try:
                ModelProvider(provider_name.lower())
            except ValueError:
                result.add_warning(f"Unknown provider: {provider_name}")

            models = provider_data.get("models", {})
            if not isinstance(models, dict):
                result.add_error(f"Provider '{provider_name}' models must be a dictionary")
                continue

            for model_id, model_data in models.items():
                result.model_count += 1

                if not isinstance(model_data, dict):
                    result.add_error(f"Model '{model_id}' data must be a dictionary")
                    continue

                for field_name in REQUIRED_MODEL_FIELDS:
                    if field_name not in model_data:
                        result.add_error(f"Model '{model_id}' missing required field: {field_name}")

                if "context_window" in model_data:
                    if not isinstance(model_data["context_window"], int):
                        result.add_error(f"Model '{model_id}' context_window must be an integer")
        try:
            from .models_schema import RegistryConfig

            # Pydantic validation
            config = RegistryConfig.model_validate(data)
            result.model_count = len(config.models)
            result.provider_count = len(set(m.provider for m in config.models))
            return result
        except Exception as e:
            result.add_error(f"Schema validation failed: {str(e)}")
            return result

    def _calculate_default_scores(
        self, coding_score: float, reasoning_score: float, supports_vision: bool
    ) -> dict[TaskType, float]:
        """Calculate default task scores based on capabilities."""
        scores: dict[TaskType, float] = {}
        coding_norm = coding_score / 100.0
        reasoning_norm = reasoning_score / 100.0

        scores[TaskType.CODE_GENERATION] = coding_norm
        scores[TaskType.DEBUGGING] = coding_norm * 0.9 + reasoning_norm * 0.1
        scores[TaskType.ARCHITECTURAL_DESIGN] = reasoning_norm * 0.7 + coding_norm * 0.3
        scores[TaskType.DOCUMENTATION] = (coding_norm + reasoning_norm) / 2
        scores[TaskType.TESTING] = coding_norm * 0.8 + reasoning_norm * 0.2
        scores[TaskType.DATA_ANALYSIS] = reasoning_norm * 0.6 + coding_norm * 0.4
        scores[TaskType.GENERAL] = (coding_norm + reasoning_norm) / 2
        scores[TaskType.REASONING] = reasoning_norm
        scores[TaskType.VISION] = 1.0 if supports_vision else 0.0
        scores[TaskType.SECURITY_AUDIT] = coding_norm * 0.7 + reasoning_norm * 0.3
        scores[TaskType.CREATIVE_WRITING] = reasoning_norm * 0.8

        return scores

    def _load_all_models(self):
        """Load all models, preferring YAML config over defaults"""
        loaded_from_yaml = False
        if self.registry_path:
            loaded_from_yaml = self._load_from_yaml()

        if not loaded_from_yaml:
            logger.warning("Registry YAML not found or failed, falling back to defaults")
            self._load_defaults()

    def _load_from_yaml(self) -> bool:
        """Load models from registry.yaml with Pydantic validation."""
        path = Path(self.registry_path)
        if not path.exists():
            return False

        try:
            with open(path) as f:
                data = yaml.safe_load(f)

            # Validate with legacy validator first for validation_result
            self._validation_result = self.validate_registry(data)

            # Validate with Pydantic
            from .models_schema import RegistryConfig

            try:
                config = RegistryConfig.model_validate(data)
            except Exception as e:
                logger.error(f"Registry YAML validation failed: {e}")
                self._validation_result.add_error(str(e))
                return False

            # Transform to internal ModelCapabilities
            for model_cfg in config.models:
                try:
                    caps = self._create_model_caps(
                        model_id=model_cfg.id,
                        api_name=model_cfg.api_name or model_cfg.id,
                        provider=model_cfg.provider,
                        context_window=model_cfg.context_window,
                        input_cost=model_cfg.input_cost,
                        output_cost=model_cfg.output_cost,
                        reasoning_score=model_cfg.reasoning_score,
                        coding_score=model_cfg.coding_score,
                        speed_rating=model_cfg.speed_rating,
                        maturity=model_cfg.maturity,
                        status=model_cfg.status,
                        supports_function_calling=model_cfg.supports_function_calling,
                        supports_vision=model_cfg.supports_vision,
                        supports_json_mode=model_cfg.supports_json_mode,
                    )
                    self.models[model_cfg.id] = caps
                except Exception as e:
                    logger.error(f"Failed to load model {model_cfg.id}: {e}")

            logger.info(f"Loaded {len(self.models)} models from {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load registry YAML: {e}")
            return False

    def _create_model_caps(
        self,
        model_id: str,
        api_name: str,
        provider: ModelProvider,
        context_window: int,
        input_cost: float,
        output_cost: float,
        reasoning_score: float,
        coding_score: float,
        speed_rating: float,
        maturity: ProviderMaturity = ProviderMaturity.PRODUCTION,
        status: ModelStatus = ModelStatus.ACTIVE,
        supports_function_calling: bool = False,
        supports_vision: bool = False,
        supports_json_mode: bool = False,
        name: str | None = None,
    ) -> ModelCapabilities:
        """Helper to create ModelCapabilities with calculated task scores."""
        # Coerce strings to Enums if necessary
        if isinstance(status, str):
            try:
                status = ModelStatus[status.upper()]
            except KeyError:
                status = ModelStatus.ACTIVE
        
        if isinstance(maturity, str):
            try:
                maturity = ProviderMaturity[maturity.upper()]
            except KeyError:
                maturity = ProviderMaturity.BETA

        default_scores = self._calculate_default_scores(coding_score, reasoning_score, supports_vision)
        return ModelCapabilities(
            name=name or model_id,
            api_name=api_name,
            provider=provider,
            context_window=context_window,
            input_cost=input_cost,
            output_cost=output_cost,
            reasoning_score=reasoning_score,
            coding_score=coding_score,
            speed_rating=speed_rating,
            maturity=maturity,
            status=status,
            supports_function_calling=supports_function_calling,
            supports_vision=supports_vision,
            supports_json_mode=supports_json_mode,
            task_scores=default_scores,
        )

    def _load_defaults(self):
        """Load hardcoded default models"""
        self._load_grok_models()
        self._load_openai_models()
        self._load_google_models()
        self._load_anthropic_models()
        self._load_local_models()

    def _load_grok_models(self):
        """Load xAI Grok models"""
        self.models.update(
            {
                "grok-4-fast-reasoning": self._create_model_caps(
                    model_id="grok-4-fast-reasoning",
                    name="Grok 4 Fast Reasoning",
                    api_name="grok-4-fast-reasoning",
                    provider=ModelProvider.XAI,
                    context_window=2000000,
                    supports_function_calling=True,
                    input_cost=2.0,
                    output_cost=6.0,
                    reasoning_score=95.0,
                    coding_score=85.0,
                    speed_rating=7.0,
                    maturity=ProviderMaturity.BETA,
                ),
                "grok-code-fast-1": self._create_model_caps(
                    model_id="grok-code-fast-1",
                    name="Grok Code Fast 1",
                    api_name="grok-code-fast-1",
                    provider=ModelProvider.XAI,
                    context_window=256000,
                    input_cost=1.5,
                    output_cost=4.5,
                    reasoning_score=85.0,
                    coding_score=90.0,
                    speed_rating=8.0,
                    maturity=ProviderMaturity.BETA,
                ),
                "grok-3": self._create_model_caps(
                    model_id="grok-3",
                    name="Grok 3",
                    api_name="grok-3",
                    provider=ModelProvider.XAI,
                    context_window=131072,
                    input_cost=1.0,
                    output_cost=3.0,
                    reasoning_score=80.0,
                    coding_score=75.0,
                    speed_rating=6.0,
                    maturity=ProviderMaturity.BETA,
                ),
            }
        )

    def _load_openai_models(self):
        """Load OpenAI models"""
        self.models.update(
            {
                "o1-pro": self._create_model_caps(
                    model_id="o1-pro",
                    name="O1 Pro",
                    api_name="o1-pro",
                    provider=ModelProvider.OPENAI,
                    context_window=200000,
                    input_cost=60.0,
                    output_cost=240.0,
                    reasoning_score=99.0,
                    coding_score=98.0,
                    speed_rating=3.0,
                    maturity=ProviderMaturity.PRODUCTION,
                ),
                "gpt-4o": self._create_model_caps(
                    model_id="gpt-4o",
                    name="GPT-4o",
                    api_name="gpt-4o",
                    provider=ModelProvider.OPENAI,
                    context_window=128000,
                    supports_function_calling=True,
                    supports_vision=True,
                    input_cost=5.0,
                    output_cost=15.0,
                    reasoning_score=90.0,
                    coding_score=85.0,
                    speed_rating=8.0,
                    maturity=ProviderMaturity.PRODUCTION,
                ),
                "gpt-4o-mini": self._create_model_caps(
                    model_id="gpt-4o-mini",
                    name="GPT-4o Mini",
                    api_name="gpt-4o-mini",
                    provider=ModelProvider.OPENAI,
                    context_window=128000,
                    supports_function_calling=True,
                    supports_vision=True,
                    input_cost=0.15,
                    output_cost=0.6,
                    reasoning_score=85.0,
                    coding_score=80.0,
                    speed_rating=9.0,
                    maturity=ProviderMaturity.PRODUCTION,
                ),
                "o1-mini": self._create_model_caps(
                    model_id="o1-mini",
                    name="O1 Mini",
                    api_name="o1-mini",
                    provider=ModelProvider.OPENAI,
                    context_window=128000,
                    input_cost=3.0,
                    output_cost=12.0,
                    reasoning_score=96.0,
                    coding_score=95.0,
                    speed_rating=5.0,
                    maturity=ProviderMaturity.PRODUCTION,
                ),
            }
        )

    def _load_google_models(self):
        """Load Google Gemini models"""
        self.models.update(
            {
                "gemini-2.5-pro": self._create_model_caps(
                    model_id="gemini-2.5-pro",
                    name="Gemini 2.5 Pro",
                    api_name="gemini-2.5-pro",
                    provider=ModelProvider.GOOGLE,
                    context_window=1000000,
                    supports_function_calling=True,
                    supports_vision=True,
                    input_cost=1.25,
                    output_cost=5.0,
                    reasoning_score=85.0,
                    coding_score=85.0,
                    speed_rating=7.0,
                    maturity=ProviderMaturity.BETA,
                ),
                "gemini-2.5-flash": self._create_model_caps(
                    model_id="gemini-2.5-flash",
                    name="Gemini 2.5 Flash",
                    api_name="gemini-2.5-flash",
                    provider=ModelProvider.GOOGLE,
                    context_window=1000000,
                    supports_function_calling=True,
                    supports_vision=True,
                    input_cost=0.075,
                    output_cost=0.3,
                    reasoning_score=80.0,
                    coding_score=80.0,
                    speed_rating=9.0,
                    maturity=ProviderMaturity.BETA,
                ),
            }
        )

    def _load_anthropic_models(self):
        """Load Anthropic Claude models"""
        self.models.update(
            {
                "claude-3-5-sonnet": self._create_model_caps(
                    model_id="claude-3-5-sonnet",
                    name="Claude 3.5 Sonnet",
                    api_name="claude-3-5-sonnet-20240620",
                    provider=ModelProvider.ANTHROPIC,
                    context_window=200000,
                    supports_function_calling=True,
                    supports_vision=True,
                    input_cost=3.0,
                    output_cost=15.0,
                    reasoning_score=95.0,
                    coding_score=95.0,
                    speed_rating=7.0,
                    maturity=ProviderMaturity.PRODUCTION,
                ),
                "claude-3-5-haiku": self._create_model_caps(
                    model_id="claude-3-5-haiku",
                    name="Claude 3.5 Haiku",
                    api_name="claude-3-5-haiku-20241022",
                    provider=ModelProvider.ANTHROPIC,
                    context_window=200000,
                    supports_function_calling=True,
                    input_cost=0.25,
                    output_cost=1.25,
                    reasoning_score=88.0,
                    coding_score=85.0,
                    speed_rating=9.0,
                    maturity=ProviderMaturity.PRODUCTION,
                ),
                "claude-3-5-opus": self._create_model_caps(
                    model_id="claude-3-5-opus",
                    name="Claude 3.5 Opus",
                    api_name="claude-3-5-opus-latest",
                    provider=ModelProvider.ANTHROPIC,
                    context_window=200000,
                    supports_function_calling=True,
                    supports_vision=True,
                    input_cost=15.0,
                    output_cost=75.0,
                    reasoning_score=99.0,
                    coding_score=97.0,
                    speed_rating=4.0,
                    maturity=ProviderMaturity.BETA,
                ),
                "claude-3-opus": self._create_model_caps(
                    model_id="claude-3-opus",
                    name="Claude 3 Opus",
                    api_name="claude-3-opus-20240229",
                    provider=ModelProvider.ANTHROPIC,
                    context_window=200000,
                    supports_function_calling=True,
                    supports_vision=True,
                    input_cost=15.0,
                    output_cost=75.0,
                    reasoning_score=98.0,
                    coding_score=92.0,
                    speed_rating=5.0,
                    maturity=ProviderMaturity.PRODUCTION,
                ),
            }
        )

    def _load_local_models(self):
        """Load local Ollama models"""
        # These are placeholders, actual available models are detected by LocalManager
        self.models.update(
            {
                "codellama:34b": self._create_model_caps(
                    model_id="codellama:34b",
                    name="CodeLlama 34B",
                    api_name="codellama:34b",
                    provider=ModelProvider.OLLAMA,
                    context_window=16384,
                    input_cost=0.0,
                    output_cost=0.0,
                    reasoning_score=85.0,
                    coding_score=95.0,
                    speed_rating=5.0,
                ),
                "qwen2.5:32b": self._create_model_caps(
                    model_id="qwen2.5:32b",
                    name="Qwen 2.5 32B",
                    api_name="qwen2.5:32b-instruct-q4_K_M",
                    provider=ModelProvider.OLLAMA,
                    context_window=32768,
                    supports_function_calling=True,
                    input_cost=0.0,
                    output_cost=0.0,
                    reasoning_score=88.0,
                    coding_score=85.0,
                    speed_rating=6.0,
                ),
            }
        )

    def get_model(self, model_id: str) -> ModelCapabilities | None:
        """Get model by ID"""
        return self.models.get(model_id)

    def get_models_by_provider(self, provider: ModelProvider) -> list[ModelCapabilities]:
        """Get all models for a provider"""
        return [m for m in self.models.values() if m.provider == provider]

    def get_all_models(self) -> list[ModelCapabilities]:
        """Get all registered models"""
        return list(self.models.values())

    def validate_credentials(self, provider: ModelProvider) -> bool:
        """Check if required credentials are present for the provider."""
        import os

        required_vars = {
            ModelProvider.OPENAI: ["OPENAI_API_KEY"],
            ModelProvider.ANTHROPIC: ["ANTHROPIC_API_KEY"],
            ModelProvider.GOOGLE: ["GOOGLE_API_KEY"],
            ModelProvider.XAI: ["XAI_API_KEY"],
            ModelProvider.AZURE: ["AZURE_OPENAI_KEY", "AZURE_ENDPOINT"],
            ModelProvider.BEDROCK: ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"],
            ModelProvider.OLLAMA: [],  # Local, always valid or checks OLLAMA_HOST
        }

        vars_to_check = required_vars.get(provider, [])
        missing = [v for v in vars_to_check if not os.getenv(v)]

        if missing:
            # Special case for Bedrock implicit auth
            if provider == ModelProvider.BEDROCK:
                # If keys missing, it might use profile/role, so we can't definitively say it's invalid
                # But for explicit check we warn. The client handles implicit auth.
                # Returning True to allow client to try implicit auth.
                return True

            logger.warning(f"Provider {provider.value} missing credentials: {', '.join(missing)}")
            return False

        return True

    def get_health_status(self, provider: ModelProvider) -> str:
        """Get the health status of a provider."""
        if not self.validate_credentials(provider):
            return "MISCONFIGURED"

        # Here we could implement more complex checks (circuit breaker status etc)
        # For now, if credentials exist, it's ACTIVE
        return "ACTIVE"
