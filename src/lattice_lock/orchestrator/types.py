from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


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
    SECURITY_AUDIT = auto()
    CREATIVE_WRITING = auto()
    TRANSLATION = auto()


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

    PRODUCTION = auto()  # Stable, verified, default
    BETA = auto()  # Functional but evolving
    EXPERIMENTAL = auto()  # Gated, requires setup


@dataclass
class ModelCapabilities:
    """Defines the capabilities and costs of a specific model."""

    name: str
    api_name: str
    provider: ModelProvider
    context_window: int
    input_cost: float  # Per 1M tokens
    output_cost: float  # Per 1M tokens
    reasoning_score: float  # 0-100
    coding_score: float  # 0-100
    speed_rating: float  # 0-10
    maturity: ProviderMaturity = ProviderMaturity.BETA
    status: ModelStatus = ModelStatus.ACTIVE

    # Feature Flags
    supports_vision: bool = False
    supports_function_calling: bool = False
    supports_json_mode: bool = False

    # Explicit task scores
    task_scores: dict[TaskType, float] = field(default_factory=dict)

    @property
    def blended_cost(self) -> float:
        """Average cost per 1M tokens (assuming 3:1 input:output ratio)."""
        return (self.input_cost * 3 + self.output_cost) / 4

    @property
    def supports_reasoning(self) -> bool:
        """Whether this model has strong reasoning capabilities (score >= 70 per spec)."""
        return self.reasoning_score >= 70.0

    @property
    def code_specialized(self) -> bool:
        """Whether this model is specialized for code tasks (score >= 80 per spec)."""
        return self.coding_score >= 80.0


@dataclass
class TaskRequirements:
    """Defines the requirements for a specific task."""

    task_type: TaskType
    min_context: int = 4000
    max_cost: float | None = None  # Max blended cost per 1M tokens
    min_reasoning: float = 0.0
    min_coding: float = 0.0
    priority: str = "balanced"  # "speed", "cost", "quality", "balanced"
    require_vision: bool = False
    require_functions: bool = False


@dataclass
class FunctionCall:
    """Represents a function call requested by the model."""

    name: str
    arguments: dict[str, Any]


@dataclass
class FunctionDefinition:
    """Represents a function that can be called by the model."""

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)  # JSON schema for parameters


@dataclass
class TokenUsage:
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float | None = None


@dataclass
class APIResponse:
    """Standardized API response format."""

    content: str
    model: str
    provider: str
    usage: TokenUsage | dict[str, int]  # input_tokens, output_tokens
    latency_ms: int
    raw_response: dict | None = None
    error: str | None = None
    function_call: FunctionCall | None = None
    function_call_result: Any | None = None
