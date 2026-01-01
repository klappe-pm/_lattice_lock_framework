"""Preferences repository for Firestore.

This module provides access to user preferences stored in Firestore.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from lattice_lock.database.gcp_clients import get_firestore_client

# Default user preferences
DEFAULT_PREFERENCES = {
    "theme": "system",
    "language": "en",
    "timezone": "UTC",
    "dateFormat": "YYYY-MM-DD",
    "editor": {
        "fontSize": 14,
        "fontFamily": "JetBrains Mono",
        "lineNumbers": True,
        "wordWrap": True,
        "tabSize": 2,
    },
    "defaultModels": {
        "chat": "claude-3-5-sonnet",
        "coding": "gpt-4-turbo",
        "reasoning": "o1-preview",
        "fast": "gpt-4o-mini",
    },
    "notifications": {
        "email": {
            "quotaWarnings": True,
            "weeklyDigest": False,
            "securityAlerts": True,
        },
        "inApp": {
            "taskComplete": True,
            "modelErrors": True,
        },
    },
    "dashboard": {
        "widgets": ["cost_overview", "usage_chart", "recent_activity"],
        "refreshInterval": 30,
    },
}


class PreferencesRepository:
    """Repository for user preferences in Firestore."""

    def __init__(self):
        """Initialize the repository."""
        self._client = None

    @property
    def client(self):
        """Lazy-load the Firestore client."""
        if self._client is None:
            self._client = get_firestore_client()
        return self._client

    def _user_prefs_ref(self, user_id: str):
        """Get the preferences document reference for a user."""
        return self.client.collection("users").document(user_id).collection("preferences").document("settings")

    async def get(self, user_id: str) -> dict[str, Any]:
        """Get user preferences, returning defaults if not set.
        
        Args:
            user_id: User ID.
            
        Returns:
            User preferences dictionary.
        """
        doc = await self._user_prefs_ref(user_id).get()

        if doc.exists:
            prefs = doc.to_dict()
            # Merge with defaults for any missing keys
            return self._merge_with_defaults(prefs)

        return DEFAULT_PREFERENCES.copy()

    async def update(
        self,
        user_id: str,
        preferences: dict[str, Any],
        merge: bool = True,
    ) -> dict[str, Any]:
        """Update user preferences.
        
        Args:
            user_id: User ID.
            preferences: Preferences to set/update.
            merge: If True, merge with existing; if False, replace entirely.
            
        Returns:
            Updated preferences.
        """
        prefs = {
            **preferences,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }

        await self._user_prefs_ref(user_id).set(prefs, merge=merge)

        return await self.get(user_id)

    async def update_nested(
        self,
        user_id: str,
        path: str,
        value: Any,
    ) -> None:
        """Update a nested preference value using dot notation.
        
        Args:
            user_id: User ID.
            path: Dot-notation path (e.g., 'editor.fontSize').
            value: New value.
        """
        # Firestore supports dot notation for nested updates
        await self._user_prefs_ref(user_id).update({
            path: value,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        })

    async def reset_to_defaults(self, user_id: str) -> dict[str, Any]:
        """Reset user preferences to defaults.
        
        Args:
            user_id: User ID.
            
        Returns:
            Default preferences.
        """
        prefs = {
            **DEFAULT_PREFERENCES,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
        await self._user_prefs_ref(user_id).set(prefs)
        return prefs

    async def delete(self, user_id: str) -> None:
        """Delete user preferences.
        
        Args:
            user_id: User ID.
        """
        await self._user_prefs_ref(user_id).delete()

    def _merge_with_defaults(self, prefs: dict[str, Any]) -> dict[str, Any]:
        """Deep merge preferences with defaults."""
        result = DEFAULT_PREFERENCES.copy()

        def deep_merge(base: dict, override: dict) -> dict:
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = deep_merge(base[key].copy(), value)
                else:
                    base[key] = value
            return base

        return deep_merge(result, prefs)


class OrganizationSettingsRepository:
    """Repository for organization settings in Firestore."""

    def __init__(self):
        """Initialize the repository."""
        self._client = None

    @property
    def client(self):
        """Lazy-load the Firestore client."""
        if self._client is None:
            self._client = get_firestore_client()
        return self._client

    def _org_settings_ref(self, org_id: str):
        """Get the settings document reference for an organization."""
        return self.client.collection("organizations").document(org_id).collection("settings").document("config")

    async def get(self, org_id: str) -> dict[str, Any]:
        """Get organization settings.
        
        Args:
            org_id: Organization ID.
            
        Returns:
            Organization settings dictionary.
        """
        doc = await self._org_settings_ref(org_id).get()

        if doc.exists:
            return doc.to_dict()

        return self._default_settings()

    async def update(
        self,
        org_id: str,
        settings: dict[str, Any],
        merge: bool = True,
    ) -> dict[str, Any]:
        """Update organization settings.
        
        Args:
            org_id: Organization ID.
            settings: Settings to set/update.
            merge: If True, merge with existing.
            
        Returns:
            Updated settings.
        """
        data = {
            **settings,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }

        await self._org_settings_ref(org_id).set(data, merge=merge)
        return await self.get(org_id)

    def _default_settings(self) -> dict[str, Any]:
        """Return default organization settings."""
        return {
            "branding": {
                "logoUrl": None,
                "primaryColor": "#3B82F6",
                "customDomain": None,
            },
            "security": {
                "enforceSSO": False,
                "allowedDomains": [],
                "sessionTimeoutMinutes": 480,
                "requireMFA": False,
                "ipAllowlist": [],
            },
            "modelPolicies": {
                "defaultProvider": "anthropic",
                "fallbackChain": ["anthropic", "openai", "google"],
                "blockedModels": [],
                "requireApprovalForNewModels": False,
            },
            "agentDefaults": {
                "maxChainLength": 5,
                "consensusThreshold": 0.7,
                "enableHandoffs": True,
                "autoRollbackOnError": True,
            },
        }
