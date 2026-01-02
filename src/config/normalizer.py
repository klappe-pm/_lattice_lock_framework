from typing import Dict, Any, List, Optional
import hashlib
import json

class JSONNormalizer:
    """
    Normalizes a configuration dictionary into a relational JSON structure.
    Used to optimize context window usage and reduce duplication in LLM contexts.
    """

    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for normalization.
        Detects structure and applies appropriate strategies.
        """
        normalized = data.copy()
        
        if 'agents' in normalized and isinstance(normalized['agents'], list):
            self._normalize_agents(normalized)
            
        return normalized

    def _normalize_agents(self, data: Dict[str, Any]):
        """
        Relational Normalization for Agents.
        Extracts 'provider_preferences' and 'subagents' to top-level lists.
        """
        agents = data['agents']
        all_prefs = []
        all_sub_refs = []
        
        for agent in agents:
            if not isinstance(agent, dict):
                continue
                
            agent_id = agent.get('id') or self._generate_id(agent.get('name', 'unknown'))
            agent['id'] = agent_id # Ensure ID exists
            
            # 1. Normalize Provider Preferences
            if 'provider_preferences' in agent and isinstance(agent['provider_preferences'], list):
                pref_ids = []
                for idx, pref in enumerate(agent['provider_preferences']):
                    pref_id = f"pref_{agent_id}_{idx}"
                    # Create normalized entry
                    norm_pref = pref.copy()
                    norm_pref['id'] = pref_id
                    norm_pref['agent_id'] = agent_id
                    all_prefs.append(norm_pref)
                    pref_ids.append(pref_id)
                
                # Replace list with IDs
                agent['provider_preferences'] = pref_ids

            # 2. Normalize Subagents
            if 'subagents' in agent and isinstance(agent['subagents'], list):
                sub_ids = []
                for idx, sub in enumerate(agent['subagents']):
                    # If sub is just a string (ref), keep it? Or object?
                    # Assuming object definition as per plan
                    if isinstance(sub, dict):
                        sub_id = sub.get('id') or f"sub_{agent_id}_{idx}"
                        norm_sub = sub.copy()
                        norm_sub['id'] = sub_id
                        norm_sub['agent_id'] = agent_id
                        all_sub_refs.append(norm_sub)
                        sub_ids.append(sub_id)
                    else:
                         # Already a ref or string
                         sub_ids.append(str(sub))
                
                agent['subagents'] = sub_ids

        # Add extracted lists to top level
        if all_prefs:
            if 'provider_preferences' not in data:
                data['provider_preferences'] = []
            data['provider_preferences'].extend(all_prefs)
            
        if all_sub_refs:
            if 'subagent_refs' not in data:
                data['subagent_refs'] = []
            data['subagent_refs'].extend(all_sub_refs)

    def _generate_id(self, source: str) -> str:
        """Generates a stable short ID from a string."""
        hash_object = hashlib.md5(source.encode())
        return f"id_{hash_object.hexdigest()[:8]}"
