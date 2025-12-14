
# IMPLEMENTATION PROTOTYPE (Agent D_6_3_8)
# Task 6.3.8: Task Analyzer v2 Implementation

import re

class TaskAnalyzer:
    def __init__(self):
        # Heuristics (Regex)
        self.patterns = {
            "CODE_GENERATION": [r"def .+\(", r"class .+\:", r"import .+"].copy(),
            "TESTING": [r"test", r"pytest", r"assert", r"mock"].copy(),
            "DEBUGGING": [r"fix", r"error", r"exception", r"traceback"].copy()
        }

    def analyze(self, user_prompt: str):
        print(f"[ANALYZER] Analyzing: '{user_prompt}'")

        # 1. Fast Heuristics
        for task_type, regexes in self.patterns.items():
            for pattern in regexes:
                if re.search(pattern, user_prompt, re.IGNORECASE):
                    print(f"  [MATCH] Heuristic Match: {task_type} (Pattern: {pattern})")
                    return task_type

        # 2. Fallback to LLM (Simulated)
        print("  [LLM] Heuristics failed. Calling Router Model...")
        return "GENERAL"

if __name__ == "__main__":
    analyzer = TaskAnalyzer()
    analyzer.analyze("def hello_world(): pass") # Should be CODE
    analyzer.analyze("Why is my code crashing with ValueError?") # Should be DEBUG
    analyzer.analyze("Tell me a joke") # Should be GENERAL
