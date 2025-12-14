from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import logging
from .types import ModelCapabilities, ModelProvider, TaskType, ProviderMaturity, ModelStatus

logger = logging.getLogger(__name__)


REQUIRED_MODEL_FIELDS = [
    'api_name',
    'context_window',
    'input_cost',
    'output_cost',
    'reasoning_score',
    'coding_score',
    'speed_rating',
]

VALID_MATURITY_VALUES = ['PRODUCTION', 'BETA', 'EXPERIMENTAL', 'DEPRECATED']
VALID_STATUS_VALUES = ['ACTIVE', 'INACTIVE', 'DEPRECATED']
VALID_CAPABILITIES = ['function_calling', 'vision']


@dataclass
class RegistryValidationResult:
    """Result of registry validation."""
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    model_count: int = 0
    provider_count: int = 0

    def add_error(self, error: str):
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str):
        self.warnings.append(warning)


class ModelRegistry:
    """Centralized model registry with all model definitions"""

    def __init__(self, registry_path: Optional[str] = "models/registry.yaml"):
        self.models: Dict[str, ModelCapabilities] = {}
        self.registry_path = registry_path
        self._validation_result: Optional[RegistryValidationResult] = None
        self._load_all_models()

    @property
    def validation_result(self) -> Optional[RegistryValidationResult]:
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

        if 'version' not in data:
            result.add_warning("Registry missing 'version' field")

        if 'providers' not in data:
            result.add_error("Registry missing required 'providers' section")
            return result

        providers = data.get('providers', {})
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

            models = provider_data.get('models', {})
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

                if 'context_window' in model_data:
                    if not isinstance(model_data['context_window'], int):
                        result.add_error(f"Model '{model_id}' context_window must be an integer")
                    elif model_data['context_window'] <= 0:
                        result.add_error(f"Model '{model_id}' context_window must be positive")

                for cost_field in ['input_cost', 'output_cost']:
                    if cost_field in model_data:
                        if not isinstance(model_data[cost_field], (int, float)):
                            result.add_error(f"Model '{model_id}' {cost_field} must be a number")
                        elif model_data[cost_field] < 0:
                            result.add_error(f"Model '{model_id}' {cost_field} cannot be negative")

                for score_field in ['reasoning_score', 'coding_score', 'speed_rating']:
                    if score_field in model_data:
                        if not isinstance(model_data[score_field], (int, float)):
                            result.add_error(f"Model '{model_id}' {score_field} must be a number")
                        elif not (0 <= model_data[score_field] <= 100):
                            result.add_warning(f"Model '{model_id}' {score_field} should be between 0 and 100")

                if 'maturity' in model_data:
                    if model_data['maturity'] not in VALID_MATURITY_VALUES:
                        result.add_error(f"Model '{model_id}' has invalid maturity: {model_data['maturity']}")

                if 'status' in model_data:
                    if model_data['status'] not in VALID_STATUS_VALUES:
                        result.add_error(f"Model '{model_id}' has invalid status: {model_data['status']}")

                if 'capabilities' in model_data:
                    caps = model_data['capabilities']
                    if not isinstance(caps, list):
                        result.add_error(f"Model '{model_id}' capabilities must be a list")
                    else:
                        for cap in caps:
                            if cap not in VALID_CAPABILITIES:
                                result.add_warning(f"Model '{model_id}' has unknown capability: {cap}")

        return result

    def _calculate_default_scores(self, coding_score: float, reasoning_score: float, supports_vision: bool) -> Dict[TaskType, float]:
        """Calculate default task scores based on capabilities."""
        scores: Dict[TaskType, float] = {}
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
        """Load models from registry.yaml with validation."""
        path = Path(self.registry_path)
        if not path.exists():
            return False

        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)

            self._validation_result = self.validate_registry(data)

            if self._validation_result.errors:
                for error in self._validation_result.errors:
                    logger.error(f"Registry validation error: {error}")

            if self._validation_result.warnings:
                for warning in self._validation_result.warnings:
                    logger.warning(f"Registry validation warning: {warning}")

            for provider_name, provider_data in data.get('providers', {}).items():
                try:
                    provider_enum = ModelProvider(provider_name.lower())
                except ValueError:
                    logger.warning(f"Unknown provider in registry: {provider_name}")
                    continue

                for model_id, model_data in provider_data.get('models', {}).items():
                    try:
                        maturity = ProviderMaturity[model_data.get('maturity', 'BETA')]
                        status = ModelStatus[model_data.get('status', 'ACTIVE')]

                        # Calculate default task scores if not provided or just init empty
                        # Logic to calculate scores will be moved to a helper or done here
                        default_scores = self._calculate_default_scores(
                             model_data.get('coding_score', 0),
                             model_data.get('reasoning_score', 0),
                             'vision' in model_data.get('capabilities', [])
                        )

                        caps = ModelCapabilities(
                            name=model_id, # using id as name if not separate
                            api_name=model_data['api_name'],
                            provider=provider_enum,
                            context_window=model_data['context_window'],
                            input_cost=model_data['input_cost'],
                            output_cost=model_data['output_cost'],
                            reasoning_score=model_data['reasoning_score'],
                            coding_score=model_data['coding_score'],
                            speed_rating=model_data['speed_rating'],
                            maturity=maturity,
                            status=status,
                            supports_function_calling='function_calling' in model_data.get('capabilities', []),
                            supports_vision='vision' in model_data.get('capabilities', []),
                            task_scores=default_scores
                        )
                        self.models[model_id] = caps
                    except Exception as e:
                        logger.error(f"Failed to load model {model_id}: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to load registry YAML: {e}")
            return False

    def _load_defaults(self):
        """Load hardcoded default models"""
        self._load_grok_models()
        self._load_openai_models()
        self._load_google_models()
        self._load_anthropic_models()
        self._load_local_models()

    def _load_grok_models(self):
        """Load xAI Grok models"""
        self.models.update({
            "grok-4-fast-reasoning": ModelCapabilities(
                name="Grok 4 Fast Reasoning",
                api_name="grok-4-fast-reasoning",
                provider=ModelProvider.XAI,
                context_window=2000000,
                supports_function_calling=True,
                supports_vision=False, # Assuming false based on previous file
                input_cost=2.0,
                output_cost=6.0,
                reasoning_score=95.0,
                coding_score=85.0,
                speed_rating=7.0,
                maturity=ProviderMaturity.BETA,
                task_scores=self._calculate_default_scores(85.0, 95.0, False)
            ),
            "grok-code-fast-1": ModelCapabilities(
                name="Grok Code Fast 1",
                api_name="grok-code-fast-1",
                provider=ModelProvider.XAI,
                context_window=256000,
                supports_function_calling=False,
                supports_vision=False,
                input_cost=1.5,
                output_cost=4.5,
                reasoning_score=85.0,
                coding_score=90.0,
                speed_rating=8.0,
                maturity=ProviderMaturity.BETA,
            ),
            "grok-3": ModelCapabilities(
                name="Grok 3",
                api_name="grok-3",
                provider=ModelProvider.XAI,
                context_window=131072,
                supports_function_calling=False,
                supports_vision=False,
                input_cost=1.0,
                output_cost=3.0,
                reasoning_score=80.0,
                coding_score=75.0,
                speed_rating=6.0,
                maturity=ProviderMaturity.BETA,
            ),
        })

    def _load_openai_models(self):
        """Load OpenAI models"""
        self.models.update({
            "o1-pro": ModelCapabilities(
                name="O1 Pro",
                api_name="o1-pro",
                provider=ModelProvider.OPENAI,
                context_window=200000,
                supports_function_calling=False,
                supports_vision=False,
                input_cost=60.0,
                output_cost=240.0,
                reasoning_score=99.0,
                coding_score=98.0,
                speed_rating=3.0,
                maturity=ProviderMaturity.PRODUCTION,
                task_scores=self._calculate_default_scores(98.0, 99.0, False)
            ),
            "gpt-4o": ModelCapabilities(
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
                task_scores=self._calculate_default_scores(85.0, 90.0, True)
            ),
        })

    def _load_google_models(self):
        """Load Google Gemini models"""
        self.models.update({
            "gemini-2.5-pro": ModelCapabilities(
                name="Gemini 2.5 Pro",
                api_name="gemini-2.5-pro",
                provider=ModelProvider.GOOGLE,
                context_window=1000000,
                supports_function_calling=True,
                supports_vision=True, # Assuming true for Gemini
                input_cost=1.25,
                output_cost=5.0,
                reasoning_score=85.0,
                coding_score=85.0,
                speed_rating=7.0,
                maturity=ProviderMaturity.BETA,
                task_scores=self._calculate_default_scores(85.0, 85.0, True)
            ),
            "gemini-2.5-flash": ModelCapabilities(
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
                task_scores=self._calculate_default_scores(80.0, 80.0, True)
            ),
        })

    def _load_anthropic_models(self):
        """Load Anthropic Claude models"""
        self.models.update({
            "claude-3-5-sonnet": ModelCapabilities(
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
                task_scores=self._calculate_default_scores(95.0, 95.0, True)
            ),
             "claude-3-opus": ModelCapabilities(
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
                task_scores=self._calculate_default_scores(92.0, 98.0, True)
            ),
        })

    def _load_local_models(self):
        """Load local Ollama models"""
        # These are placeholders, actual available models are detected by LocalManager
        self.models.update({
            "codellama:34b": ModelCapabilities(
                name="CodeLlama 34B",
                api_name="codellama:34b",
                provider=ModelProvider.OLLAMA,
                context_window=16384,
                supports_function_calling=False,
                supports_vision=False,
                input_cost=0.0,
                output_cost=0.0,
                reasoning_score=85.0,
                coding_score=95.0,
                speed_rating=5.0,
                task_scores=self._calculate_default_scores(95.0, 85.0, False)
            ),
            "qwen2.5:32b": ModelCapabilities(
                name="Qwen 2.5 32B",
                api_name="qwen2.5:32b-instruct-q4_K_M",
                provider=ModelProvider.OLLAMA,
                context_window=32768,
                supports_function_calling=True,
                supports_vision=False,
                input_cost=0.0,
                output_cost=0.0,
                reasoning_score=88.0,
                coding_score=85.0,
                speed_rating=6.0,
                task_scores=self._calculate_default_scores(85.0, 88.0, False)
            ),
        })

    def get_model(self, model_id: str) -> Optional[ModelCapabilities]:
        """Get model by ID"""
        return self.models.get(model_id)

    def get_models_by_provider(self, provider: ModelProvider) -> List[ModelCapabilities]:
        """Get all models for a provider"""
        return [m for m in self.models.values() if m.provider == provider]

    def get_all_models(self) -> List[ModelCapabilities]:
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
            ModelProvider.OLLAMA: [] # Local, always valid or checks OLLAMA_HOST
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
