---
title: local_models
type: guide
status: stable
categories: [guides, configuration]
sub_categories: [local_models]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [guide-local-models-001]
tags: [guide, local_models, ollama, setup]
---

# Local Models Setup and Management Guide

## Overview

This guide covers setting up and using local AI models with Lattice Lock. Local models provide:

- **🆓 Zero Cost**: No API fees, unlimited usage
- **🔒 Full Privacy**: All processing happens locally
- **⚡ High Performance**: No network latency
- **🔌 Offline Capable**: Works without internet connection
- **🎯 Intelligent Integration**: Seamless orchestration with cloud models
- **🔄 Automatic Fallback**: Ensures continuity when cloud providers are unavailable

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

## Installation

### Ollama Installation (macOS)

#### Option 1: Direct Download (Recommended)

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

#### Option 2: Homebrew

```bash
# Install via Homebrew
brew install ollama

# Start Ollama service
brew services start ollama
```

#### Option 3: Manual Installation

1. Download from: <https://ollama.com/download/mac>
2. Install the .dmg file
3. Run Ollama from Applications

### Starting Ollama Service

#### Background Service (Recommended)

```bash
# Start Ollama service in background
ollama serve

# Or start as system service (macOS)
brew services start ollama
```

#### Check Service Status

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Expected response: {"version":"0.1.x"}
```

## Recommended Models by Hardware

### High-End Models (for systems with 64GB+ RAM)

```bash
# Llama 3.1 70B - Excellent reasoning and analysis
ollama pull llama3.1:70b

# Llama 3.1 405B - Largest, best quality (requires significant RAM)
ollama pull llama3.1:405b

# DeepSeek R1 70B - Ultimate reasoning model
ollama pull deepseek-r1:70b

# CodeLlama 34B - Best code quality
ollama pull codellama:34b
```

### Premium Models (for systems with 32GB+ RAM)

```bash
# Qwen2.5 32B - Premium multilingual intelligence
ollama pull qwen2.5:32b-instruct-q4_K_M

# CodeLlama 13B - High-quality code generation
ollama pull codellama:13b-code

# Llama 3.2 90B - Large, high quality
ollama pull llama3.2:90b
```

### Balanced Models (for systems with 16GB+ RAM)

```bash
# Gemma 7B - Google's balanced model
ollama pull gemma:7b

# Magicoder 7B - Optimal code generation balance
ollama pull magicoder:7b

# Qwen3 8B - Multilingual reasoning
ollama pull qwen3:8b

# Llama 3.1 8B - General purpose
ollama pull llama3.1:8b

# Qwen2.5 7B Instruct - Instruction-tuned variant
ollama pull qwen2.5:7b-instruct

# Mistral 7B - Balanced performance
ollama pull mistral:7b
```

### Lightweight Models (for systems with 8GB+ RAM)

```bash
# Llama 3.2 3B - Fast conversations
ollama pull llama3.2:3b

# DeepSeek Coder 1.3B - Quick code snippets
ollama pull deepseek-coder:1.3b

# Phi-3 3.8B - Microsoft's efficient model
ollama pull phi3:3.8b
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

### Monitor Running Models

```bash
# Show currently loaded models
ollama ps

# Show installed models
ollama list
```

## Configuration with Lattice Lock

### Model Selection Rules

Model selection rules are defined in `MODELS.md` in the project root. The Orchestrator uses this file to determine which models to use for specific tasks.

#### Structure of MODELS.md

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

### Local Model Configuration

Lattice Lock automatically detects and uses local Ollama models when they match the model names in your configuration. The framework will attempt to connect to the local Ollama instance at `http://localhost:11434` when a local model is selected.

## Testing Local Models

### Basic Test with Ollama CLI

```bash
# Test Llama 3.1 70B
ollama run llama3.1:70b "Explain quantum computing in simple terms"

# Test Gemma 7B
ollama run gemma:7b "Write a Python function to sort a list"

# Test with code generation
ollama run codellama:13b "Write a Python function to calculate fibonacci numbers"
```

### Test with Lattice Lock Orchestrator

```bash
# Test local model integration
lattice-lock orchestrator analyze "Write a simple Python function"

# Test specific local model with cost optimization
lattice-lock orchestrator route "Hello, how are you?" --strategy cost_optimize
```

### Test API Connectivity

```bash
# Test Ollama API directly
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:70b",
    "prompt": "Hello world",
    "stream": false
  }'
```

## Quick Setup Script

For quick setup of recommended models:

```bash
# Install Ollama (macOS)
curl -fsSL https://ollama.com/install.sh | sh
# Or: brew install ollama

# Start Ollama service
brew services start ollama

# Install recommended models based on your system RAM
# For 16GB+ RAM systems:
ollama pull llama3.2:8b      # Balanced performance
ollama pull llama3.2:3b      # Fast, lightweight
ollama pull gemma:7b         # Google's balanced model
ollama pull qwen2.5:7b-instruct  # Instruction-tuned
ollama pull codellama:13b-code   # Code generation

# For 32GB+ RAM systems, additionally install:
ollama pull qwen2.5:32b-instruct-q4_K_M  # High-quality multilingual
ollama pull llama3.1:70b     # High quality reasoning

# Verify installation
ollama list
```

## Troubleshooting

### Model Not Found

**Issue**: Lattice Lock reports that a local model is not found.

**Solution**: Ensure the model name in `MODELS.md` matches exactly with `ollama list` output.

```bash
# Check installed models
ollama list

# Verify exact model name and version
```

### Performance Issues

**Issue**: Local models are slow or using excessive memory.

**Solution**: 
- Local inference depends heavily on available RAM/VRAM
- Use smaller quantized models (e.g., `7b` or `8b`) on consumer hardware
- Ensure no other memory-intensive applications are running
- Consider using quantized variants (e.g., `q4_K_M`)

### Connection Refused

**Issue**: Cannot connect to Ollama service.

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# If not running, start it
brew services start ollama
# Or manually: ollama serve
```

### Model Loading Issues

**Issue**: Model fails to load or crashes.

**Solution**:
- Check available RAM: `vm_stat` (macOS) or `free -h` (Linux)
- Use a smaller model variant
- Restart Ollama service: `brew services restart ollama`

## Best Practices

1. **Start with smaller models**: Test with 7B or 8B models before deploying larger ones
2. **Monitor resource usage**: Use `ollama ps` to see which models are loaded
3. **Keep models updated**: Regularly run `ollama pull <model>` to get latest versions
4. **Configure fallback chains**: Always define fallback sequences in `MODELS.md`
5. **Test before production**: Verify model performance with your specific use cases
6. **Document blocked models**: Maintain clear records of why models are blocked

## Integration with CI/CD

Local models can be used in CI/CD pipelines for:
- Code review automation
- Documentation generation
- Test case generation
- Static analysis enhancement

Ensure your CI/CD environment has sufficient resources and Ollama installed before enabling local model features.

## See Also

- [Model Orchestration Guide](../concepts/model_orchestration.md)
- [Configuration Reference](../reference/configuration.md)
- [Provider Strategy Guide](../advanced/provider_strategy.md)
