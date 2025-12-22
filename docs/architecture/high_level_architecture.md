# High-Level Architecture

## High-Level Architecture

### Core Components

- **[[Model Orchestrator]]** (`model-orchestrator.py`, `model_orchestrator_v2.py`): Main orchestration engine with task analysis, model capability scoring, cost tracking, and performance history
- **[[Zen MCP Bridge]]** (`zen_mcp_bridge.py`): Extends Zen MCP tools with multi-model capabilities and intelligent routing
- **[[API Clients]]** (`api_clients.py`, `grok_api.py`): Unified interface to all AI model providers
- **[[CLI Interface]]** (`orchestrator-cli.py`): Command-line interface for model operations and testing
- **[[Testing Suite]]** (`test_integration.py`, `test_real_world.py`): Comprehensive testing framework

### Key Features

- **[[Intelligent Model Selection]]**: Scores models based on task affinity (40%), performance (30%), accuracy (20%), and cost efficiency (10%)
- **[[Multi-Model Interaction Patterns]]**: Chain of thought, parallel consensus, hierarchical refinement, adaptive analysis
- **[[Cost Optimization]]**: Real-time cost tracking and optimization across providers
- **[[Comprehensive Provider Support]]**: 63 total models across 8 providers - Local/Ollama (20 models), OpenAI (11 models), Bedrock (8 models), Anthropic (7 models), Google Gemini (6 models), xAI Grok (5 models), Azure (4 models), DIAL (2 models)
