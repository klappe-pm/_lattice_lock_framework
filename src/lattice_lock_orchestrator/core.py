import logging
import asyncio
from typing import Optional, Dict, List, Any
from .types import TaskType, TaskRequirements, APIResponse, ModelCapabilities
from .registry import ModelRegistry
from .scorer import TaskAnalyzer, ModelScorer
from .guide import ModelGuideParser
from .api_clients import get_api_client

logger = logging.getLogger(__name__)

class ModelOrchestrator:
    """
    Intelligent model orchestration system.
    Routes requests to the best model based on task requirements, cost, and performance.
    """

    def __init__(self, guide_path: Optional[str] = None):
        self.registry = ModelRegistry()
        self.analyzer = TaskAnalyzer()
        self.scorer = ModelScorer()
        self.guide = ModelGuideParser(guide_path)
        self.clients = {}

    async def route_request(self, 
                          prompt: str, 
                          model_id: Optional[str] = None, 
                          task_type: Optional[TaskType] = None,
                          **kwargs) -> APIResponse:
        """
        Route a request to the appropriate model.
        
        Args:
            prompt: The user prompt.
            model_id: Optional specific model ID to force use.
            task_type: Optional manual task type override.
            **kwargs: Additional arguments passed to the API client.
        """
        
        # 1. Analyze Task
        requirements = self.analyzer.analyze(prompt)
        if task_type:
            requirements.task_type = task_type
            
        logger.info(f"Analyzed task: {requirements.task_type.name}, Priority: {requirements.priority}")

        # 2. Select Model
        selected_model_id = model_id
        if not selected_model_id:
            selected_model_id = self._select_best_model(requirements)
        
        if not selected_model_id:
            raise ValueError("No suitable model found for request")

        model_cap = self.registry.get_model(selected_model_id)
        if not model_cap:
             raise ValueError(f"Model {selected_model_id} not found in registry")

        logger.info(f"Selected model: {selected_model_id} ({model_cap.provider.value})")

        # 3. Execute Request
        try:
            return await self._call_model(model_cap, prompt, **kwargs)
        except Exception as e:
            logger.error(f"Primary model failed: {e}. Attempting fallback...")
            return await self._handle_fallback(requirements, prompt, failed_model=selected_model_id, **kwargs)

    def _select_best_model(self, requirements: TaskRequirements) -> Optional[str]:
        """Select the best model based on requirements and guide"""
        
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
                return valid_recs[0] # Return top recommendation

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

    async def _call_model(self, model: ModelCapabilities, prompt: str, **kwargs) -> APIResponse:
        """Call the specific model API"""
        client = self._get_client(model.provider.value)
        
        messages = [{"role": "user", "content": prompt}]
        if "messages" in kwargs:
            messages = kwargs.pop("messages")
            
        return await client.chat_completion(
            model=model.api_name,
            messages=messages,
            **kwargs
        )

    async def _handle_fallback(self, requirements: TaskRequirements, prompt: str, failed_model: str, **kwargs) -> APIResponse:
        """Handle fallback logic"""
        # Get fallback chain from guide
        chain = self.guide.get_fallback_chain(requirements.task_type.name)
        
        # If no chain, or failed model was last in chain, try to find next best scorer
        if not chain:
             # Simple fallback: try next best model from registry
             candidates = []
             for model in self.registry.get_all_models():
                if model.api_name == failed_model: 
                    continue
                score = self.scorer.score(model, requirements)
                if score > 0:
                    candidates.append((model.api_name, score))
             candidates.sort(key=lambda x: x[1], reverse=True)
             chain = [c[0] for c in candidates[:3]] # Try top 3
        
        for model_id in chain:
            if model_id == failed_model:
                continue
                
            logger.info(f"Fallback to: {model_id}")
            model_cap = self.registry.get_model(model_id)
            if not model_cap:
                continue
                
            try:
                return await self._call_model(model_cap, prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Fallback model {model_id} failed: {e}")
                continue
                
        raise RuntimeError("All fallback models failed")

    def _get_client(self, provider: str):
        """Get or create API client"""
        if provider not in self.clients:
            self.clients[provider] = get_api_client(provider)
        return self.clients[provider]
