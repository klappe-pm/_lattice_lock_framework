# Local Models Setup Guide

## Overview

This guide covers setting up and using **21 local AI models** with the Power Prompts orchestration system. Local models provide:

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
1. Download from: https://ollama.com/download/mac
2. Install the .dmg file
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

### Currently Recommended Models

#### High-End Models (for systems with 64GB+ RAM)
```bash
# Llama 3.1 70B (new!) - Excellent reasoning and analysis
ollama pull llama3.1:70b

# DeepSeek R1 70B - Ultimate reasoning model
ollama pull deepseek-r1:70b

# CodeLlama 34B - Best code quality
ollama pull codellama:34b
```

#### Premium Models (for systems with 32GB+ RAM)
```bash
# Qwen2.5 32B - Premium multilingual intelligence
ollama pull qwen2.5:32b-instruct-q4_K_M

# CodeLlama 13B - High-quality code generation
ollama pull codellama:13b-code
```

#### Balanced Models (for systems with 16GB+ RAM)
```bash
# Gemma 7B (new!) - Google's balanced model
ollama pull gemma:7b

# Magicoder 7B - Optimal code generation balance
ollama pull magicoder:7b

# Qwen3 8B - Multilingual reasoning
ollama pull qwen3:8b

# Llama 3.1 8B - General purpose
ollama pull llama3.1:8b

# Qwen2.5 7B Instruct (new!) - Instruction-tuned variant
ollama pull qwen2.5:7b-instruct
```

#### Lightweight Models (for systems with 8GB+ RAM)
```bash
# Llama 3.2 3B - Fast conversations
ollama pull llama3.2:3b

# DeepSeek Coder 1.3B - Quick code snippets
ollama pull deepseek-coder:1.3b
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
# Test Llama 3.1 70B (new large model)
ollama run llama3.1:70b "Explain quantum computing in simple terms"

# Test Gemma 7B (new Google model)
ollama run gemma:7b "Write a Python function to sort a list"

# Test with code generation
ollama run codellama:13b "Write a Python function to calculate fibonacci numbers"
```

### Test with Power Prompts Orchestrator
```bash
# Test local model integration
./orchestrator-cli.py analyze "Write a simple Python function"

# Test specific local model (will prefer cost-optimize strategy)
./orchestrator-cli.py route "Hello, how are you?" --strategy cost_optimize
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

## Integration with Model Orchestrator

### Local Model Configuration

The orchestrator is pre-configured with **21 local models** across different providers:

#### Meta Llama Models (9 models)
**Note**: llama3.1:70b is now installed - a powerful 70B parameter model
- `llama-3.2-90b` → `llama3.2:90b` (Vision capable)
- `llama-3.2-11b` → `llama3.2:11b` (Vision capable) 
- `llama-3.2-3b` → `llama3.2:3b` (Lightweight)
- `llama-3.1-405b` → `llama3.1:405b` (Largest model)
- `llama-3.1-70b` → `llama3.1:70b` (**NEW - High quality, 70B parameters**)
- `llama-3.1-8b` → `llama3.1:8b` (Balanced)
- `llama-3-70b` → `llama3:70b` (Previous gen high quality)
- `llama-3-8b` → `llama3:8b` (Previous gen balanced)
- `llama3.2` → `llama3.2` (Alias)

#### Code-Specialized Models (3 models)
- `codellama:34b` → **Best overall code quality**
- `codellama:13b` → **Balanced code performance**
- `magicoder:7b` → **Optimal code generation balance**

#### Qwen Models (3 models)
- `qwen2.5:32b-instruct` → High-quality multilingual model
- `qwen3:8b` → Multilingual reasoning capabilities
- `qwen2.5:7b-instruct` → **NEW - Instruction-tuned variant, balanced performance**

#### DeepSeek Models (2 models)
- `deepseek-r1:70b` → **Ultimate reasoning model**
- `deepseek-coder:1.3b` → Ultra-fast code generation

#### Additional Models (3 models)
- `llama3.1:8b` → General purpose model
- `llama3.2:3b` → Lightweight conversation model
- `gemma:7b` → **NEW - Google's balanced model with strong capabilities**

### ✅ Currently Installed Models (14 models)
Based on your current setup (verified 2025-10-05):

| Model | Size | Status | Purpose | NEW |
|-------|------|--------|---------|-----|
| **llama3.1:70b** | 42GB | ✅ Installed | **High-end reasoning & analysis** | 🆕 |
| deepseek-r1:70b | 42GB | ✅ Installed | Ultimate reasoning | |
| codellama:34b | 19GB | ✅ Installed | Best code quality | |
| qwen2.5:32b | 19GB | ✅ Installed | Premium intelligence | |
| codellama:13b | 7.4GB | ✅ Installed | High-quality code | |
| codellama:13b-code | 7.4GB | ✅ Installed | Code generation focus | |
| qwen3:8b | 5.2GB | ✅ Installed | Multilingual reasoning | |
| **gemma:7b** | 5.0GB | ✅ Installed | **Google's balanced model** | 🆕 |
| llama3.1:8b | 4.9GB | ✅ Installed | General tasks | |
| llama3:8b | 4.7GB | ✅ Installed | General conversations | |
| **qwen2.5:7b-instruct** | 4.7GB | ✅ Installed | **Instruction-tuned Qwen** | 🆕 |
| magicoder:7b | 3.8GB | ✅ Installed | Optimal code balance | |
| llama3.2:3b | 2.0GB | ✅ Installed | Fast conversations | |
| deepseek-coder:1.3b | 776MB | ✅ Installed | Quick code snippets | |

### Custom Local Model Server

If using a different server or port:

```bash
# Set custom local server URL
export CUSTOM_API_URL="http://localhost:8080/v1"

