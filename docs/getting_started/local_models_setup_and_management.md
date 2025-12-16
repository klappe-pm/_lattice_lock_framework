# Local Models Setup and Management

## Local Models Setup and Management

```bash
# Install Ollama (macOS)
curl -fsSL https://ollama.com/install.sh | sh
# Or: brew install ollama

# Start Ollama service (automated script)
./start-ollama.sh

# Install recommended models
ollama pull llama3.2:8b      # Balanced performance
ollama pull llama3.2:3b      # Fast, lightweight
ollama pull qwen2.5:32b-instruct-q4_K_M  # High-quality multilingual
ollama pull llama3.1:70b     # High quality (requires 64GB+ RAM)
ollama pull gemma:7b         # Google's balanced model (NEW!)
ollama pull qwen2.5:7b-instruct  # Instruction-tuned Qwen (NEW!)
ollama pull codellama:13b-code # Code generation

# Warm up models for better performance
./warmup-models.sh

# Test local model integration
./orchestrator-cli.py analyze "Write a Python function" --strategy cost_optimize

# Monitor local models
ollama ps              # Show loaded models
ollama list            # Show installed models
```
