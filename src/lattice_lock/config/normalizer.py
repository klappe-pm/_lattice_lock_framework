import hashlib
from typing import Any


class JSONNormalizer:
    """Normalizes configuration dictionary into relational JSON structure."""

    def normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        """Main entry point for normalization."""
        normalized = data.copy()

        if "agents" in normalized and isinstance(normalized["agents"], list):
            self._normalize_agents(normalized)

        return normalized

    def _normalize_agents(self, data: dict[str, Any]):
        """Relational Normalization for Agents."""
        agents = data["agents"]
        all_prefs = []
        all_sub_refs = []

        for agent in agents:
            if not isinstance(agent, dict):
                continue

            agent_id = agent.get("id") or self._generate_id(agent.get("name", "unknown"))
            agent["id"] = agent_id

            if "provider_preferences" in agent and isinstance(agent["provider_preferences"], list):
                pref_ids = []
                for idx, pref in enumerate(agent["provider_preferences"]):
                    pref_id = f"pref_{agent_id}_{idx}"
                    norm_pref = pref.copy()
                    norm_pref["id"] = pref_id
                    norm_pref["agent_id"] = agent_id
                    all_prefs.append(norm_pref)
                    pref_ids.append(pref_id)
                agent["provider_preferences"] = pref_ids

            if "subagents" in agent and isinstance(agent["subagents"], list):
                sub_ids = []
                for idx, sub in enumerate(agent["subagents"]):
                    if isinstance(sub, dict):
                        sub_id = sub.get("id") or f"sub_{agent_id}_{idx}"
                        norm_sub = sub.copy()
                        norm_sub["id"] = sub_id
                        norm_sub["agent_id"] = agent_id
                        all_sub_refs.append(norm_sub)
                        sub_ids.append(sub_id)
                    else:
                        sub_ids.append(str(sub))
                agent["subagents"] = sub_ids

        if all_prefs:
            data.setdefault("provider_preferences", []).extend(all_prefs)
        if all_sub_refs:
            data.setdefault("subagent_refs", []).extend(all_sub_refs)

    def _generate_id(self, source: str) -> str:
        """Generates a stable short ID from a string."""
        hash_object = hashlib.md5(source.encode())
        return f"id_{hash_object.hexdigest()[:8]}"
