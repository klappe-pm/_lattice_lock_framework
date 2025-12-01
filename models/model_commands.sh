#!/bin/bash
# AI Model Commands - Complete Reference
# Comprehensive command guide for all 63 AI models in Lattice Lock Framework
# Usage: Copy and paste these commands to use any model

# =============================================================================
# SETUP & CREDENTIALS
# =============================================================================

# Load all API keys from Keychain (recommended)
eval "$(load-keychain-credentials)"

# OR load from project .env file
source ~/Documents/Lattice\ Lock\ Framework/credentials/.env

# OR source shell profile
source ~/.bash_profile

# Verify keys are loaded
echo "OpenAI: $(echo $OPENAI_API_KEY | cut -c1-15)..."
echo "Anthropic: $(echo $ANTHROPIC_API_KEY | cut -c1-15)..."
echo "Google: $(echo $GOOGLE_API_KEY | cut -c1-15)..."
echo "xAI Grok: $(echo $XAI_API_KEY | cut -c1-15)..."

# =============================================================================
# GROK MODELS (xAI) - 5 Models
# =============================================================================

# Navigate to project
cd ~/Documents/Lattice\ Lock\ Framework

# List all Grok models
venv/bin/python src/lattice_lock_orchestrator/grok_api.py list

# grok-4-fast-reasoning (2M context, advanced reasoning)
venv/bin/python src/lattice_lock_orchestrator/grok_api.py chat \
  --model grok-4-fast-reasoning \
  --prompt "Design a distributed microservices architecture"

# grok-code-fast-1 (256K context, code specialized)
venv/bin/python src/lattice_lock_orchestrator/grok_api.py chat \
  --model grok-code-fast-1 \
  --prompt "Write a binary search tree implementation in Python"

# grok-3 (131K context, general purpose)
venv/bin/python src/lattice_lock_orchestrator/grok_api.py chat \
  --model grok-3 \
  --prompt "Explain quantum computing concepts"

# grok-3-fast (131K context, faster inference)
venv/bin/python src/lattice_lock_orchestrator/grok_api.py chat \
  --model grok-3-fast \
  --prompt "Summarize this document: [paste text]"

# grok-2-vision-1212 (32K context, vision analysis)
venv/bin/python src/lattice_lock_orchestrator/grok_api.py vision \
  --model grok-2-vision-1212 \
  --prompt "Analyze this image" \
  --image /path/to/image.jpg

# =============================================================================
# OPENAI MODELS - 11 Models
# =============================================================================

# gpt-4o (128K context, vision, function calling)
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Your prompt here"}],
    "temperature": 0.7
  }'

# gpt-4o-mini (128K context, cost-effective)
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Your prompt here"}],
    "temperature": 0.7
  }'

# gpt-4-turbo (128K context)
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-turbo-2024-04-09",
    "messages": [{"role": "user", "content": "Your prompt here"}]
  }'

# o1-pro (128K context, advanced reasoning)
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "o1-pro",
    "messages": [{"role": "user", "content": "Complex reasoning task"}]
  }'

# o1-preview (128K context, reasoning preview)
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "o1-preview",
    "messages": [{"role": "user", "content": "Reasoning task"}]
  }'

# o1-mini (128K context, fast reasoning)
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "o1-mini",
    "messages": [{"role": "user", "content": "Quick reasoning task"}]
  }'

# o3-mini (200K context)
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "o3-mini",
    "messages": [{"role": "user", "content": "Your prompt"}]
  }'

# =============================================================================
# ANTHROPIC CLAUDE MODELS - 7 Models
# =============================================================================

# claude-opus-4.1 (200K context, best quality)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4.1",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Your prompt here"}]
  }'

# claude-sonnet-4.5 (200K context, balanced)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4.5",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Your prompt here"}]
  }'

# claude-3.5-sonnet (200K context)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Your prompt here"}]
  }'

# claude-3-opus (200K context)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20240229",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Your prompt here"}]
  }'

# claude-3-sonnet (200K context)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Your prompt here"}]
  }'

# claude-3-haiku (200K context, fastest)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-haiku-20240307",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Your prompt here"}]
  }'

# =============================================================================
# GOOGLE GEMINI MODELS - 6 Models
# =============================================================================

# gemini-2.0-flash-exp (1M context, latest)
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Your prompt here"}]}]
  }'

# gemini-1.5-pro (2M context)
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Your prompt here"}]}]
  }'

