"""
Pydantic models for registry YAML validation.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from .types import ModelProvider, ModelStatus, ProviderMaturity


class ModelConfig(BaseModel):
    """Configuration for a single model in registry.yaml."""
    id: str = Field(..., description="Unique identifier for the model (e.g. gpt-4o)")
    name: Optional[str] = Field(None, description="Human readable name")
    api_name: Optional[str] = Field(None, description="Actual API model name (defaults to id)")
    provider: ModelProvider
    context_window: int = Field(..., gt=0)

    # Cost per 1M tokens
    input_cost: float = Field(0.0, ge=0.0)
    output_cost: float = Field(0.0, ge=0.0)

    # Capability scores (0-100)
    reasoning_score: float = Field(0.0, ge=0.0, le=100.0)
    coding_score: float = Field(0.0, ge=0.0, le=100.0)
    speed_rating: float = Field(5.0, ge=0.0, le=10.0)

    # Metadata
    maturity: ProviderMaturity = ProviderMaturity.BETA
    status: ModelStatus = ModelStatus.ACTIVE

    # Capabilities
    supports_vision: bool = False
    supports_function_calling: bool = False
    supports_json_mode: bool = False

    @field_validator('api_name', mode='before')
    @classmethod
    def set_api_name(cls, v, info):
        # If api_name is missing, use id
        if v is None and info.data and 'id' in info.data:
            return info.data['id']
        return v

    @field_validator('maturity', mode='before')
    @classmethod
    def parse_maturity(cls, v):
        if isinstance(v, str):
            try:
                return ProviderMaturity[v.upper()]
            except KeyError:
                raise ValueError(f"Invalid maturity: {v}")
        return v

    @field_validator('status', mode='before')
    @classmethod
    def parse_status(cls, v):
        if isinstance(v, str):
            try:
                return ModelStatus[v.upper()]
            except KeyError:
                raise ValueError(f"Invalid status: {v}")
        return v


class ProviderModelsConfig(BaseModel):
    """Configuration for a provider's models section."""
    models: Dict[str, dict] = Field(default_factory=dict)


class RegistryConfig(BaseModel):
    """Root configuration for registry.yaml

    Supports two formats:
    1. Provider-based (recommended): { providers: { openai: { models: { gpt-4: {...} } } } }
    2. Flat list: { models: [{ id: "gpt-4", provider: "openai", ... }] }
    """
    version: str = "1.0"
    providers: Dict[str, ProviderModelsConfig] = Field(default_factory=dict)
    models: List[ModelConfig] = Field(default_factory=list)

    @model_validator(mode='after')
    def flatten_providers_to_models(self):
        """Convert provider-based structure to flat model list."""
        if self.providers and not self.models:
            flat_models = []
            for provider_name, provider_config in self.providers.items():
                try:
                    provider_enum = ModelProvider(provider_name.lower())
                except ValueError:
                    continue

                for model_id, model_data in provider_config.models.items():
                    # Map capabilities list to boolean flags
                    capabilities = model_data.get('capabilities', [])
                    supports_vision = 'vision' in capabilities
                    supports_function_calling = 'function_calling' in capabilities
                    supports_json_mode = 'json_mode' in capabilities

                    model_cfg = ModelConfig(
                        id=model_id,
                        provider=provider_enum,
                        api_name=model_data.get('api_name', model_id),
                        context_window=model_data.get('context_window', 4096),
                        input_cost=model_data.get('input_cost', 0.0),
                        output_cost=model_data.get('output_cost', 0.0),
                        reasoning_score=model_data.get('reasoning_score', 0.0),
                        coding_score=model_data.get('coding_score', 0.0),
                        speed_rating=model_data.get('speed_rating', 5.0),
                        maturity=model_data.get('maturity', 'BETA'),
                        status=model_data.get('status', 'ACTIVE'),
                        supports_vision=supports_vision,
                        supports_function_calling=supports_function_calling,
                        supports_json_mode=supports_json_mode,
                    )
                    flat_models.append(model_cfg)
            self.models = flat_models
        return self
