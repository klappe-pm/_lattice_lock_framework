# Module 3: Configuration & Environment Management Comparison

## Executive Summary

Lattice Lock uses **code-centric configuration** (pyproject.toml, embedded YAML) while PAL MCP uses **environment-centric configuration** (.env, JSON catalogs). Lattice Lock's approach is more structured but less flexible at runtime; PAL MCP's approach enables rapid reconfiguration without code changes.

---

## Configuration File Inventory

### Questions
1. Lattice Lock uses multiple different types of configuration file types. PAL MCP uses EVN and JSON. Research the benefits to stramlining the files types used for configuration. Decide if: Lattice Lock should migrate configuration files to ENV and JSON format.

### Lattice Lock Configuration

| File | Purpose | Lines |
|------|---------|-------|
| `pyproject.toml` | Project config, dependencies, tool settings | 180 |
| `Makefile` | Build automation commands | 47 |
| `.pre-commit-config.yaml` | Pre-commit hooks (7 hooks) | 64 |
| `src/lattice_lock/orchestrator/models.yaml` | Model definitions | 203 |
| `src/lattice_lock/orchestrator/scorer_config.yaml` | Scorer weights | 41 |
| `lattice.yaml` (user) | Governance rules | Varies |
| `.gitignore` | Git ignore patterns | ~100 |
| `docker-compose.yml` | Container orchestration | ~30 |

### PAL MCP Configuration

| File | Purpose | Format |
|------|---------|--------|
| `.env.example` | Complete environment template | ENV |
| `conf/openai_models.json` | OpenAI model catalog | JSON |
| `conf/gemini_models.json` | Gemini model catalog | JSON |
| `conf/openrouter_models.json` | OpenRouter catalog | JSON |
| `conf/azure_models.json` | Azure model catalog | JSON |
| `conf/custom_models.json` | Custom model catalog | JSON |

---

## Model Configuration Comparison

### Lattice Lock: Embedded YAML

```yaml
# src/lattice_lock/orchestrator/models.yaml
version: "1.0"
models:
  - id: grok-4-fast-reasoning
    api_name: grok-4-fast-reasoning
    provider: xai
    context_window: 2000000
    input_cost: 2.0
    output_cost: 6.0
    reasoning_score: 95.0
    coding_score: 85.0
    speed_rating: 7.0
    maturity: beta
    supports_function_calling: true
```

**Providers covered:** xai (3), openai (4), google (2), anthropic (6), ollama (2) = 17 models

### PAL MCP: External JSON Catalogs

```json
// conf/openai_models.json
{
  "_README": "Schema documentation...",
  "models": [
    {
      "id": "gpt-4o",
      "intelligence_score": 95,
      "context_window": 128000,
      "input_cost_per_million": 5.0,
      "output_cost_per_million": 15.0,
      "allow_code_generation": true,
      "supports_json_mode": true,
      "supports_vision": true
    }
  ]
}
```

### Key Differences

| Aspect | Lattice Lock | PAL MCP |
|--------|--------------|---------|
| Format | YAML (embedded) | JSON (external) |
| Location | `src/lattice_lock/orchestrator/` | `conf/` directory |
| Override | Requires code/restart | Env var `*_MODELS_CONFIG_PATH` |
| Documentation | Comments in YAML | `_README` block in JSON |
| Schema validation | Python models | N/A |
| Per-provider files | ❌ Single file | ✅ Separate files |
| Custom models | ❌ Add to YAML | ✅ `custom_models.json` |

**Gap:** Lattice Lock lacks external config override capability.

---

## Environment Variable Patterns

### Lattice Lock: Minimal Environment

```bash
# Currently inferred from code (no .env.example)
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...
XAI_API_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=...
```

### PAL MCP: Comprehensive .env.example

```bash
# .env.example - PAL MCP Pattern
# --- Feature Flags ---
DISABLED_TOOLS=analyze,refactor,testgen,secaudit,docgen,tracer

# --- Model Selection ---
DEFAULT_MODEL=auto
DEFAULT_THINKING_MODE_THINKDEEP=high

# --- Provider API Keys ---
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

# --- External Config Paths ---
OPENAI_MODELS_CONFIG_PATH=/path/to/openai_models.json
GEMINI_MODELS_CONFIG_PATH=/path/to/gemini_models.json

# --- Override Flags ---
PAL_MCP_FORCE_ENV_OVERRIDE=true

# --- Docker ---
DOCKER_HOST=unix:///var/run/docker.sock

# --- Logging ---
LOG_LEVEL=INFO
```

### Gap Analysis

