
import logging
import time
from typing import Any, Callable, List, Optional
from ..types import APIResponse

logger = logging.getLogger(__name__)

class ProviderUnavailableError(RuntimeError):
    """Raised when all providers in the fallback chain fail."""
    pass

class FallbackManager:
    """Manages execution resilience across multiple model providers."""
    
    def __init__(self, max_retries: int = 1):
        self.max_retries = max_retries

    def execute_with_fallback(
        self, 
        func: Callable[..., APIResponse], 
        candidates: List[Any], 
        *args, 
        **kwargs
    ) -> APIResponse:
        """
        Execute a function with a list of update candidates (models/clients).
        
        Args:
            func: The function to execute. It must accept a candidate as first arg, then *args, **kwargs.
            candidates: List of fallback candidates (e.g. model objects or clients).
            
        Returns:
            The result of the successful execution.
            
        Raises:
            ProviderUnavailableError: If all candidates fail.
        """
        last_error = None
        
        for i, candidate in enumerate(candidates):
            logger.info(f"Attempting execution with candidate {i+1}/{len(candidates)}: {candidate}")
            
            # Simple retry logic for the current candidate
            for attempt in range(self.max_retries + 1):
                try:
                    return func(candidate, *args, **kwargs)
                except Exception as e:
                    logger.warning(f"Candidate {candidate} failed (attempt {attempt+1}/{self.max_retries+1}): {e}")
                    last_error = e
                    if attempt < self.max_retries:
                        time.sleep(0.5 * (2 ** attempt)) # Exponential backoff
            
            logger.warning(f"Falling back from candidate {candidate} due to persistent failure.")

        logger.error("All candidates exhausted. raising ProviderUnavailableError.")
        raise ProviderUnavailableError(f"All providers failed. Last error: {last_error}")
