import logging
from string import Template
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PromptEngine:
    """
    Generates structured prompts from specifications.
    """
    PROMPT_TEMPLATE = Template("""
Role: Senior Python Engineer
Task: $task_type
Context Files:
$context

Goal:
$goal

Constraints:
- Strictly follow lattice.yaml rules.
- Add type hints to all functions.
""")

    def generate(self, spec: Dict[str, Any]) -> str:
        """
        Generates a prompt string based on the provided specification.
        """
        logger.info("Generating prompt from spec...")

        context_files = spec.get('files', [])
        context_str = "\n".join([f"- {f}" for f in context_files])

        return self.PROMPT_TEMPLATE.substitute(
            task_type=spec.get('type', 'Implementation'),
            context=context_str if context_str else "No context files provided.",
            goal=spec.get('goal', 'No goal provided.')
        )
