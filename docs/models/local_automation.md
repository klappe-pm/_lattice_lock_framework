# Local Model Automation Reference

This document details the automation logic for managing local models via Ollama within the Model Orchestrator.

## 1. Overview
The `LocalModelManager` (now `model_orchestrator.local_manager`) automates the lifecycle of local LLMs. It handles:
- Discovery of installed models.
- RAM/VRAM resource monitoring.
- Smart model selection based on available resources.
- Keep-alive management to prevent frequent reloading.

## 2. Model Discovery
The system uses the `ollama` CLI to discover models.

- **Command**: `ollama list`
- **Parsed Data**:
    - Model Name (e.g., `llama3:8b`)
    - Size (e.g., `4.7 GB`)
    - Modified Time

## 3. Resource Management (RAM Awareness)
Before loading a model, the system checks available system RAM to prevent crashes or heavy swapping.

- **`RAMMonitor` Class**:
    - Uses `psutil` to check `available` memory.
    - **`can_load(model_size_gb)`**: Returns `True` if `available_ram > model_size_gb + buffer`.
    - **Buffer**: Defaults to 2GB to ensure OS stability.

## 4. Selection Logic (`select_best_model`)
When a local model is requested, the manager selects the best available model using this hierarchy:

1.  **Keep-Alive Models**: Checks if a suitable model is *already loaded* in memory (fastest).
2.  **Task Matching**:
    - If `TaskType` is `CODE_GENERATION` or `DEBUGGING`, it prioritizes models with "code" or "coder" in their name (e.g., `deepseek-coder`, `codellama`).
    - Otherwise, it defaults to general-purpose models (e.g., `llama3`, `mistral`).
3.  **Resource Check**: It filters out models that are too large for the current available RAM.
4.  **Fallback**: If the preferred model fits in RAM, it is selected. If not, it falls back to a smaller quantized version or a smaller model family (e.g., `8b` -> `7b` -> `phi`).

## 5. Keep-Alive System
To optimize performance for frequent requests, specific models can be designated as "keep-alive".

- **Configuration**: `KEEP_ALIVE_MODELS` list in `config`.
- **Mechanism**: The system periodically pings these models (or sets a long keep-alive timeout in the API call) to prevent them from being unloaded from VRAM.
- **Status Tracking**: The system tracks the currently loaded model to avoid redundant load calls.

## 6. Adding New Local Models
To add a new local model to the automation:
1.  **Pull the model**: `ollama pull <model_name>`
2.  **Update Config** (Optional): Add to `MODEL_SIZES` map if the size estimation needs to be precise, though the system auto-detects size from `ollama list`.
3.  **Tagging**: Ensure the model name reflects its capability (e.g., use `deepseek-coder` for coding tasks) so the selector recognizes it.
