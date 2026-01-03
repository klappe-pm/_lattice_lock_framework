"""
Feature Flags System for Lattice Lock Framework.

Centralized management of optional features via environment variables and presets.
"""

import logging
import os
from enum import Enum
from functools import lru_cache

logger = logging.getLogger(__name__)


class Feature(str, Enum):
    """Available features that can be toggled."""

    SHERIFF = "sheriff"
    GAUNTLET = "gauntlet"
    FEEDBACK = "feedback"
    ROLLBACK = "rollback"
    CONSENSUS = "consensus"
    MCP = "mcp"


class FeaturePreset(str, Enum):
    """Configuration presets."""

    MINIMAL = "minimal"  # Core orchestrator only
    STANDARD = "standard"  # Orchestrator + Sheriff + Gauntlet
    FULL = "full"  # All features enabled


# Presets define what is ENABLED by default for that preset
_PRESET_DEFINITIONS = {
    FeaturePreset.MINIMAL: set(),
    FeaturePreset.STANDARD: {Feature.SHERIFF, Feature.GAUNTLET},
    FeaturePreset.FULL: {
        Feature.SHERIFF,
        Feature.GAUNTLET,
        Feature.FEEDBACK,
        Feature.ROLLBACK,
        Feature.CONSENSUS,
        Feature.MCP,
    },
}


@lru_cache(maxsize=1)
def _get_enabled_features() -> set[str]:
    """Calculate the set of enabled features based on configuration."""
    # 1. Start with preset baseline
    preset_name = os.getenv("LATTICE_FEATURE_PRESET", "full").lower()
    try:
        preset = FeaturePreset(preset_name)
    except ValueError:
        logger.warning(f"Unknown feature preset '{preset_name}', defaulting to FULL")
        preset = FeaturePreset.FULL

    enabled = _PRESET_DEFINITIONS.get(preset, _PRESET_DEFINITIONS[FeaturePreset.FULL]).copy()

    # 2. Apply explicit disables from env var
    disabled_env = os.getenv("LATTICE_DISABLED_FEATURES", "")
    if disabled_env:
        for f in disabled_env.split(","):
            f_clean = f.strip().lower()
            # Remove matching feature strings
            # We iterate over enum values to match
            for feature in Feature:
                if feature.value == f_clean:
                    enabled.discard(feature)

    # 3. Apply runtime overrides
    for feature_name, is_enabled in _RUNTIME_OVERRIDES.items():
        feature_enum = None
        for f in Feature:
             if f.value == feature_name:
                 feature_enum = f
                 break

        if feature_enum:
             if is_enabled:
                 enabled.add(feature_enum)
             else:
                 enabled.discard(feature_enum)

    return {f.value for f in enabled}

import threading

# Global dictionary for runtime overrides (feature_name -> enabled)
_RUNTIME_OVERRIDES: dict[str, bool] = {}
_OVERRIDE_LOCK = threading.Lock()

def override_feature(feature: str | Feature, enabled: bool):
    """
    Override a feature flag at runtime.
    
    Args:
        feature: Feature to override
        enabled: Whether to enable or disable
    """
    feature_name = feature.value if isinstance(feature, Feature) else feature.lower()
    with _OVERRIDE_LOCK:
        _RUNTIME_OVERRIDES[feature_name] = enabled
        _get_enabled_features.cache_clear()
    logger.info(f"Feature '{feature_name}' runtime override set to: {enabled}")


def is_feature_enabled(feature: str | Feature) -> bool:
    """
    Check if a feature is enabled.
    
    Args:
        feature: Feature enum or string name
    
    Returns:
        bool: True if feature is enabled
    """
    if isinstance(feature, Feature):
        feature_name = feature.value
    else:
        feature_name = feature.lower()

    enabled_features = _get_enabled_features()
    return feature_name in enabled_features


def assert_feature_enabled(feature: str | Feature):
    """
    Raise detailed error if feature is disabled.

    Args:
        feature: Feature to check

    Raises:
        RuntimeError: If feature is disabled
    """
    if not is_feature_enabled(feature):
        raise RuntimeError(
            f"Feature '{feature}' is currently disabled. "
            f"Check LATTICE_DISABLED_FEATURES or LATTICE_FEATURE_PRESET."
        )
