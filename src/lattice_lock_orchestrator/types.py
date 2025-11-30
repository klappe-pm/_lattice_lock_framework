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

class ModelProvider(Enum):
    """Supported model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    XAI = "xai"  # Grok
    OLLAMA = "ollama"
    AZURE = "azure"
    BEDROCK = "bedrock"

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
    speed_rating: float # 0-10
    supports_vision: bool = False
    supports_function_calling: bool = False
    
    @property
    def blended_cost(self) -> float:
        """Average cost per 1M tokens (assuming 3:1 input:output ratio)."""
        return (self.input_cost * 3 + self.output_cost) / 4

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
class APIResponse:
    """Standardized API response format."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]  # input_tokens, output_tokens
    latency_ms: int
    raw_response: Optional[Dict] = None
    error: Optional[str] = None