# gemini-1.5-flash (1M context, fast)
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Your prompt here"}]}]
  }'

# gemini-1.5-flash-8b (1M context, smaller)
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Your prompt here"}]}]
  }'

# =============================================================================
# LOCAL OLLAMA MODELS - 20 Models (FREE)
# =============================================================================

# Ensure Ollama is running
ollama serve &

# llama-3.2-90b (128K context, vision, function calling)
ollama run llama-3.2-90b "Your prompt here"

# llama-3.1-405b (128K context, largest)
ollama run llama-3.1-405b "Complex reasoning task"

# llama-3.1-70b (128K context)
ollama run llama-3.1-70b "Your prompt here"

# llama-3.1-8b (128K context, fast)
ollama run llama-3.1-8b "Quick task"

# llama3.1:8b (alias)
ollama run llama3.1:8b "Your prompt here"

# codellama:34b (16K context, code specialized)
ollama run codellama:34b "Write a sorting algorithm"

# codellama:13b (16K context, code specialized)
ollama run codellama:13b "Debug this code: [paste code]"

# magicoder:7b (16K context, code specialized)
ollama run magicoder:7b "Generate unit tests for this function"

# qwen2.5:32b-instruct (32K context, multilingual)
ollama run qwen2.5:32b-instruct "Translate this to Chinese: Hello"

# qwen2.5:7b-instruct (32K context, multilingual)
ollama run qwen2.5:7b-instruct "Your prompt here"

# qwen3:8b (32K context, multilingual)
ollama run qwen3:8b "Analyze this text"

# deepseek-r1:70b (32K context, advanced reasoning)
ollama run deepseek-r1:70b "Complex problem solving"

# deepseek-coder:1.3b (16K context, code)
ollama run deepseek-coder:1.3b "Quick code snippet"

# gemma:7b (8K context, balanced)
ollama run gemma:7b "Your prompt here"

# llama-3.2-11b (128K context, vision)
ollama run llama-3.2-11b "Analyze this image and text"

# llama-3.2-3b (128K context, small)
ollama run llama-3.2-3b "Simple task"

# llama3.2:3b (alias)
ollama run llama3.2:3b "Quick question"

# llama-3-70b (8K context)
ollama run llama-3-70b "Your prompt"

# llama-3-8b (8K context)
ollama run llama-3-8b "Simple query"

# llama3.2 (alias, 128K context)
ollama run llama3.2 "General task"

# =============================================================================
# AZURE OPENAI MODELS - 4 Models
# =============================================================================

# Note: Replace {deployment-name} and {endpoint} with your Azure deployment details

# azure-gpt-4o
curl https://{your-resource}.openai.azure.com/openai/deployments/{deployment-name}/chat/completions?api-version=2024-02-15-preview \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Your prompt"}]
  }'

# azure-gpt-4-turbo
curl https://{your-resource}.openai.azure.com/openai/deployments/{deployment-name}/chat/completions?api-version=2024-02-15-preview \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Your prompt"}]
  }'

# =============================================================================
# AWS BEDROCK MODELS - 8 Models
# =============================================================================

# Note: Requires AWS CLI configured with credentials

# bedrock-claude-opus-3.5
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-5-opus-20250220-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","messages":[{"role":"user","content":"Your prompt"}],"max_tokens":4096}' \
  --region us-east-1 \
  output.json

# bedrock-claude-sonnet-3.5
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-5-sonnet-20240229-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","messages":[{"role":"user","content":"Your prompt"}],"max_tokens":4096}' \
  --region us-east-1 \
  output.json

# bedrock-claude-sonnet-3
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-sonnet-20240229-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","messages":[{"role":"user","content":"Your prompt"}],"max_tokens":4096}' \
  --region us-east-1 \
  output.json

# bedrock-llama-3.1-405b
aws bedrock-runtime invoke-model \
  --model-id meta.llama3-1-405b-instruct-v1:0 \
  --body '{"prompt":"Your prompt","max_gen_len":4096}' \
  --region us-east-1 \
  output.json

# bedrock-llama-3.1-70b
aws bedrock-runtime invoke-model \
  --model-id meta.llama3-1-70b-instruct-v1:0 \
  --body '{"prompt":"Your prompt","max_gen_len":4096}' \
  --region us-east-1 \
  output.json

