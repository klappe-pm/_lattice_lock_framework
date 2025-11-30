from typing import Dict, List, Optional
from .types import ModelCapabilities, ModelProvider, TaskType

class ModelRegistry:
    """Centralized model registry with all model definitions"""

    def __init__(self):
        self.models: Dict[str, ModelCapabilities] = {}
        self._load_all_models()

    def _load_all_models(self):
        """Load all models across all providers"""
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
                # task_scores logic will be handled by scorer based on capabilities
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