# Or configure in the orchestrator
./orchestrator-cli.py --help
```

## Performance Optimization

### Memory Requirements by Model
- **Small models (1.3B-8B)**: 2-8GB RAM
- **Medium models (13B-32B)**: 12-25GB RAM  
- **Large models (34B-70B)**: 30-50GB RAM

**New Model Requirements:**
- **llama3.1:70b**: Requires 42GB+ RAM (similar to deepseek-r1:70b)
- **gemma:7b**: Requires 5-8GB RAM
- **qwen2.5:7b-instruct**: Requires 5-8GB RAM

### Speed Optimization
```bash
# Warm up frequently used models
ollama run llama3.1:70b "warm up"
ollama run gemma:7b "warm up"
ollama run magicoder:7b "warm up"
```

### Storage Management
- **Total Installed**: ~135GB for all 14 models
- **Available Models**: 21 models total
- **Recommended**: Keep 3-5 models active based on your use cases

## Usage Recommendations

### For Different Use Cases

#### **Code Development** 🔥
1. **Premium**: codellama:34b (best quality)
2. **Balanced**: magicoder:7b (optimal balance)
3. **Fast**: deepseek-coder:1.3b (quick iterations)

#### **Reasoning & Analysis** 🧠  
1. **Ultimate**: deepseek-r1:70b (best reasoning)
2. **High-End**: **llama3.1:70b** (new - excellent for complex analysis)
3. **Balanced**: qwen2.5:32b (multilingual reasoning)

#### **General Tasks** ⚡
1. **Balanced**: **gemma:7b** (new - Google's solid all-rounder)
2. **Multilingual**: **qwen2.5:7b-instruct** (new - instruction-tuned)
3. **Fast**: llama3.2:3b (lightweight conversations)

#### **Specialized Tasks**
- **Vision**: llama-3.2-90b (when available)
- **Multilingual**: qwen3:8b, qwen2.5:7b-instruct
- **Enterprise Code**: codellama:13b-code

## Troubleshooting

### Model Not Responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Restart if needed
brew services restart ollama
```

### Out of Memory Errors
1. **Check current usage**: `ollama ps`
2. **Switch to smaller model**: Use 3B-8B models instead of 30B+
3. **Restart Ollama**: Clears model cache
4. **Monitor RAM**: `vm_stat | head -4`

### New Model Issues
```bash
# If new models aren't working, try re-pulling
ollama pull llama3.1:70b
ollama pull gemma:7b
ollama pull qwen2.5:7b-instruct

# Check model status
ollama list | grep -E "(llama3.1:70b|gemma:7b|qwen2.5:7b)"
```

### Slow Performance
1. **Use warmup script**: `./warmup-models.sh`
2. **Prefer smaller models**: 7B-13B range for speed
3. **Close other applications**: Free up RAM for models
4. **Consider model priority**: Use lighter models for development, heavier for production

## Cost Optimization Strategy

### Zero-Cost Advantages
- **Total Cost**: $0.00 for all local models
- **No Rate Limits**: Process unlimited requests
- **No Internet Required**: Work offline
- **Full Privacy**: Data never leaves your machine

### Recommended Workflow
1. **Start Local**: Always try local models first
2. **Scale Up**: Use cloud models only when local isn't sufficient
3. **Hybrid Approach**: Use local for development, cloud for production validation
4. **Cost Monitoring**: Track when you switch to paid APIs

## Next Steps

### Immediate Actions
1. ✅ **14 local models installed** - Ready to use
2. 🔧 **Test the new models**: llama3.1:70b, gemma:7b, qwen2.5:7b-instruct  
3. 📚 **Try the orchestrator**: Use `cost_optimize` strategy to prefer local models

### Expansion Options
1. **More local models**: Install remaining 7 models from the 21 available
2. **Cloud integration**: Set up API keys for specialized tasks
3. **Custom workflows**: Create scripts for your most common tasks

### Pro Tips
- **Local-first strategy**: Use local models for 90% of tasks
- **New model advantages**: llama3.1:70b offers excellent reasoning, gemma:7b provides balanced performance
- **Resource management**: Monitor RAM usage with multiple large models
- **Backup strategy**: Keep smaller models for when large models are busy

---

## 🏆 Your Updated Local AI Environment

**Current Setup**:
- **Installed Models**: 14 out of 21 available
- **New Models**: llama3.1:70b, gemma:7b, qwen2.5:7b-instruct
- **Storage Used**: ~135GB
- **RAM Requirements**: Supports models up to 70B parameters
- **Cost**: $0.00 for unlimited local processing

🎉 **You now have an enhanced professional-grade local AI development environment with 3 powerful new models!**