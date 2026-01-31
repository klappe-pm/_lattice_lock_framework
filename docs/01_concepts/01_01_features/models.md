---
title: "Model Selection Guide"
type: concept
status: stable
categories: [Concepts, Models]
sub_categories: [Selection]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [concept-models-001]
tags: [concept, models, selection, guide]
author: AI Agent
---

# Model Selection Guide

This file provides human-editable preferences for model routing in the Lattice Lock Orchestrator.
It is parsed by `lattice_lock.orchestrator.guide.ModelGuideParser`.

> **Note**: This is a documentation copy of the root `MODELS.md` file. The canonical source
> is located at `/MODELS.md` in the project root. For the complete guide including examples,
> cost tiers, and troubleshooting, see the root file.

## Parsing Notes

The parser expects specific section formats:

- `### Code Tasks` section with lines formatted as: `- **task_key**: model_a > model_b > model_c`
- `### Blocked Models` section with lines starting with `- `. Parsing stops at the next `## ` heading.
- `### Fallback Chains` section with lines formatted as: `- task_key: model_a -> model_b -> model_c`

Model IDs must match the registry IDs exactly (see `src/lattice_lock/orchestrator/models.yaml`).

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

### Blocked Models

Models listed here will be excluded from automatic selection.
Note: Block list uses exact-match. To block a model family, list each variant.

- llama3.2:3b
- deepseek-coder:1.3b

## Fallbacks

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

### Provider Reference

| Provider | Models | Status | Required Environment |
|----------|--------|--------|---------------------|
| OpenAI | o1-pro, o1-mini, gpt-4o, gpt-4o-mini | Production | `OPENAI_API_KEY` |
| Anthropic | claude-4-5-opus, claude-4-5-sonnet, claude-4-sonnet, claude-3-7-sonnet, claude-3-5-haiku | Production | `ANTHROPIC_API_KEY` |
| Google | gemini-2.5-pro, gemini-2.5-flash | Beta | `GOOGLE_API_KEY` |
| xAI | grok-4-fast-reasoning, grok-code-fast-1, grok-3 | Beta | `XAI_API_KEY` |
| Azure | azure-gpt-4o, azure-gpt-4-turbo | Production | `AZURE_OPENAI_KEY`, `AZURE_ENDPOINT` |
| Bedrock | bedrock-claude-3-opus, bedrock-claude-3.5-sonnet | Production | AWS credentials (IAM or explicit) |
| Ollama | qwen3-next-80b, deepseek-r1:70b, glm4, codellama:34b, qwen2.5:32b | Local | `OLLAMA_HOST` (optional) |

### Task Type Reference

| Task Type | Description | Key Capabilities |
|-----------|-------------|------------------|
| code_generation | Writing new code | High coding score |
| debugging | Finding and fixing bugs | Coding + reasoning |
| architectural_design | System design decisions | Strong reasoning |
| documentation | Writing docs and comments | Balanced skills |
| testing | Writing and analyzing tests | Coding focus |
| data_analysis | Analyzing data patterns | Reasoning + coding |
| general | General-purpose tasks | Balanced, fast |
| reasoning | Complex logical problems | High reasoning score |
| vision | Image understanding | Vision capability required |
| security_audit | Security analysis | Coding + reasoning |
| creative_writing | Creative content | High reasoning |
| translation | Language translation | Multilingual support |

### Notes

These preferences are intended to be "best effort." Providers can be unavailable due to missing API keys.
See `src/lattice_lock/orchestrator/models.yaml` for the canonical list of model IDs and capabilities.

For the complete guide with examples, cost tiers, capability matrix, and troubleshooting, see `/MODELS.md` in the project root.
