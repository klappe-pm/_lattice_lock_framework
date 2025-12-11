from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

class TaskType(Enum):
    """Categorizes the nature of the request to optimize model selection."""
    CODE_GENERATION = auto()
    DEBUGGING = auto()
    ARCHITECTURAL_DESIGN = auto()
    DOCUMENTATION = auto()
    TESTING = auto()
    DATA_ANALYSIS = auto()
    GENERAL = auto()
    REASONING = auto()
    VISION = auto()

class ModelProvider(Enum):
    """Supported model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    XAI = "xai"  # Grok
    OLLAMA = "ollama"
    AZURE = "azure"
    BEDROCK = "bedrock"

class ModelStatus(Enum):
    """Lifecycle status of the model."""
    ACTIVE = auto()
    DEPRECATED = auto()
    SUNSET = auto()

class ProviderMaturity(Enum):
    """Maturity tier of the provider implementation."""
    PRODUCTION = auto()    # Stable, verified, default
    BETA = auto()         # Functional but evolving
    EXPERIMENTAL = auto() # Gated, requires setup

@dataclass
class ModelCapabilities:
    """Defines the capabilities and costs of a specific model."""
    name: str
    api_name: str
    provider: ModelProvider
    context_window: int
    input_cost: float  # Per 1M tokens
    output_cost: float # Per 1M tokens
    reasoning_score: float # 0-100
    coding_score: float # 0-100
    coding_score: float # 0-100
    speed_rating: float # 0-10
    maturity: ProviderMaturity = ProviderMaturity.BETA
    status: ModelStatus = ModelStatus.ACTIVE
    supports_vision: bool = False
    supports_function_calling: bool = False
    
    @property
    def blended_cost(self) -> float:
        """Average cost per 1M tokens (assuming 3:1 input:output ratio)."""
        return (self.input_cost * 3 + self.output_cost) / 4

    @property
    def supports_reasoning(self) -> bool:
        """Whether this model has strong reasoning capabilities (score >= 85)."""
        return self.reasoning_score >= 85.0

    @property
    def code_specialized(self) -> bool:
        """Whether this model is specialized for code tasks (score >= 85)."""
        return self.coding_score >= 85.0

    @property
    def task_scores(self) -> Dict[TaskType, float]:
        """
        Returns a dictionary mapping TaskType to a normalized score (0-1).
        Scores are derived from the model's capabilities.
        """
        scores: Dict[TaskType, float] = {}
        # Normalize scores from 0-100 to 0-1
        coding_norm = self.coding_score / 100.0
        reasoning_norm = self.reasoning_score / 100.0

        scores[TaskType.CODE_GENERATION] = coding_norm
        scores[TaskType.DEBUGGING] = coding_norm * 0.9 + reasoning_norm * 0.1
        scores[TaskType.ARCHITECTURAL_DESIGN] = reasoning_norm * 0.7 + coding_norm * 0.3
        scores[TaskType.DOCUMENTATION] = (coding_norm + reasoning_norm) / 2
        scores[TaskType.TESTING] = coding_norm * 0.8 + reasoning_norm * 0.2
        scores[TaskType.DATA_ANALYSIS] = reasoning_norm * 0.6 + coding_norm * 0.4
        scores[TaskType.GENERAL] = (coding_norm + reasoning_norm) / 2
        scores[TaskType.REASONING] = reasoning_norm
        scores[TaskType.VISION] = 1.0 if self.supports_vision else 0.0

        return scores

@dataclass
class TaskRequirements:
    """Defines the requirements for a specific task."""
    task_type: TaskType
    min_context: int = 4000
    max_cost: Optional[float] = None # Max blended cost per 1M tokens
    min_reasoning: float = 0.0
    min_coding: float = 0.0
    priority: str = "balanced" # "speed", "cost", "quality", "balanced"
    require_vision: bool = False
    require_functions: bool = False

@dataclass
class FunctionCall:
    """Represents a function call requested by the model."""
    name: str
    arguments: Dict[str, Any]

@dataclass
class FunctionDefinition:
    """Represents a function that can be called by the model."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict) # JSON schema for parameters

@dataclass
class APIResponse:
    """Standardized API response format."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]  # input_tokens, output_tokens
    latency_ms: int
    raw_response: Optional[Dict] = None
    error: Optional[str] = None
    function_call: Optional[FunctionCall] = None
    function_call_result: Optional[Any] = None
