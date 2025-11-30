#!/usr/bin/env python3
"""
RAM Monitoring Module for Model Orchestrator
Provides real-time RAM usage tracking and model capacity recommendations
"""

import subprocess
import json
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class RAMTier(Enum):
    """System RAM tier classification"""
    TIER_16GB = "16GB"
    TIER_32GB = "32GB+"
    TIER_64GB = "64GB+"


@dataclass
class RAMStatus:
    """Current RAM status"""
    total_gb: float
    used_gb: float
    free_gb: float
    available_gb: float
    utilization_percent: float
    tier: RAMTier

    def to_dict(self) -> Dict:
        return {
            "total_gb": round(self.total_gb, 2),
            "used_gb": round(self.used_gb, 2),
            "free_gb": round(self.free_gb, 2),
            "available_gb": round(self.available_gb, 2),
            "utilization_percent": round(self.utilization_percent, 1),
            "tier": self.tier.value,
        }


@dataclass
class ModelCapacity:
    """Model loading capacity recommendations"""
    tier: RAMTier
    max_concurrent_models: int
    recommended_models: list
    total_ram_budget_gb: float


class RAMMonitor:
    """Monitor system RAM and provide model capacity recommendations"""

    def __init__(self):
        self.total_ram = self._get_total_ram()
        self.tier = self._determine_tier()

    def _get_total_ram(self) -> float:
        """Get total system RAM in GB"""
        try:
            result = subprocess.run(
                ["sysctl", "hw.memsize"],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse: hw.memsize: 38654705664
            memsize = int(result.stdout.split(':')[1].strip())
            return memsize / (1024 ** 3)  # Convert to GB
        except Exception:
            return 0.0

    def _determine_tier(self) -> RAMTier:
        """Determine RAM tier based on total memory"""
        if self.total_ram >= 64:
            return RAMTier.TIER_64GB
        elif self.total_ram >= 32:
            return RAMTier.TIER_32GB
        else:
            return RAMTier.TIER_16GB

    def get_current_status(self) -> RAMStatus:
        """Get current RAM usage status"""
        try:
            result = subprocess.run(
                ["vm_stat"],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse vm_stat output
            lines = result.stdout.split("\n")
            pages = {}

            for line in lines:
                if "Pages" in line and ":" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[1].rstrip(":")
                        value = parts[2].rstrip(".")
                        try:
                            pages[key] = int(value)
                        except ValueError:
                            pass

            # Calculate RAM usage (page size = 4096 bytes)
            page_size = 4096
            active = pages.get("active", 0)
            wired = pages.get("wired", 0)
            free = pages.get("free", 0)
            inactive = pages.get("inactive", 0)

            used_gb = (active + wired) * page_size / (1024 ** 3)
            free_gb = free * page_size / (1024 ** 3)
            available_gb = (free + inactive) * page_size / (1024 ** 3)
            utilization = (used_gb / self.total_ram) * 100 if self.total_ram > 0 else 0

            return RAMStatus(
                total_gb=self.total_ram,
                used_gb=used_gb,
                free_gb=free_gb,
                available_gb=available_gb,
                utilization_percent=utilization,
                tier=self.tier
            )

        except Exception as e:
            # Return safe defaults on error
            return RAMStatus(
                total_gb=self.total_ram,
                used_gb=0,
                free_gb=0,
                available_gb=0,
                utilization_percent=0,
                tier=self.tier
            )

    def get_model_capacity(self) -> ModelCapacity:
        """Get recommended model capacity for current tier"""
        status = self.get_current_status()

        if self.tier == RAMTier.TIER_64GB:
            return ModelCapacity(
                tier=self.tier,
                max_concurrent_models=10,
                recommended_models=[
                    "deepseek-coder:1.3b",
                    "llama3.2:3b",
                    "magicoder:7b",
                    "llama3.1:8b",
                    "qwen2.5:7b-instruct",
                    "codellama:13b",
                    "qwen2.5:32b",
                    "codellama:34b",
                    "deepseek-r1:70b",
                    "llama3.1:70b",
                ],
                total_ram_budget_gb=60.0
            )
        elif self.tier == RAMTier.TIER_32GB:
            return ModelCapacity(
                tier=self.tier,
                max_concurrent_models=7,
                recommended_models=[
                    "deepseek-coder:1.3b",
                    "llama3.2:3b",
                    "magicoder:7b",
                    "llama3.1:8b",
                    "qwen2.5:7b-instruct",
                    "codellama:13b",
                    "qwen2.5:32b",
                ],
                total_ram_budget_gb=28.0
            )
        else:  # 16GB tier
            return ModelCapacity(
                tier=self.tier,
                max_concurrent_models=5,
                recommended_models=[
                    "deepseek-coder:1.3b",
                    "llama3.2:3b",
                    "magicoder:7b",
                    "llama3.1:8b",
                    "qwen2.5:7b-instruct",
                ],
                total_ram_budget_gb=14.0
            )

    def can_load_model(self, model_size_gb: float) -> Tuple[bool, str]:
        """
        Check if a model can be loaded given current RAM status

        Args:
            model_size_gb: Size of model in GB

        Returns:
            Tuple of (can_load, reason)
        """
        status = self.get_current_status()

        # Reserve 8GB for system
        available_for_models = status.available_gb - 8.0

        if available_for_models < model_size_gb:
            return False, f"Insufficient RAM: {available_for_models:.1f}GB available, {model_size_gb:.1f}GB needed"

        if status.utilization_percent > 85:
            return False, f"High RAM utilization: {status.utilization_percent:.1f}%"

        return True, "RAM available"

    def get_recommended_keep_alive_models(self) -> list:
        """Get recommended models for keep-alive based on tier and usage"""
        if self.tier == RAMTier.TIER_64GB:
            return [
                "deepseek-coder:1.3b",
                "magicoder:7b",
                "llama3.1:8b",
                "qwen2.5:7b-instruct",
                "codellama:13b",
            ]
        elif self.tier == RAMTier.TIER_32GB:
            return [
                "deepseek-coder:1.3b",
                "magicoder:7b",
                "llama3.1:8b",
                "qwen2.5:7b-instruct",
            ]
        else:  # 16GB
            return [
                "deepseek-coder:1.3b",
                "magicoder:7b",
                "llama3.1:8b",
            ]
