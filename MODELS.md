# Model Selection Guide

This file provides human-editable preferences for model routing in the Lattice Lock Orchestrator.
It is parsed by `lattice_lock.orchestrator.guide.ModelGuideParser`.

## Parsing Notes

The parser expects specific section formats:

- `### Code Tasks` section with lines formatted as: `- **task_key**: model_a > model_b > model_c`
- `### Blocked Models` section with lines starting with `- `. Parsing stops at the next `## ` heading.
- `### Fallback Chains` section with lines formatted as: `- task_key: model_a -> model_b -> model_c`

Model IDs must match the registry IDs exactly (see `docs/models/registry.yaml`).

### Code Tasks

Models are ordered by preference: premium (highest quality) > standard > budget/local (free).

- **code_generation**: o1-pro > claude-opus-4.5 > claude-sonnet-4.5 > grok-code-fast-1 > qwen3-next-80b > codellama:34b > glm4 > magicoder:7b
- **debugging**: o1 > claude-sonnet-4 > grok-4-fast-reasoning > gemini-2.0-pro > qwen3-next-80b > deepseek-r1:70b > codellama:34b
- **architectural_design**: o1-pro > claude-opus-4 > qwen3-next-80b > gemini-3.0-pro-high > grok-4-fast-reasoning > llama3.1:70b
- **documentation**: claude-3-5-sonnet > gpt-4o > gemini-1.5-pro > grok-4-fast-non-reasoning > gemini-2.5-flash > glm4 > qwen2.5:32b
- **testing**: o1-mini > claude-sonnet-4 > gemini-2.0-flash > grok-code-fast-1 > glm4 > codellama:34b
- **data_analysis**: o1-pro > gemini-3.0-pro-low > gpt-4o > grok-4-fast-reasoning > qwen3-next-80b > llama3.1:70b > qwen2.5:32b
- **general**: gpt-4o > claude-3-5-haiku > gemini-2.5-flash > grok-4-fast-non-reasoning > glm4 > llama3.1:8b
- **reasoning**: o1-pro > claude-opus-4.5 > grok-4-fast-reasoning > qwen3-next-80b > gemini-3.0-pro-high > deepseek-r1:70b > llama3.1:405b
- **vision**: gpt-4o > claude-opus-4 > gemini-2.0-pro > grok-2-vision-1212 > llama3.2:90b > llama3.2:11b
- **security_audit**: o1-pro > claude-sonnet-4.5 > gpt-4-turbo > grok-4-fast-reasoning > codellama:34b
- **creative_writing**: claude-opus-4.5 > gpt-4o > gemini-1.5-pro > claude-3-haiku > grok-3 > llama3.1:70b
- **translation**: gemini-2.5-flash > qwen2.5:32b > gpt-4o-mini > grok-3 > qwen2.5:7b-instruct > qwen3:8b

### Blocked Models

Models listed here will be excluded from automatic selection.
Note: Block list uses exact-match. To block a model family, list each variant.

- llama3.2:3b
- deepseek-coder:1.3b

## Fallbacks

### Fallback Chains

When a primary model fails, the orchestrator will attempt these models in order.
Chains should include models from different providers for resilience.

- code_generation: o1-pro → claude-sonnet-4.5 → grok-code-fast-1 → qwen3-next-80b → codellama:34b → glm4 → magicoder:7b
- debugging: o1 → claude-sonnet-4 → grok-4-fast-reasoning → gemini-2.0-pro → qwen3-next-80b → deepseek-r1:70b
- architectural_design: o1-pro → claude-opus-4 → qwen3-next-80b → gemini-3.0-pro-high → grok-4-fast-reasoning → llama3.1:70b
- documentation: claude-3-5-sonnet → gpt-4o → gemini-2.5-flash → claude-3-5-haiku → glm4 → qwen2.5:32b
- testing: o1-mini → claude-sonnet-4 → gemini-2.0-flash → grok-code-fast-1 → glm4 → codellama:34b
- data_analysis: o1-pro → gemini-3.0-pro-low → gpt-4o → grok-4-fast-reasoning → qwen3-next-80b → llama3.1:70b
- general: gpt-4o → claude-3-5-haiku → gemini-2.5-flash → gpt-3.5-turbo → glm4 → llama3.1:8b
- reasoning: o1-pro → claude-opus-4.5 → grok-4-fast-reasoning → qwen3-next-80b → gemini-3.0-pro-high → deepseek-r1:70b
- vision: gpt-4o → claude-opus-4 → gemini-2.0-pro → grok-2-vision-1212 → llama3.2:90b
- security_audit: o1-pro → claude-sonnet-4.5 → gpt-4-turbo → grok-4-fast-reasoning → codellama:34b
- creative_writing: claude-opus-4.5 → gpt-4o → gemini-1.5-pro → claude-3-haiku → llama3.1:70b
- translation: gemini-2.5-flash → qwen2.5:32b → gpt-4o-mini → qwen2.5:7b-instruct → qwen3:8b

### Provider Reference

| Provider | Models | Notes |
|----------|--------|-------|
| OpenAI | o1-pro, o1, o1-mini, gpt-4o, gpt-4-turbo, gpt-4, gpt-4o-mini, gpt-3.5-turbo | Production-ready, requires OPENAI_API_KEY |
| Anthropic | claude-opus-4.5, claude-sonnet-4.5, claude-opus-4, claude-sonnet-4, claude-3-5-sonnet, claude-3-5-haiku, claude-3-haiku | Production-ready, requires ANTHROPIC_API_KEY |
| Google | gemini-3.0-pro-high, gemini-3.0-pro-low, gemini-3.0-flash, gemini-2.0-pro, gemini-2.0-flash, gemini-2.5-pro, gemini-2.5-flash, gemini-1.5-pro, gemini-1.5-flash | Beta/Experimental, requires GOOGLE_API_KEY |
| xAI | grok-4-fast-reasoning, grok-4-fast-non-reasoning, grok-code-fast-1, grok-3, grok-2-vision-1212 | Beta, requires XAI_API_KEY |
| Azure | azure-gpt-4o, azure-gpt-4-turbo, azure-gpt-4, azure-claude-3.5-sonnet | Production-ready, requires AZURE_OPENAI_KEY |
| Bedrock | bedrock-claude-3-opus, bedrock-claude-3.5-sonnet, bedrock-llama-3.1-405b, bedrock-llama-3.1-70b | Production-ready, requires AWS credentials |
|| Ollama | qwen3-next-80b, deepseek-r1:70b, glm4, codellama:34b, qwen2.5:32b, magicoder:7b, llama3.1:70b, llama3.1:405b, etc. | Local/Free, requires Ollama installation ||

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
See `docs/models/registry.yaml` for the canonical list of model IDs and capabilities.
