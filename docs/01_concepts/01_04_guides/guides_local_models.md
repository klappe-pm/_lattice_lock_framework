# Local Model Fallback Guide

Lattice Lock supports robust local model fallback to ensure continuity when primary cloud providers are unavailable or strictly for cost saving/privacy reasons.

## Configuration

Model selection rules are defined in `MODELS.md` in the project root. The Orchestrator uses this file to determine which models to use for specific tasks.

### Structure of MODELS.md

```markdown
### Code Tasks
- **code_generation**: codellama:34b > magicoder:7b > grok-code-fast-1
- **reasoning**: o1-pro > grok-4-fast-reasoning > gemini-2.5-pro
- **translation**: qwen2.5-32b-instruct > qwen3:8b > gemini-2.5-flash

### Blocked Models
- llama3.2

### Fallback Chains
- code_generation: codellama:34b → magicoder:7b
- reasoning: o1-pro → grok-4-fast-reasoning
```

- **Task Mappings (`>`)**: Defines priority order. If the first model fails or is unavailable, the system tries the next.
- **Blocked Models**: Explicitly prevents usage of specific models (e.g., due to license issues or known bugs).
- **Fallback Chains (`→`)**: Explicitly defines the sequence of attempts.

## Setting Up Local Models (Ollama)

1.  **Install Ollama**: Follow instructions at [ollama.ai](https://ollama.ai).
2.  **Pull Recommended Models**:
    ```bash
    ollama pull codellama:34b
    ollama pull magicoder:7b
    ollama pull qwen2.5-32b-instruct
    ```
3.  **Verify Availability**:
    Ensure the models are running or available to be loaded. The Lattice Lock framework will attempt to connect to the local Ollama instance (default: `http://localhost:11434`) when a local model is selected.

## Troubleshooting

- **Model Not Found**: Ensure the model name in `MODELS.md` matches exactly with `ollama list`.
- **Performance**: Local inference depends heavily on available RAM/VRAM. Use smaller quantized models (e.g., `7b` or `8b`) if running on consumer hardware.
