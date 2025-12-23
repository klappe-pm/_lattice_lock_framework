# Model Selection Guide

This file controls the model selection logic for the Lattice Lock Orchestrator.

### Code Tasks
- **code_generation**: codellama:34b > magicoder:7b > grok-code-fast-1
- **reasoning**: o1-pro > grok-4-fast-reasoning > gemini-2.5-pro
- **translation**: qwen2.5-32b-instruct > qwen3:8b > gemini-2.5-flash

### Blocked Models
- llama3.2

### Fallback Chains
- code_generation: codellama:34b → magicoder:7b
- reasoning: o1-pro → grok-4-fast-reasoning
