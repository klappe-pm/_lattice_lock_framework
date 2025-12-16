# Model Orchestrator

A unified interface for intelligent model routing across multiple AI providers with cost optimization, fallback chains, and multi-model interaction patterns.

## Key Features

- **Intelligent Model Selection**: Automatically selects the best model based on task requirements, cost, and performance
- **Cost Optimization**: Real-time cost tracking and optimization across all providers
- **Multi-Model Patterns**: Chain, parallel consensus, hierarchical refinement, and adaptive analysis
- **Local Model Support**: 14 free local models via Ollama for privacy and zero cost
- **Fallback Chains**: Automatic retry with alternative models when primary is unavailable
- **Consensus Mode**: Multiple models for critical decisions
- **Performance Learning**: Continuous improvement based on actual results
- **Multi-Provider**: Unified interface across 9 providers
- **Rule-Based Guidance**: MODELS.md integration for custom routing rules
- **High Performance**: Sub-10ms model selection with comprehensive capability matching
- **Enterprise Ready**: Supports Azure, AWS Bedrock, and enterprise API endpoints

---

## Architecture

### API Integration Layer

| Component | Description |
|-----------|-------------|
| API Clients Factory | Unified interface for all providers |
| Provider Clients | Specialized clients for each API provider |
| Zen MCP Bridge | Integration with Model Context Protocol |

### Core Orchestrator

| Component | Description |
|-----------|-------------|
| ModelOrchestrator | Main routing engine that coordinates all operations |
| ModelGuideParser | Parses MODELS.md for task-to-model mappings and rules |
| Configuration | YAML-based configuration for system behavior |

### Cost Optimization

| Component | Description |
|-----------|-------------|
| Cost Tracker | Real-time tracking per model and task |
| Budget Manager | Enforces spending limits |
| Tier Selection | Balances quality vs cost based on task criticality |

### Local Model Management

| Component | Description |
|-----------|-------------|
| LocalModelManager | Manages Ollama local models |
| Keep Models Loaded | Ensures models stay in memory for performance |
| RAM Monitor | Tracks memory usage and prevents overload |
| Warmup Scripts | Pre-loads models for instant availability |

### Model Registry

**ModelCapabilities** — Comprehensive profiles for each model including:
- Performance metrics (speed, accuracy, reasoning depth)
- Cost per million tokens
- Task affinity scores
- Feature support (vision, function calling, streaming)

**ModelProvider Enum** — 9 supported providers:
- Anthropic
- OpenAI
- Google
- XAI
- Local (Ollama)
- DIAL
- Zen MCP
- Azure
- Bedrock

**Performance History** — Tracks actual performance for continuous improvement

### Selection Engine

| Component | Description |
|-----------|-------------|
| Model Selection Algorithm | Multi-factor scoring system (task affinity, quality, cost, availability, history) |
| Fallback Chain Handler | Automatic failover when primary model unavailable |
| Consensus Mode | Multiple models for critical tasks |
| Parallel Execution Engine | Concurrent model queries for speed |

### Quality & Monitoring

| Component | Description |
|-----------|-------------|
| Quality Gates | Validation checkpoints for output quality |
| Performance Metrics | Latency, accuracy, cost tracking |
| Structured Logging | Comprehensive audit trail |
| Benchmarks | Performance validation suite |

### Task Analysis

| Component | Description |
|-----------|-------------|
| TaskType Enum | 14 task categories |
| TaskRequirements | Specifications for context window, capabilities, constraints |
| Task Affinity Scoring | Matches tasks to models based on capability scores |

### User Interface Layer

| Component | Description |
|-----------|-------------|
| CLI Interface | Command-line interface for direct orchestrator interaction |
| API Endpoints | REST API for programmatic access |

---

## Intelligent Model Selection

The system scores models using a weighted multi-factor algorithm:

| Factor | Weight | Description |
|--------|--------|-------------|
| Task Affinity | 40% | How well suited for the task type |
| Performance | 30% | Speed vs reasoning depth tradeoff |
| Accuracy | 20% | Model accuracy rating |
| Cost Efficiency | 10% | Price/performance ratio |

### Supported Task Types

| Task Type | Description |
|-----------|-------------|
| `CODE_GENERATION` | Writing code |
| `CODE_REVIEW` | Reviewing/analyzing code |
| `DEBUGGING` | Finding and fixing bugs |
| `SYSTEM_DESIGN` | Architecture planning |
| `REASONING` | Complex reasoning tasks |
| `ANALYSIS` | Data/system analysis |
| `VISION` | Image analysis |
| `CREATIVE_WRITING` | Stories, poems |
| `TRANSLATION` | Language translation |
| `SUMMARIZATION` | Text summarization |

---

## Multi-Model Interaction Patterns

### Chain of Thought

Sequential processing through multiple models:

```python
chain = orchestrator.create_model_chain(tasks)
```

### Parallel Consensus

Multiple models vote on the answer:

```python
consensus = orchestrator.create_consensus_group(prompt, num_models=3)
```

### Hierarchical Refinement

Start cheap, refine with better models:

```python
result = await hierarchical_refinement(prompt, refinements)
```

### Adaptive Analysis

Depth adjusts to complexity:

```python
result = await adaptive_analysis(prompt, depth="auto")
```

---

## Testing Framework

| Test Type | Purpose |
|-----------|---------|
| Unit Tests | Core functionality verification |
| Integration Tests | API client validation |
| Concurrent Tests | Parallel execution validation |
| Real World Tests | End-to-end scenario validation |
