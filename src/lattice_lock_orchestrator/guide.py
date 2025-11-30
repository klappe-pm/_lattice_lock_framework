import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ModelGuideParser:
    """Parse MODELS.md for model selection guidance"""

    def __init__(self, guide_path: Optional[str] = None):
        default_path = Path.home() / "Obsidian/Power Prompts/gitignore/Claude Context/MODELS.md"
        self.guide_path = Path(guide_path) if guide_path else default_path
        self.rules = self._parse_guide()

    def _parse_guide(self) -> Dict[str, Any]:
        """Parse the MODELS.md file for rules"""
        if not self.guide_path.exists():
            logger.warning(f"MODELS.md not found at {self.guide_path}")
            return self._get_default_rules()

        try:
            with open(self.guide_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read MODELS.md: {e}")
            return self._get_default_rules()

        rules = {
            "task_mappings": {},
            "fallback_chains": {},
            "blocked_models": [],
        }

        # Parse task-to-model mappings
        task_section = re.search(r'### Code Tasks(.*?)###', content, re.DOTALL)
        if task_section:
            lines = task_section.group(1).strip().split('\n')
            for line in lines:
                if '**' in line and ':' in line:
                    match = re.match(r'- \*\*(.+?)\*\*: (.+)', line)
                    if match:
                        task = match.group(1).lower().replace(' ', '_')
                        models = [m.strip() for m in match.group(2).split('>')]
                        rules["task_mappings"][task] = models

        # Parse blocked models
        blocked_section = re.search(r'### Blocked Models(.*?)##', content, re.DOTALL)
        if blocked_section:
            lines = blocked_section.group(1).strip().split('\n')
            for line in lines:
                if line.startswith('- '):
                    model = line.split(':')[0].replace('- ', '').strip()
                    rules["blocked_models"].append(model)

        # Parse fallback chains
        fallback_section = re.search(r'### Fallback Chains(.*?)###', content, re.DOTALL)
        if fallback_section:
            lines = fallback_section.group(1).strip().split('\n')
            for line in lines:
                if '→' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        task = parts[0].replace('- ', '').strip().lower()
                        chain = [m.strip() for m in parts[1].split('→')]
                        rules["fallback_chains"][task] = chain

        return rules

    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default rules when MODELS.md is not available"""
        return {
            "task_mappings": {
                "code_generation": ["codellama:34b", "magicoder:7b", "grok-code-fast-1"],
                "reasoning": ["o1-pro", "grok-4-fast-reasoning", "gemini-2.5-pro"],
                "translation": ["qwen2.5-32b-instruct", "qwen3:8b", "gemini-2.5-flash"]
            },
            "fallback_chains": {},
            "blocked_models": ["llama3.2"],
        }

    def get_recommended_models(self, task_type: str) -> List[str]:
        """Get recommended models for a task type"""
        task_key = task_type.lower().replace(' ', '_')
        return self.rules.get("task_mappings", {}).get(task_key, [])

    def get_fallback_chain(self, task_type: str) -> List[str]:
        """Get fallback chain for a task"""
        return self.rules.get("fallback_chains", {}).get(task_type.lower(), [])

    def is_model_blocked(self, model_id: str) -> bool:
        """Check if model is blocked"""
        return model_id in self.rules.get("blocked_models", [])
