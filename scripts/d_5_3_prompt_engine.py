
# IMPLEMENTATION PROTOTYPE (Agent D_5_3)
# Task 5.3: Prompt Generation Engine

import json
from string import Template

PROMPT_TEMPLATE = Template("""
Role: $role
Task: $task_type
Context:
$context
Instructions:
$instructions
""")

class PromptEngine:
    def generate(self, spec: dict) -> str:
        print("[ENGINE] Generating prompt from spec...")
        
        context_str = "\n".join([f"- {f}" for f in spec.get('files', [])])
        
        return PROMPT_TEMPLATE.substitute(
            role="Senior Python Engineer",
            task_type=spec.get('type', 'Implementation'),
            context=context_str,
            instructions=spec.get('goal', 'Do the thing')
        )

if __name__ == "__main__":
    engine = PromptEngine()
    spec = {
        "type": "Code Generation",
        "files": ["src/main.py", "tests/test_main.py"],
        "goal": "Implement the login logic"
    }
    result = engine.generate(spec)
    print("--- GENERATED PROMPT ---")
    print(result)
    print("------------------------")