# bedrock-titan-text-express
aws bedrock-runtime invoke-model \
  --model-id amazon.titan-text-express-v1 \
  --body '{"inputText":"Your prompt","textGenerationConfig":{"maxTokenCount":4096}}' \
  --region us-east-1 \
  output.json

# =============================================================================
# COMMON USE CASES BY TASK
# =============================================================================

# CODE GENERATION - Best Models
# 1. codellama:34b (free, local)
ollama run codellama:34b "Implement a REST API in Python using FastAPI"

# 2. grok-code-fast-1
venv/bin/python src/lattice_lock_orchestrator/grok_api.py chat \
  --model grok-code-fast-1 \
  --prompt "Create a React component for user authentication"

# 3. claude-sonnet-4.5
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4.5",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Write a database migration script"}]
  }'

# ADVANCED REASONING - Best Models
# 1. deepseek-r1:70b (free, local)
ollama run deepseek-r1:70b "Design a fault-tolerant distributed system"

# 2. grok-4-fast-reasoning (2M context)
venv/bin/python src/lattice_lock_orchestrator/grok_api.py chat \
  --model grok-4-fast-reasoning \
  --prompt "Analyze the trade-offs between microservices and monoliths"

# 3. o1-pro
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "o1-pro",
    "messages": [{"role": "user", "content": "Solve this algorithmic problem"}]
  }'

# CREATIVE WRITING - Best Models
# 1. claude-opus-4.1
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4.1",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Write a short story about AI"}]
  }'

# 2. gpt-4o
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Create marketing copy for a product"}]
  }'

# VISION ANALYSIS - Best Models
# 1. grok-2-vision-1212
venv/bin/python src/lattice_lock_orchestrator/grok_api.py vision \
  --model grok-2-vision-1212 \
  --prompt "Analyze this diagram" \
  --image /path/to/image.jpg

# 2. gpt-4o (vision capable)
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "What is in this image?"},
        {"type": "image_url", "image_url": {"url": "https://..."}}
      ]
    }]
  }'

# LARGE CONTEXT TASKS - Best Models (200K+ tokens)
# 1. grok-4-fast-reasoning (2M tokens)
venv/bin/python src/lattice_lock_orchestrator/grok_api.py chat \
  --model grok-4-fast-reasoning \
  --prompt "Analyze this entire codebase: [paste large code]"

# 2. gemini-1.5-pro (2M tokens)
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Summarize these 50 documents..."}]}]
  }'

# 3. claude-opus-4.1 (200K tokens)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4.1",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Long context analysis"}]
  }'

# =============================================================================
# MODEL SELECTION GUIDE
# =============================================================================

# FREE (Local Ollama) - 20 models
# Best for: Privacy, offline use, no API costs
# Recommendation: llama-3.1-405b (best quality), deepseek-r1:70b (reasoning)

# LOW COST ($0.15-$1/M tokens)
# gpt-4o-mini, gemini-1.5-flash, grok-3
# Best for: High-volume tasks, prototyping

# BALANCED ($1-$5/M tokens)
# claude-sonnet-4.5, gpt-4o, grok-code-fast-1, gemini-1.5-pro
# Best for: Production applications, code generation

# PREMIUM ($15-$100/M tokens)
# claude-opus-4.1, o1-pro, grok-4-fast-reasoning
# Best for: Critical reasoning, complex analysis, highest quality

# =============================================================================
# QUICK REFERENCE
# =============================================================================

# List all available models
cd ~/Documents/Lattice\ Lock\ Framework
venv/bin/python src/lattice_lock_orchestrator/grok_api.py list

# Test any Grok model
source credentials/.env && \
venv/bin/python src/lattice_lock_orchestrator/grok_api.py chat \
  --model grok-3 \
  --prompt "Hello!"

# Test Ollama (local, free)
ollama run llama3.1:8b "Hello!"

# View this file
cat ~/Documents/Lattice\ Lock\ Framework/AI_MODEL_COMMANDS.sh

# =============================================================================
# MORE INFORMATION
# =============================================================================

# Model configurations: ~/Documents/Lattice Lock Framework/models/
# API keys setup: ~/Documents/Lattice Lock Framework/credentials/
# Grok documentation: ~/Documents/configurations/GROK_SETUP.md
# Full model database: ~/Documents/Lattice Lock Framework/models/model_configuration_database.md

# Total: 63 models across 8 providers
# Free: 20 local models via Ollama
# Cloud: 43 API-based models

---
# Last Updated: 2025-12-01
# Status: ✅ All 63 models documented
