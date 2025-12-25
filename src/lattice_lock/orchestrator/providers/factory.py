from typing import Any
from .base import BaseAPIClient, ProviderAvailability, ProviderStatus
from .openai import OpenAIAPIClient
from .anthropic import AnthropicAPIClient
from .google import GoogleAPIClient
from .xai import XAIAPIClient
from .azure import AzureOpenAIClient
from .bedrock import BedrockAPIClient

def get_api_client(provider: str, **kwargs: Any) -> BaseAPIClient:
    """
    Factory function to get the appropriate API client for a provider.
    
    Args:
        provider: Provider name (e.g., 'openai', 'anthropic', 'grok')
        **kwargs: Additional arguments for the client constructor
        
    Returns:
        Instance of BaseAPIClient subclass
        
    Raises:
        ValueError: If provider is unknown
    """
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIAPIClient(**kwargs)
    elif provider == "anthropic":
        return AnthropicAPIClient(**kwargs)
    elif provider == "google" or provider == "gemini":
        return GoogleAPIClient(**kwargs)
    elif provider == "xai" or provider == "grok":
        return XAIAPIClient(**kwargs)
    elif provider == "azure":
        return AzureOpenAIClient(**kwargs)
    elif provider == "bedrock":
        return BedrockAPIClient(**kwargs)
    elif provider == "dial":
        # Anthropic client handles DIAL via flag
        return AnthropicAPIClient(use_dial=True, **kwargs)
    # Add local/fallback if needed
    
    raise ValueError(f"Unknown provider: {provider}")