| Pattern | Lattice Lock | PAL MCP |
|---------|--------------|---------|
| `.env.example` | ❌ Missing | ✅ Comprehensive |
| Feature flags | ❌ None | ✅ `DISABLED_TOOLS` |
| Config path overrides | ❌ None | ✅ `*_CONFIG_PATH` |
| Default model selection | ❌ Code-defined | ✅ `DEFAULT_MODEL` |
| Force override flag | ❌ None | ✅ `PAL_MCP_FORCE_ENV_OVERRIDE` |
| Thinking mode config | ❌ None | ✅ `DEFAULT_THINKING_MODE_*` |

---

## Scorer Configuration

### Lattice Lock: scorer_config.yaml

```yaml
# Priority weights for different selection modes
priority_weights:
  quality:
    reasoning: 0.3
    coding: 0.2
    base: 0.5
  speed:
    speed: 0.5
    base: 0.5
  cost:
    cost: 0.5
    base: 0.5
  balanced:
    reasoning: 0.2
    coding: 0.2
    speed: 0.1
    base: 0.5

# Task-specific score boosts
task_boosts:
  CODE_GENERATION:
    coding: 0.2
  DEBUGGING:
    coding: 0.2
  REASONING:
    reasoning: 0.2
```

### PAL MCP: Intelligence Score

```json
{
  "intelligence_score": 95  // 1-100, affects auto-selection sort
}
```

**Comparison:**
- Lattice Lock: Multi-dimensional scoring (reasoning, coding, speed, cost)
- PAL MCP: Single-dimension scoring with capability flags

**Lattice Lock advantage:** More nuanced model selection for governance use cases.

---

## Governance Configuration (lattice.yaml)

Lattice Lock's unique configuration pattern:

```yaml
# lattice.yaml - Governance rules
version: v2.1
generated_module: types_basic

entities:
  User:
    fields:
      id:
        type: uuid
        primary_key: true
      username:
        type: str
        unique: true
      age:
        type: int
        gte: 0
        lte: 150
```

**Features:**
- Domain entity definitions
- Field type constraints
- Uniqueness rules
- Boundary validation

**PAL MCP equivalent:** None - PAL MCP doesn't have governance configuration.

---

## Pre-Commit Configuration

### Lattice Lock: Comprehensive Hooks

```yaml
repos:
  # Standard hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - trailing-whitespace
      - end-of-file-fixer
      - check-yaml
      - check-added-large-files
      - detect-private-key

  # Formatters
  - repo: https://github.com/psf/black
  - repo: https://github.com/pycqa/isort
  - repo: https://github.com/astral-sh/ruff-pre-commit

  # Custom Lattice Lock hooks
  - repo: local
    hooks:
      - id: lattice-structure-check
      - id: lattice-naming-check
      - id: mcp-no-secrets
```

**Strength:** Custom hooks for structure and naming validation.

---

## Recommendations

### P0 - Create .env.example (Immediate)

```bash
# .env.example for Lattice Lock

# === Provider API Keys ===
# At least one provider is required
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
XAI_API_KEY=

# AWS Bedrock (optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Ollama (local models)
OLLAMA_HOST=http://localhost:11434

# === Feature Flags ===
# Comma-separated list of features to disable
LATTICE_DISABLED_FEATURES=

# === Model Selection ===
# Override default model selection
LATTICE_DEFAULT_MODEL=auto

# === Logging ===
LATTICE_LOG_LEVEL=INFO

# === Database ===
DATABASE_URL=sqlite:///lattice.db

# === Admin API ===
ADMIN_SECRET_KEY=
JWT_SECRET_KEY=
```

### P1 - Externalize Model Config (Medium Effort)

**Option A:** Keep YAML, add override path

```bash
LATTICE_MODELS_CONFIG_PATH=/custom/models.yaml
```

**Option B:** Switch to JSON with per-provider files

```
conf/
├── openai.json
├── anthropic.json
├── google.json
├── xai.json
└── ollama.json
```

**Recommendation:** Option A - simpler, maintains existing format.

### P2 - Add Feature Flags

```python
# config.py
import os

DISABLED_FEATURES = set(
    f.strip() 
    for f in os.getenv("LATTICE_DISABLED_FEATURES", "").split(",") 
    if f.strip()
)

def is_enabled(feature: str) -> bool:
    return feature not in DISABLED_FEATURES
```

---

## Configuration Pattern Summary

| Pattern | Status | Priority | Effort |
|---------|--------|----------|--------|
| Create `.env.example` | ❌ Missing | P0 | 30 min |
| Add `LATTICE_DISABLED_FEATURES` | ❌ Missing | P1 | 2 hours |
| Add models config path override | ❌ Missing | P1 | 2 hours |
| Add `LATTICE_DEFAULT_MODEL` | ❌ Missing | P2 | 1 hour |
| Switch to per-provider JSON | ❌ N/A | P3 | 8 hours |
| Keep multi-dimensional scoring | ✅ Good | N/A | N/A |
| Keep lattice.yaml governance | ✅ Unique | N/A | N/A |

---

*Module 3 completed. Next: Module 4 - Documentation & Developer Experience*
