# Local Models Setup Guide

## Overview

This guide covers setting up and using **18 local AI models** with the Power Prompts orchestration system. Local models provide:

- **🆓 Zero Cost**: No API fees, unlimited usage
- **🔒 Full Privacy**: All processing happens locally
- **⚡ High Performance**: No network latency
- **🔌 Offline Capable**: Works without internet connection
- **🎯 Intelligent Integration**: Seamless orchestration with cloud models

## Supported Local Model Servers

### Ollama (Recommended)

- **Best For**: Easy setup, wide model support, good performance
- **Supported Models**: All Llama family models, Mistral, CodeLlama, and more
- **Platform**: macOS, Linux, Windows

### Other Supported Servers

- **LM Studio**: GUI-based local model serving
- **Text Generation Web UI**: Advanced features and customization
- **vLLM**: High-performance inference server
- **Custom OpenAI-compatible servers**: Any server with OpenAI API compatibility

## Ollama Installation (macOS)

### Option 1: Direct Download (Recommended)

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

### Option 2: Homebrew

```bash
# Install via Homebrew
brew install ollama

# Start Ollama service
brew services start ollama
```

### Option 3: Manual Installation

1. Download from: <https://ollama.com/download/mac>
2. Install the.dmg file
3. Run Ollama from Applications

## Starting Ollama Service

### Background Service (Recommended)

```bash
# Start Ollama service in background
ollama serve

# Or start as system service (macOS)
brew services start ollama
```

### Check Service Status

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Expected response: {"version":"0.1.x"}
```

## Installing Local Models

### Llama Models (Configured in Orchestrator)

#### Llama 3.2 Family

```bash
# Llama 3.2 90B (large, high quality)
ollama pull llama3.2:90b

# Llama 3.2 11B (medium, vision capable)
ollama pull llama3.2:11b-vision

# Llama 3.2 3B (small, fast)
ollama pull llama3.2:3b
```

#### Llama 3.1 Family

```bash
# Llama 3.1 405B (largest, best quality - requires significant RAM)
ollama pull llama3.1:405b

# Llama 3.1 70B (large, high quality)
ollama pull llama3.1:70b

# Llama 3.1 8B (medium, balanced)
ollama pull llama3.1:8b
```

#### Llama 3 Family

```bash
# Llama 3 70B (large, high quality)
ollama pull llama3:70b

# Llama 3 8B (medium, balanced)
ollama pull llama3:8b
```

### Other Recommended Models

```bash
# Code-focused models
ollama pull codellama:13b-code
ollama pull codellama:34b-code

# Qwen2.5 models (Alibaba Cloud)
ollama pull qwen2.5:32b-instruct-q4_K_M  # High-quality multilingual model
ollama pull qwen2.5:14b-instruct         # Balanced performance
ollama pull qwen2.5:7b-instruct          # Fast, efficient

# Mistral models
ollama pull mistral:7b
ollama pull mixtral:8x7b

# Specialized models
ollama pull phi3:3.8b        # Microsoft Phi-3
ollama pull gemma:7b         # Google Gemma
```

## Model Management

### List Installed Models

```bash
# Show all locally available models
ollama list
```

### Remove Models

```bash
# Remove specific model
ollama rm llama3.2:90b

# Remove all versions of a model
ollama rm llama3.2
```

### Update Models

```bash
# Update to latest version
ollama pull llama3.2:latest
```

## Testing Local Models

### Basic Test with Ollama CLI

```bash
# Test Llama 3.2 8B
ollama run llama3.2:8b "What is the capital of France?"

# Test with code generation
ollama run codellama:13b "Write a Python function to calculate fibonacci numbers"
```

### Test with Power Prompts Orchestrator

```bash
# Test local model integration
./orchestrator-cli.py analyze "Write a simple Python function"

# Test specific local model
./orchestrator-cli.py route "Hello, how are you?" --strategy cost_optimize
```

### Test API Connectivity

```bash
# Test Ollama API directly
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:8b",
    "prompt": "Hello world",
    "stream": false
  }'
