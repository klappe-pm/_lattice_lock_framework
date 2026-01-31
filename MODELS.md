# Model Selection Guide

This file provides human-editable preferences for model routing in the Lattice Lock Orchestrator.
It is parsed by `lattice_lock.orchestrator.guide.ModelGuideParser`.

## Table of Contents

- [Overview](#overview)
- [How Routing Works](#how-routing-works)
- [Task Preferences](#task-preferences)
- [Cost Tiers](#cost-tiers)
- [Capability Matrix](#capability-matrix)
- [Blocked Models](#blocked-models)
- [Fallback Configuration](#fallback-configuration)
- [Provider Reference](#provider-reference)
- [Task Type Reference](#task-type-reference)
- [Example Workflows](#example-workflows)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)

---

## Overview

The Lattice Lock Orchestrator intelligently routes tasks to the most appropriate AI model based on:

- **Task type** (code generation, debugging, architecture, etc.)
- **Model capabilities** (reasoning score, coding score, context window)
- **Priority mode** (quality, speed, cost, balanced)
- **Feature requirements** (vision, function calling, JSON mode)

This guide defines the preferred models for each task type and fallback chains for resilience.

---

## How Routing Works

The orchestrator uses a multi-factor scoring system to select the optimal model for each task.

### Scoring Algorithm

Each model receives a fitness score (0.0 - 1.0) based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Base Score | 0.50 | Starting score for all eligible models |
| Primary Task Match | 0.30 | How well the model fits the detected task type |
| Secondary Task Match | 0.10 | Bonus for supporting secondary task types |
| Complexity Boost | 0.10 | Bonus for complex tasks (favors high-reasoning models) |

### Priority Modes

Users can specify a priority that adjusts the weighting:

| Priority | Focus | Best For |
|----------|-------|----------|
| `quality` | reasoning (0.3) + coding (0.2) | Complex analysis, architecture decisions |
| `speed` | speed_rating (0.5) | Quick iterations, prototyping |
| `cost` | inverse of blended_cost (0.5) | Budget-conscious workloads |
| `balanced` | All factors equally | General-purpose use (default) |

### Task Score Calculation

Each model has pre-calculated task scores derived from its `coding_score` and `reasoning_score`:

| Task Type | Formula |
|-----------|---------|
| CODE_GENERATION | `coding_score / 100` |
| DEBUGGING | `coding * 0.9 + reasoning * 0.1` |
| ARCHITECTURAL_DESIGN | `reasoning * 0.7 + coding * 0.3` |
| DOCUMENTATION | `(coding + reasoning) / 2` |
| TESTING | `coding * 0.8 + reasoning * 0.2` |
| DATA_ANALYSIS | `reasoning * 0.6 + coding * 0.4` |
| GENERAL | `(coding + reasoning) / 2` |
| REASONING | `reasoning_score / 100` |
| VISION | `1.0 if supports_vision else 0.0` |
| SECURITY_AUDIT | `coding * 0.7 + reasoning * 0.3` |
| CREATIVE_WRITING | `reasoning * 0.8` |
| TRANSLATION | `reasoning * 0.9` |

### Disqualification Rules

A model is immediately disqualified (score = 0) if:

- `context_window < min_context_required`
- `require_vision = true` but `supports_vision = false`
- `require_functions = true` but `supports_function_calling = false`

---

## Task Preferences

### Parsing Notes

The parser expects specific section formats:

- `### Code Tasks` section with lines formatted as: `- **task_key**: model_a > model_b > model_c`
- Model IDs must match the registry IDs exactly (see `src/lattice_lock/orchestrator/models.yaml`)

### Code Tasks

Models are ordered by preference: premium (highest quality) > standard > budget/local (free).

- **code_generation**: o1-pro > claude-4-5-opus > claude-4-5-sonnet > grok-code-fast-1 > qwen3-next-80b > codellama:34b > glm4
- **debugging**: o1-pro > claude-4-sonnet > grok-4-fast-reasoning > gemini-2.5-pro > qwen3-next-80b > deepseek-r1:70b > codellama:34b
- **architectural_design**: o1-pro > claude-4-5-opus > qwen3-next-80b > gemini-2.5-pro > grok-4-fast-reasoning
- **documentation**: claude-4-5-sonnet > gpt-4o > gemini-2.5-pro > gemini-2.5-flash > glm4 > qwen2.5:32b
- **testing**: o1-mini > claude-4-sonnet > gemini-2.5-flash > grok-code-fast-1 > glm4 > codellama:34b
- **data_analysis**: o1-pro > gemini-2.5-pro > gpt-4o > grok-4-fast-reasoning > qwen3-next-80b > qwen2.5:32b
- **general**: gpt-4o > claude-3-5-haiku > gemini-2.5-flash > glm4
- **reasoning**: o1-pro > claude-4-5-opus > grok-4-fast-reasoning > qwen3-next-80b > gemini-2.5-pro > deepseek-r1:70b
- **vision**: gpt-4o > claude-4-5-opus > gemini-2.5-pro > claude-4-5-sonnet
- **security_audit**: o1-pro > claude-4-5-sonnet > gpt-4o > grok-4-fast-reasoning > codellama:34b
- **creative_writing**: claude-4-5-opus > gpt-4o > gemini-2.5-pro > claude-3-5-haiku > grok-3
- **translation**: gemini-2.5-flash > qwen2.5:32b > gpt-4o-mini > grok-3

---

## Cost Tiers

Models are organized into cost tiers based on blended cost (per 1M tokens).

*Blended cost = (input_cost x 3 + output_cost) / 4, assuming 3:1 input:output ratio*

### Premium Tier ($15+ / 1M tokens)

Best for: Critical decisions, complex architecture, security audits

| Model | Blended Cost | Reasoning | Coding | Speed | Provider |
|-------|-------------|-----------|--------|-------|----------|
| o1-pro | $105.00 | 99 | 98 | 3 | OpenAI |
| claude-4-5-opus | $35.00 | 99.5 | 99 | 5 | Anthropic |

### Standard Tier ($3-15 / 1M tokens)

Best for: Daily development, code review, documentation

| Model | Blended Cost | Reasoning | Coding | Speed | Provider |
|-------|-------------|-----------|--------|-------|----------|
| claude-4-5-sonnet | $8.75 | 98 | 98 | 8 | Anthropic |
| gpt-4o | $7.50 | 90 | 85 | 8 | OpenAI |
| claude-4-sonnet | $7.00 | 96 | 96 | 8 | Anthropic |
| claude-3-7-sonnet | $6.75 | 95 | 95 | 7 | Anthropic |
| grok-4-fast-reasoning | $3.00 | 95 | 85 | 7 | xAI |
| o1-mini | $5.25 | 96 | 95 | 5 | OpenAI |

### Budget Tier ($0.15-3 / 1M tokens)

Best for: High-volume tasks, prototyping, translation

| Model | Blended Cost | Reasoning | Coding | Speed | Provider |
|-------|-------------|-----------|--------|-------|----------|
| grok-code-fast-1 | $2.25 | 85 | 90 | 8 | xAI |
| grok-3 | $1.50 | 80 | 75 | 6 | xAI |
| gemini-2.5-pro | $1.88 | 85 | 85 | 7 | Google |
| claude-3-5-haiku | $0.50 | 88 | 85 | 9 | Anthropic |
| gpt-4o-mini | $0.26 | 85 | 80 | 9 | OpenAI |
| gemini-2.5-flash | $0.13 | 80 | 80 | 9 | Google |

### Free Tier (Local Models)

Best for: Offline work, privacy-sensitive tasks, unlimited usage

| Model | Provider | Reasoning | Coding | Speed | Context |
|-------|----------|-----------|--------|-------|---------|
| qwen3-next-80b | Ollama | 95 | 95 | 4 | 128K |
| deepseek-r1:70b | Ollama | 95 | 90 | 5 | 64K |
| glm4 | Ollama | 85 | 90 | 8 | 128K |
| codellama:34b | Ollama | 85 | 95 | 5 | 16K |
| qwen2.5:32b | Ollama | 88 | 85 | 6 | 32K |

---

## Capability Matrix

| Model | Vision | Function Calling | JSON Mode | Max Context |
|-------|--------|------------------|-----------|-------------|
| **OpenAI** |||||
| o1-pro | - | - | - | 200K |
| o1-mini | - | - | - | 128K |
| gpt-4o | Yes | Yes | Yes | 128K |
| gpt-4o-mini | Yes | Yes | Yes | 128K |
| **Anthropic** |||||
| claude-4-5-opus | Yes | Yes | - | 500K |
| claude-4-5-sonnet | Yes | Yes | - | 500K |
| claude-4-sonnet | Yes | Yes | - | 300K |
| claude-3-7-sonnet | Yes | Yes | - | 250K |
| claude-3-5-haiku | - | Yes | - | 200K |
| **Google** |||||
| gemini-2.5-pro | Yes | Yes | - | 1M |
| gemini-2.5-flash | Yes | Yes | - | 1M |
| **xAI** |||||
| grok-4-fast-reasoning | - | Yes | - | 2M |
| grok-code-fast-1 | - | - | - | 256K |
| grok-3 | - | - | - | 128K |
| **Local (Ollama)** |||||
| qwen3-next-80b | - | Yes | Yes | 128K |
| deepseek-r1:70b | - | - | - | 64K |
| glm4 | - | Yes | Yes | 128K |
| codellama:34b | - | - | - | 16K |
| qwen2.5:32b | - | Yes | - | 32K |

**Legend:** Yes = Supported, - = Not supported

---

## Blocked Models

Models listed here will be excluded from automatic selection.

Note: Block list uses exact-match. To block a model family, list each variant.

### Blocked Models

- llama3.2:3b
- deepseek-coder:1.3b

---

## Fallback Configuration

### Fallback Chains

When a primary model fails, the orchestrator will attempt these models in order.
Chains should include models from different providers for resilience.

- code_generation: o1-pro -> claude-4-5-sonnet -> grok-code-fast-1 -> qwen3-next-80b -> codellama:34b -> glm4
- debugging: o1-pro -> claude-4-sonnet -> grok-4-fast-reasoning -> gemini-2.5-pro -> qwen3-next-80b -> deepseek-r1:70b
- architectural_design: o1-pro -> claude-4-5-opus -> qwen3-next-80b -> gemini-2.5-pro -> grok-4-fast-reasoning
- documentation: claude-4-5-sonnet -> gpt-4o -> gemini-2.5-flash -> claude-3-5-haiku -> glm4 -> qwen2.5:32b
- testing: o1-mini -> claude-4-sonnet -> gemini-2.5-flash -> grok-code-fast-1 -> glm4 -> codellama:34b
- data_analysis: o1-pro -> gemini-2.5-pro -> gpt-4o -> grok-4-fast-reasoning -> qwen3-next-80b
- general: gpt-4o -> claude-3-5-haiku -> gemini-2.5-flash -> glm4
- reasoning: o1-pro -> claude-4-5-opus -> grok-4-fast-reasoning -> qwen3-next-80b -> gemini-2.5-pro -> deepseek-r1:70b
- vision: gpt-4o -> claude-4-5-opus -> gemini-2.5-pro -> claude-4-5-sonnet
- security_audit: o1-pro -> claude-4-5-sonnet -> gpt-4o -> grok-4-fast-reasoning -> codellama:34b
- creative_writing: claude-4-5-opus -> gpt-4o -> gemini-2.5-pro -> claude-3-5-haiku
- translation: gemini-2.5-flash -> qwen2.5:32b -> gpt-4o-mini -> grok-3

---

## Provider Reference

| Provider | Models | Status | Required Environment |
|----------|--------|--------|---------------------|
| OpenAI | o1-pro, o1-mini, gpt-4o, gpt-4o-mini | Production | `OPENAI_API_KEY` |
| Anthropic | claude-4-5-opus, claude-4-5-sonnet, claude-4-sonnet, claude-3-7-sonnet, claude-3-5-haiku | Production | `ANTHROPIC_API_KEY` |
| Google | gemini-2.5-pro, gemini-2.5-flash | Beta | `GOOGLE_API_KEY` |
| xAI | grok-4-fast-reasoning, grok-code-fast-1, grok-3 | Beta | `XAI_API_KEY` |
| Azure | azure-gpt-4o, azure-gpt-4-turbo | Production | `AZURE_OPENAI_KEY`, `AZURE_ENDPOINT` |
| Bedrock | bedrock-claude-3-opus, bedrock-claude-3.5-sonnet | Production | AWS credentials (IAM or explicit) |
| Ollama | qwen3-next-80b, deepseek-r1:70b, glm4, codellama:34b, qwen2.5:32b | Local | `OLLAMA_HOST` (optional, default: localhost:11434) |
| vLLM | Custom deployments | Custom | Configured via `api_base` in model config |

### Provider Maturity Levels

| Level | Description | Default Behavior |
|-------|-------------|------------------|
| `production` | Stable, fully tested | Preferred in routing |
| `beta` | Functional, may have edge cases | Used if production unavailable |
| `experimental` | Gated, requires explicit enable | Skipped unless requested |

---

## Task Type Reference

| Task Type | Description | Key Capabilities | Weight Formula |
|-----------|-------------|------------------|----------------|
| code_generation | Writing new code | High coding score | coding |
| debugging | Finding and fixing bugs | Coding + reasoning | coding * 0.9 + reasoning * 0.1 |
| architectural_design | System design decisions | Strong reasoning | reasoning * 0.7 + coding * 0.3 |
| documentation | Writing docs and comments | Balanced skills | (coding + reasoning) / 2 |
| testing | Writing and analyzing tests | Coding focus | coding * 0.8 + reasoning * 0.2 |
| data_analysis | Analyzing data patterns | Reasoning + coding | reasoning * 0.6 + coding * 0.4 |
| general | General-purpose tasks | Balanced, fast | (coding + reasoning) / 2 |
| reasoning | Complex logical problems | High reasoning score | reasoning |
| vision | Image understanding | Vision capability required | 1.0 if vision else 0.0 |
| security_audit | Security analysis | Coding + reasoning | coding * 0.7 + reasoning * 0.3 |
| creative_writing | Creative content | High reasoning | reasoning * 0.8 |
| translation | Language translation | Multilingual support | reasoning * 0.9 |

---

## Example Workflows

### Code Generation Workflow

```
Task: "Implement a REST API for user authentication"

1. Orchestrator detects: CODE_GENERATION (primary), SECURITY_AUDIT (secondary)
2. Requirements: coding >= 0.8, context >= 8K
3. Selected: claude-4-5-sonnet (coding: 98, reasoning: 98, cost-effective)

Fallback chain if primary fails:
  claude-4-5-sonnet -> grok-code-fast-1 -> qwen3-next-80b -> codellama:34b
```

### Architecture Review Workflow

```
Task: "Review the microservices architecture for scalability issues"

1. Orchestrator detects: ARCHITECTURAL_DESIGN (primary), REASONING (secondary)
2. Requirements: reasoning >= 0.9, context >= 50K
3. Selected: o1-pro (reasoning: 99, best for complex analysis)

Fallback chain:
  o1-pro -> claude-4-5-opus -> qwen3-next-80b -> gemini-2.5-pro
```

### Budget-Conscious Documentation

```
Task: "Generate API documentation for all endpoints"

1. Orchestrator detects: DOCUMENTATION (primary)
2. Requirements: priority = "cost", context >= 100K
3. Selected: gemini-2.5-flash (cost: $0.13/1M, context: 1M)

Fallback chain:
  gemini-2.5-flash -> claude-3-5-haiku -> glm4 -> qwen2.5:32b
```

### Vision Task

```
Task: "Analyze this UI screenshot for accessibility issues"

1. Orchestrator detects: VISION (primary), SECURITY_AUDIT (secondary)
2. Requirements: supports_vision = true
3. Selected: gpt-4o (vision support, strong reasoning)

Fallback chain (vision-capable only):
  gpt-4o -> claude-4-5-opus -> gemini-2.5-pro
```

### Local-Only Workflow

```
Task: "Refactor this function for better performance" (offline mode)

1. Orchestrator detects: CODE_GENERATION (primary)
2. Requirements: provider = "ollama" (local only)
3. Selected: qwen3-next-80b (highest local coding score)

Fallback chain:
  qwen3-next-80b -> glm4 -> codellama:34b
```

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI models |
| `ANTHROPIC_API_KEY` | Anthropic API key | For Claude models |
| `GOOGLE_API_KEY` | Google AI API key | For Gemini models |
| `XAI_API_KEY` | xAI API key | For Grok models |
| `AZURE_OPENAI_KEY` | Azure OpenAI key | For Azure-hosted models |
| `AZURE_ENDPOINT` | Azure endpoint URL | For Azure-hosted models |
| `AWS_ACCESS_KEY_ID` | AWS access key | For Bedrock (or use IAM) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | For Bedrock (or use IAM) |
| `AWS_REGION` | AWS region | For Bedrock |
| `OLLAMA_HOST` | Ollama server URL | Optional (default: localhost:11434) |
| `LATTICE_MODELS_CONFIG_PATH` | Custom models.yaml path | Optional |
| `LATTICE_SCORER_CONFIG_PATH` | Custom scorer config path | Optional |
| `LATTICE_DEFAULT_MODEL` | Default model override | Optional |

### Custom Preferences

To override the default preferences:

1. Copy this file to your project root as `MODELS.md`
2. Modify the `### Code Tasks` section with your preferred model order
3. Update `### Fallback Chains` with your custom fallback sequences
4. Add any models to `### Blocked Models` that you want to exclude

The orchestrator will automatically detect and parse your custom `MODELS.md`.

### Local Model Setup

To use local models via Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull recommended models
ollama pull qwen3-next-80b
ollama pull glm4
ollama pull codellama:34b
ollama pull deepseek-r1:70b
ollama pull qwen2.5:32b

# Verify installation
ollama list
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Model not found" | Model ID mismatch | Check `models.yaml` for exact IDs |
| "Provider unavailable" | Missing API key | Set required environment variable |
| "Context too small" | Task exceeds model context | Use model with larger context window |
| "Vision not supported" | Vision task on non-vision model | Check capability matrix above |
| "Fallback exhausted" | All models in chain failed | Check provider credentials and connectivity |

### Debug Mode

Enable debug logging to see model selection decisions:

```bash
export LATTICE_LOG_LEVEL=DEBUG
lattice-lock orchestrator route "your task here"
```

### Validating Configuration

Run the validation script to check your MODELS.md:

```bash
python scripts/validate_models_md.py
```

---

## Notes

- These preferences are intended to be "best effort." Providers can be unavailable due to missing API keys.
- See `src/lattice_lock/orchestrator/models.yaml` for the canonical list of model IDs and capabilities.
- See `src/lattice_lock/orchestrator/scorer_config.yaml` for scoring weight configuration.
- The parser (`ModelGuideParser`) requires exact model ID matches - typos will cause silent failures.
- Fallback chains use `->` as the delimiter (not `>`).
- Task preferences use `>` as the delimiter (not `->`).
