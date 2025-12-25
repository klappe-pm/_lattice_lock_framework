import logging
from typing import List, Tuple, Optional

from lattice_lock.orchestrator.guide import ModelGuideParser
from lattice_lock.orchestrator.registry import ModelRegistry
from lattice_lock.orchestrator.scoring import ModelScorer
from lattice_lock.orchestrator.types import TaskRequirements, ModelCapabilities
from lattice_lock.orchestrator.providers import ProviderAvailability

logger = logging.getLogger(__name__)

class ModelSelector:
    """
    Selects the best model for a given task based on requirements, scoring, and guidelines.
    """

    def __init__(self, registry: ModelRegistry, scorer: ModelScorer, guide: ModelGuideParser):
        self.registry = registry
        self.scorer = scorer
        self.guide = guide

    def select_best_model(self, requirements: TaskRequirements) -> Optional[str]:
        """
        Select the best model based on requirements and guide.

        Args:
            requirements: The task requirements.

        Returns:
            The ID of the selected model, or None if no suitable model is found.
        """
        # 1. Check Guide Recommendations first
        guide_recs = self.guide.get_recommended_models(requirements.task_type.name)
        if guide_recs:
            # Validate recommendations exist in registry and meet hard constraints
            valid_recs = []
            for mid in guide_recs:
                model = self.registry.get_model(mid)
                if model and self.scorer.score(model, requirements) > 0:
                    valid_recs.append(mid)

            if valid_recs:
                return valid_recs[0]  # Return top recommendation

        # 2. Score all models
        candidates = []
        for model in self.registry.get_all_models():
            if self.guide.is_model_blocked(model.api_name):
                continue

            score = self.scorer.score(model, requirements)
            if score > 0:
                candidates.append((model.api_name, score))

        if not candidates:
            return None

        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    def get_fallback_chain(self, requirements: TaskRequirements, failed_model: str) -> List[str]:
        """
        Get a list of fallback models.

        Args:
            requirements: The task requirements.
            failed_model: The model that failed (to be excluded).

        Returns:
            A list of model IDs to try as fallbacks.
        """
        # Get fallback chain from guide
        chain = self.guide.get_fallback_chain(requirements.task_type.name)

        # If no chain, or failed model was last in chain, try to find next best scorer
        if not chain:
            candidates = []
            for model in self.registry.get_all_models():
                if model.api_name == failed_model:
                    continue

                # Skip models from unavailable providers
                provider_name = model.provider.value
                if not self._is_provider_available(provider_name):
                    logger.debug(
                        f"Skipping model {model.api_name}: provider '{provider_name}' unavailable"
                    )
                    continue

                score = self.scorer.score(model, requirements)
                if score > 0:
                    candidates.append((model.api_name, score))

            candidates.sort(key=lambda x: x[1], reverse=True)
            chain = [c[0] for c in candidates[:5]]  # Try top 5 available models

        return chain

    def _is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available (has credentials configured)."""
        # Uses ProviderAvailability from providers package
        try:
            from lattice_lock.orchestrator.providers import ProviderAvailability
            return ProviderAvailability.is_available(provider)
        except ImportError:
            logger.warning(f"Could not check availability for {provider}, assuming True")
            return True