```

## Integration with Model Orchestrator

### Local Model Configuration

The orchestrator is pre-configured with **18 local models** across different providers:

#### Meta Llama Models (9 models)

- `llama-3.2-90b` → `llama3.2:90b` (Vision capable)
- `llama-3.2-11b` → `llama3.2:11b` (Vision capable)
- `llama-3.2-3b` → `llama3.2:3b` (Lightweight)
- `llama-3.1-405b` → `llama3.1:405b` (Largest model)
- `llama-3.1-70b` → `llama3.1:70b` (High quality)
- `llama-3.1-8b` → `llama3.1:8b` (Balanced)
- `llama-3-70b` → `llama3:70b` (Previous gen high quality)
- `llama-3-8b` → `llama3:8b` (Previous gen balanced)
- `llama3.2` → `llama3.2` (Alias)

#### Code-Specialized Models (3 models)

- `codellama:34b` → **Best overall code quality**
- `codellama:13b` → **Balanced code performance**
- `magicoder:7b` → **Optimal code generation balance**

#### Qwen Models (2 models)

- `qwen2.5:32b-instruct` → High-quality multilingual model
- `qwen3:8b` → Multilingual reasoning capabilities

#### DeepSeek Models (2 models)

- `deepseek-r1:70b` → **Ultimate reasoning model**
- `deepseek-coder:1.3b` → Ultra-fast code generation

#### Additional Models (2 models)

- `llama3.1:8b` → General purpose model
- `llama3.2:3b` → Lightweight conversation model

### ✅ Currently Installed Models (11 models)

Based on your current setup:

| Model | Size | Status | Purpose |
|-------|------|--------|----------|
| deepseek-r1:70b | 42GB | ✅ Installed | Ultimate reasoning |
| codellama:34b | 19GB | ✅ Installed | Best code quality |
| qwen2.5:32b | 19GB | ✅ Installed | Premium intelligence |
| codellama:13b | 7.4GB | ✅ Installed | High-quality code |
| qwen3:8b | 5.2GB | ✅ Installed | Multilingual reasoning |
| llama3.1:8b | 4.9GB | ✅ Installed | General tasks |
| llama3:8b | 4.7GB | ✅ Installed | General conversations |
| magicoder:7b | 3.8GB | ✅ Installed | Optimal code balance |
| llama3.2:3b | 2.0GB | ✅ Installed | Fast conversations |
| deepseek-coder:1.3b | 776MB | ✅ Installed | Quick code snippets |
| codellama:13b-code | 7.4GB | ✅ Installed | Code generation focus |

### Custom Local Model Server

If using a different server or port:

```bash
# Set custom local server URL
export CUSTOM_API_URL="http://localhost:8080/v1"

# Or configure in the orchestrator
./orchestrator-cli.py --help
```

## Performance Optimization

### Hardware Requirements

#### Minimum System Requirements

- **RAM**: 8GB (for 3B-8B models)
- **CPU**: Modern multi-core processor
- **Storage**: 10-50GB per model

#### Recommended System Requirements

- **RAM**: 32GB+ (for 70B+ models)
- **CPU**: Apple Silicon (M1/M2/M3) or high-end Intel
- **Storage**: SSD with 100GB+ free space
- **GPU**: Dedicated GPU (optional but improves performance)

### Model Size vs Performance

| Model Size | RAM Needed | Speed | Quality | Best For |
|------------|------------|--------|---------|-----------|
| 3B-8B | 8-16GB | Fast | Good | General chat, simple tasks |
| 13B-20B | 16-32GB | Medium | Better | Code generation, analysis |
| 32B (Qwen2.5) | 20-32GB | Medium | High | Multilingual, reasoning, tools |
| 34B-70B | 32-64GB | Slower | High | Complex reasoning, professional use |
| 405B+ | 200GB+ | Very Slow | Excellent | Research, specialized tasks |

### Performance Tuning

#### Ollama Configuration

```bash
# Set GPU layers (if available)
export OLLAMA_GPU_LAYERS=32

