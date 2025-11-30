#!/usr/bin/env python3
"""
Local Model Manager
Integrates RAM monitoring and keep-alive system with Model Orchestrator
Provides intelligent local model selection and availability checking
"""

import json
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Import RAM monitor
from .ram_monitor import RAMMonitor, RAMStatus


@dataclass
class LocalModel:
    """Local model information"""
    name: str
    size_gb: float
    is_loaded: bool
    is_keep_alive: bool


class LocalModelManager:
    """
    Manages local Ollama models with RAM-aware selection
    Integrates with keep-alive system for optimal performance
    """

    # Model size mapping (GB)
    MODEL_SIZES = {
        "deepseek-coder:1.3b": 0.776,
        "llama3.2:3b": 2.0,
        "magicoder:7b": 3.8,
        "llama3.1:8b": 4.9,
        "llama3:8b": 4.7,
        "qwen2.5:7b-instruct": 4.7,
        "codellama:13b": 7.4,
        "codellama:13b-code": 7.4,
        "gemma:7b": 5.0,
        "qwen2.5:32b": 19.0,
        "mistral:7b": 4.4,
        "codellama:34b": 19.0,
        "llama3.1:70b": 42.0,
        "deepseek-r1:70b": 42.0,
    }

    # Keep-alive models (based on optimized-keep-alive.py)
    KEEP_ALIVE_MODELS = [
        "deepseek-coder:1.3b",
        "magicoder:7b",
        "llama3.1:8b",
        "qwen2.5:7b-instruct",
    ]

    # Status file from keep-alive system
    STATUS_FILE = "/tmp/model-keepalive-status.json"

    def __init__(self):
        self.ram_monitor = RAMMonitor()

    def get_installed_models(self) -> List[str]:
        """Get list of installed Ollama models"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )

            models = []
            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        models.append(model_name)

            return models
        except Exception:
            return []

    def get_loaded_models(self) -> List[str]:
        """Get currently loaded models from ollama ps"""
        try:
            result = subprocess.run(
                ["ollama", "ps"],
                capture_output=True,
                text=True,
                check=True
            )

            models = []
            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        models.append(model_name)

            return models
        except Exception:
            return []

    def get_keep_alive_status(self) -> Dict:
        """Get status from keep-alive system"""
        try:
            with open(self.STATUS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def get_model_info(self, model_name: str) -> Optional[LocalModel]:
        """Get detailed information about a specific model"""
        if model_name not in self.MODEL_SIZES:
            return None

        loaded_models = self.get_loaded_models()
        keep_alive_status = self.get_keep_alive_status()

        return LocalModel(
            name=model_name,
            size_gb=self.MODEL_SIZES[model_name],
            is_loaded=model_name in loaded_models,
            is_keep_alive=model_name in keep_alive_status and
                          keep_alive_status[model_name].get("status") == "active"
        )

    def can_load_model(self, model_name: str) -> Tuple[bool, str]:
        """Check if a model can be loaded given current RAM"""
        if model_name not in self.MODEL_SIZES:
            return False, f"Unknown model: {model_name}"

        model_size = self.MODEL_SIZES[model_name]
        can_load, reason = self.ram_monitor.can_load_model(model_size)

        return can_load, reason

    def select_best_model(self, task_type: str, candidates: List[str]) -> Optional[str]:
        """
        Select best available model for task from candidates
        Prioritizes: keep-alive models > loaded models > installable models

        Args:
            task_type: Type of task (code, docs, reasoning, etc.)
            candidates: List of candidate model names

        Returns:
            Best model name or None
        """
        keep_alive_status = self.get_keep_alive_status()
        loaded_models = set(self.get_loaded_models())

        # Score models
        scored_models = []
        for model in candidates:
            if model not in self.MODEL_SIZES:
                continue

            score = 0

            # Highest priority: keep-alive and active
            if (model in keep_alive_status and
                keep_alive_status[model].get("status") == "active"):
                score += 1000

            # Medium priority: already loaded
            elif model in loaded_models:
                score += 500

            # Check if can load
            can_load, _ = self.can_load_model(model)
            if can_load:
                score += 100

            # Prefer smaller models for faster response (efficiency bonus)
            size = self.MODEL_SIZES[model]
            if size < 5:
                score += 50
            elif size < 10:
                score += 25

            scored_models.append((model, score))

        if not scored_models:
            return None

        # Return highest scored model
        scored_models.sort(key=lambda x: x[1], reverse=True)
        return scored_models[0][0]

    def get_recommended_models_for_task(self, task_type: str) -> List[str]:
        """Get recommended models for specific task type"""
        task_recommendations = {
            "code_generation": [
                "deepseek-coder:1.3b",
                "magicoder:7b",
                "codellama:13b",
                "codellama:34b",
            ],
            "code_review": [
                "magicoder:7b",
                "codellama:13b",
                "deepseek-coder:1.3b",
            ],
            "documentation": [
                "llama3.1:8b",
                "qwen2.5:7b-instruct",
                "llama3.2:3b",
            ],
            "reasoning": [
                "qwen2.5:32b",
                "llama3.1:8b",
                "deepseek-r1:70b",
            ],
            "general": [
                "llama3.1:8b",
                "llama3.2:3b",
                "qwen2.5:7b-instruct",
            ],
        }

        return task_recommendations.get(task_type, task_recommendations["general"])

    def get_status_summary(self) -> Dict:
        """Get comprehensive status summary"""
        ram_status = self.ram_monitor.get_current_status()
        keep_alive_status = self.get_keep_alive_status()
        loaded_models = self.get_loaded_models()
        installed_models = self.get_installed_models()
        capacity = self.ram_monitor.get_model_capacity()

        return {
            "ram": ram_status.to_dict(),
            "models": {
                "installed": len(installed_models),
                "loaded": len(loaded_models),
                "keep_alive_active": sum(
                    1 for s in keep_alive_status.values()
                    if s.get("status") == "active"
                ),
            },
            "keep_alive_models": list(keep_alive_status.keys()),
            "loaded_models": loaded_models,
            "capacity": {
                "tier": capacity.tier.value,
                "max_concurrent_models": capacity.max_concurrent_models,
                "recommended_models": capacity.recommended_models,
                "total_ram_budget_gb": capacity.total_ram_budget_gb,
            },
        }
