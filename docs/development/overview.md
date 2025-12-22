# Overview

## Overview

This repository contains a Model Orchestration Agent System that intelligently routes tasks across all available AI models with cost optimization and capability matching. The system now supports 63 different models across 8 major providers:

- **Local Models (20 models)**: Complete Ollama integration with Llama, CodeLlama, DeepSeek, Qwen, Magicoder, and Gemma variants
- **OpenAI (11 models)**: Complete GPT-4 family (GPT-4, GPT-4 Turbo, GPT-4o, GPT-4o Mini), GPT-3.5 family, and O1 family (O1, O1 Mini, O1 Pro)
- **Amazon Bedrock (8 models)**: Bedrock Claude, Llama, and Titan models via AWS managed service
- **Anthropic (7 models)**: Claude 4 Family (Opus 4.1, Opus 4, Sonnet 4.5, Sonnet 4) and Claude 3 Family (Opus 3, Sonnet 3.5, Haiku 3)
- **Google Gemini (6 models)**: Gemini 2.0 (Pro, Flash), Gemini 1.5 (Pro, Flash)
- **xAI Grok (5 models)**: Grok models including 2M context variants and vision capabilities
- **Microsoft Azure (4 models)**: Azure OpenAI Service models and Azure Claude partnership
- **DIAL Gateway (2 models)**: Enterprise API gateway for model access

The system operates as both a Python library and CLI tool, providing intelligent model selection based on task requirements, cost constraints, and performance characteristics.