# Set number of CPU threads
export OLLAMA_NUM_THREADS=8

# Set context window size
export OLLAMA_CONTEXT_SIZE=4096
```

#### Memory Management

```bash
# Monitor memory usage
ollama ps

# Stop running models to free memory
ollama stop llama3.2:90b
```

## Startup Scripts

### Ollama Startup Script

Create `start-ollama.sh`:

```bash
#!/bin/bash
echo "Starting Ollama service..."

# Check if Ollama is already running
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama is already running"
else
    echo "🚀 Starting Ollama service..."

    # Start Ollama in background
    nohup ollama serve > ollama.log 2>&1 &

    # Wait for service to start
    sleep 3

    # Verify startup
    if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo "✅ Ollama started successfully"
    else
        echo "❌ Failed to start Ollama"
        exit 1
    fi
fi

echo "📊 Available models:"
ollama list
```

### Model Warmup Script

Create `warmup-models.sh`:

```bash
#!/bin/bash
echo "🔥 Warming up local models..."

models=("llama3.2:8b" "llama3.1:8b" "codellama:13b")

for model in "${models[@]}"; do
    if ollama list | grep -q "$model"; then
        echo "Warming up $model..."
        ollama run "$model" "Hello" --verbose=false > /dev/null 2>&1
        echo "✅ $model ready"
    else
        echo "⚠️ $model not installed, skipping"
    fi
done

echo "🎉 Local models warmed up and ready!"
```

## Troubleshooting

### Common Issues

#### "Connection refused" Error

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# If not running, start it
ollama serve
```

#### Out of memory errors

```bash
# Check memory usage
ollama ps

# Stop large models
ollama stop llama3.1:405b

# Use smaller models
ollama run llama3.2:3b
```

#### Slow performance

```bash
# Check system resources
top -o MEM

# Use GPU acceleration if available
export OLLAMA_GPU_LAYERS=32

# Reduce context size
export OLLAMA_CONTEXT_SIZE=2048
```

### Debugging Commands

```bash
# Check Ollama logs
tail -f ollama.log

# Test model loading
ollama run llama3.2:8b "test" --verbose

# Check system resources
ollama ps
htop
```

## Integration Examples

### Using with Python

```python
import requests

# Test local model via API
response = requests.post('http://localhost:11434/api/generate',
    json={
        'model': 'llama3.2:8b',
        'prompt': 'Explain Python decorators',
        'stream': False
    })

print(response.json()['response'])
```

### Using with Orchestrator

```python
from model_orchestrator import ModelOrchestrator

orchestrator = ModelOrchestrator()

# Will automatically select local models for cost optimization
model_id, model = orchestrator.select_model(
    "Write a Python function",
    strategy="cost_optimize"
)

print(f"Selected: {model_id}")
# Output: Selected: llama-3.2-8b (local, $0.00 cost)
```

## Best Practices

### Model Selection Strategy

1. **Development/Testing**: Use 3B-8B models for speed
2. **Production**: Use 13B-70B models for quality
3. **Research**: Use 405B+ models for complex tasks
4. **Code**: Use CodeLlama models for programming tasks

### Resource Management

1. **Load models on demand**: Don't keep all models loaded
2. **Monitor memory usage**: Use `ollama ps` regularly
3. **Use appropriate model sizes**: Match model to task complexity
4. **Warm up frequently used models**: Pre-load for better response times

### Security Considerations

1. **Local models are private**: No data sent to external servers
2. **Network isolation**: Can run completely offline
3. **Access control**: Secure local API endpoints if needed
4. **Model verification**: Verify model checksums after download

## Next Steps

1. **Install Ollama**: Follow installation instructions above
2. **Download models**: Start with `llama3.2:8b` for testing
3. **Test integration**: Run orchestrator commands
4. **Optimize performance**: Tune based on your hardware
5. **Scale up**: Add larger models as needed

For questions or issues, refer to:

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Model Orchestrator README](orchestrator-readme.md)
- [WARP](WARP.md) for development guidance
