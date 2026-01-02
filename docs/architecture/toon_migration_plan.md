# TOON Notation Migration Plan for Lattice Lock

## Executive Summary

This document outlines the complete plan to migrate Lattice Lock's configuration system to support TOON (Token-Oriented Object Notation) with bidirectional compilation capabilities. The migration is designed for future-proofing at 10,000-100,000% scale growth while maintaining JSON as a hedge format for interoperability.

**Key Deliverables:**
1. Bidirectional Compiler (YAML ↔ TOON ↔ JSON)
2. Normalized Table Architecture for token efficiency
3. Token Tracking Integration for cost visibility
4. Comprehensive Test Suite for round-trip validation
5. CLI Commands for format conversion

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Current State Analysis](#current-state-analysis)
3. [Target State Design](#target-state-design)
4. [Normalization Strategy](#normalization-strategy)
5. [Bidirectional Compilation Pipeline](#bidirectional-compilation-pipeline)
6. [Token Tracker Integration](#token-tracker-integration)
7. [Migration Phases](#migration-phases)
8. [Test Strategy](#test-strategy)
9. [Risk Mitigations](#risk-mitigations)
10. [File Structure](#file-structure)
11. [Dependencies](#dependencies)
12. [Success Metrics](#success-metrics)

---

## Architecture Overview

### Design Principles

1. **Canonical AST as Intermediate Representation**
   - All formats parse to Python dict (AST)
   - All formats serialize from Python dict (AST)
   - Enables any-to-any conversion

2. **JSON as Hedge Format**
   - TOON → JSON conversion always available
   - Guaranteed interoperability escape hatch
   - No vendor lock-in to TOON

3. **Dual-Format Strategy**
   - Source of truth: Human-editable YAML (existing)
   - LLM consumption: Compiled normalized TOON
   - Compilation: Automated in CI/CD

4. **Normalization for Scale**
   - Hierarchical configs → Relational tables
   - Enables 75%+ token savings at scale
   - Supports cross-referencing without full context load

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SOURCE LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  YAML Files  │  │  JSON Files  │  │  TOON Files  │               │
│  │  (Human Edit)│  │  (API/Export)│  │  (LLM Input) │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
└─────────┼─────────────────┼─────────────────┼───────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PARSER LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ YAML Parser  │  │ JSON Parser  │  │ TOON Parser  │               │
│  │ (PyYAML)     │  │ (stdlib)     │  │ (toon-python)│               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           m   │
└─────────┼─────────────────┼─────────────────┼───────────────────────┘
          │                 │                 │
          └────────────────►│◄────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CANONICAL AST LAYER                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Python Dict (AST)                         │   │
│  │  - Format-agnostic representation                            │   │
│  │  - Preserves all semantic content                            │   │
│  │  - Includes _meta for versioning                             │   │
│  └────────────────────────────────────────────────────────── ───┘   │
└─────────────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TRANSFORM LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Normalizer  │  │Denormalizer  │  │  Validator   │               │
│  │  (→ Tables)  │  │  (→ Hierarchy│  │  (Round-trip)│               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SERIALIZER LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │YAML Serialize│  │JSON Serialize│  │TOON Serialize│               │
│  │ (PyYAML)     │  │ (stdlib)     │  │ (toon-python)│               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
└─────────┼─────────────────┼─────────────────┼───────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OUTPUT LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  .yaml       │  │  .json       │  │  .toon       │               │
│  │  (Human)     │  │  (Hedge/API) │  │  (LLM)       │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TOKEN TRACKER LAYER                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  - Count tokens per format                                  │    │
│  │  - Estimate costs (input/output)                            │    │
│  │  - Compare format efficiency                                │    │
│  │  - Track historical usage                                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Current State Analysis

### Configuration File Inventory

| Category | Count | Format | Token Impact |
|----------|-------|--------|--------------|
| Lattice Schemas (`lattice.yaml`) | ~10 | YAML | High (nested entities) |
| Agent Definitions | ~90 | YAML | High (repeated structure) |
| Agent Templates | ~12 | YAML | Medium |
| Model Registry | 2 | YAML | High (uniform array) |
| Scorer Config | 1 | YAML | Low |
| CI/CD Templates | ~5 | YAML/Jinja | Low |
| Test Fixtures | ~10 | YAML | Medium |

### Current Pain Points

1. **Token Inefficiency**: YAML repeats keys for every entity/agent
2. **No Cross-Reference Optimization**: Full files loaded for single lookups
3. **Scale Concerns**: 10,000x growth = 10,000x token costs
4. **No Cost Visibility**: Users can't see token impact of configs

### YAML Structure Patterns (Current)

**Pattern 1: Dict of Dicts (Entities)**
```yaml
entities:
  Customer:
    fields:
      id: {type: uuid, primary_key: true}
      email: {type: str, unique: true}
  Order:
    fields:
      id: {type: uuid, primary_key: true}
      customer_id: {type: uuid}
```

**Pattern 2: Nested Hierarchy (Agents)**
```yaml
agent:
  identity:
    name: engineering_agent
    role: Engineering Lead
  delegation:
    allowed_subagents:
      - name: backend_developer
        file: subagents/backend.yaml
```

**Pattern 3: Uniform Arrays (Models)**
```yaml
models:
  - id: gpt-4o
    provider: openai
    context_window: 128000
  - id: claude-3-5-sonnet
    provider: anthropic
    context_window: 200000
```

---

## Target State Design

### Compiled TOON Output Structure

```
.lattice-lock/
├── compiled/
│   ├── toon/                      # TOON format (LLM-optimized)
│   │   ├── agents.toon            # All agents normalized
│   │   ├── agent_subagents.toon   # Agent → subagent relations
│   │   ├── agent_capabilities.toon
│   │   ├── schemas.toon           # All entity schemas
│   │   ├── fields.toon            # All fields normalized
│   │   ├── field_constraints.toon
│   │   ├── models.toon            # Model registry
│   │   ├── model_capabilities.toon
│   │   └── _index.toon            # Master index
│   │
│   ├── json/                      # JSON format (hedge/API)
│   │   ├── agents.json
│   │   ├── schemas.json
│   │   └── models.json
│   │
│   └── _manifest.json             # Compilation manifest
│
└── stats/
    └── token_usage.json           # Token tracking data
```

### Normalized Table Examples

**agents.toon** (from 90 YAML files):
```
agents[90]{_id,name,version,role,status,primary_goal}:
  agt_0001,engineering_agent,2.1.0,Engineering Lead,beta,Design and implement systems
  agt_0002,product_agent,2.1.0,Product Lead,beta,Define product strategy
  agt_0003,research_agent,2.1.0,Research Lead,beta,Conduct market research
  ...
```

**agent_subagents.toon** (junction table):
```
agent_subagents[450]{agent_id,subagent_name,subagent_file}:
  agt_0001,system_architect,subagents/system_architect.yaml
  agt_0001,api_designer,subagents/api_designer.yaml
  agt_0001,backend_developer,subagents/backend_developer.yaml
  ...
```

**schemas.toon** (from lattice.yaml files):
```
schemas[50]{_id,name,module,description,persistence}:
  sch_0001,Customer,ecommerce_types,Represents a customer,table
  sch_0002,Order,ecommerce_types,Customer order,table
  ...
```

**fields.toon** (normalized from all schemas):
```
fields[425]{_id,schema_id,name,type,primary_key,unique,nullable,default}:
  fld_0001,sch_0001,id,uuid,true,false,false,null
  fld_0002,sch_0001,email,str,false,true,false,null
  fld_0003,sch_0001,credit_limit,decimal,false,false,false,null
  ...
```

---

## Normalization Strategy

### Strategy Selection by Config Type

| Config Type | Strategy | Reason |
|-------------|----------|--------|
| Agent Definitions | RELATIONAL | Many files, uniform structure, cross-references |
| Lattice Schemas | RELATIONAL | Nested entities → tables, fields → rows |
| Model Registry | RELATIONAL | Uniform array, ideal for TOON |
| Scorer Config | NONE | Small, deeply nested, rarely queried |
| CI/CD Templates | NONE | Jinja templates, not data |

### Normalization Rules

1. **Dict of Dicts → Table with Name Column**
   ```yaml
   entities:
     Customer: {...}
     Order: {...}
   ```
   → 
   ```
   schemas[2]{_id,name,...}:
     sch_0001,Customer,...
     sch_0002,Order,...
   ```

2. **Nested Arrays → Junction Tables**
   ```yaml
   delegation:
     allowed_subagents:
       - name: backend
       - name: frontend
   ```
   →
   ```
   agent_subagents[2]{agent_id,subagent_name}:
     agt_0001,backend
     agt_0001,frontend
   ```

3. **Nested Objects → Child Tables or Flatten**
   ```yaml
   identity:
     name: engineering_agent
     version: 2.1.0
   ```
   →
   ```
   agents[1]{_id,name,version}:
     agt_0001,engineering_agent,2.1.0
   ```

### Denormalization for JSON Export

The denormalizer reconstructs hierarchical JSON from normalized tables:

```python
# Normalized TOON tables
{
    "schemas": [{"_id": "sch_0001", "name": "Customer", ...}],
    "fields": [{"schema_id": "sch_0001", "name": "id", ...}]
}

# Denormalized JSON (hedge format)
{
    "entities": {
        "Customer": {
            "fields": {
                "id": {...}
            }
        }
    }
}
```

---

## Bidirectional Compilation Pipeline

### Compiler Interface

```python
from lattice_lock.compiler import LatticeCompiler, CompilerConfig

# Initialize compiler
config = CompilerConfig(
    normalize_for_toon=True,
    include_metadata=True,
    validate_roundtrip=True,
    fallback_to_json=True,
    track_tokens=True,
)
compiler = LatticeCompiler(config)

# YAML → TOON (normalized)
result = compiler.compile("agents/engineering_agent/definition.yaml", target_format="toon")

# TOON → JSON (hedge format)
result = compiler.compile("compiled/agents.toon", target_format="json")

# Validate round-trip
validations = compiler.validate_roundtrip("agents/engineering_agent/definition.yaml")
# {"yaml→toon": True, "yaml→json": True, "toon→json": True}

# Get token stats
stats = compiler.get_token_stats("agents/engineering_agent/definition.yaml")
# {"yaml": {"tokens": 450}, "toon": {"tokens": 120}, "json": {"tokens": 380}}
```

### CLI Commands

```bash
# Compile single file
lattice compile config.yaml --format toon --output compiled/

# Compile all configs to TOON
lattice compile --all --format toon --output .lattice-lock/compiled/toon/

# Compile to all formats (YAML, TOON, JSON)
lattice compile config.yaml --format all --output compiled/

# Convert between formats
lattice convert input.toon --to json --output output.json
lattice convert input.yaml --to toon --output output.toon

# Validate round-trip
lattice compile config.yaml --validate-roundtrip

# Show token statistics
lattice compile config.yaml --stats

# Compare formats
lattice compile config.yaml --compare
# Output:
# ┌────────┬────────┬───────────┬─────────┐
# │ Format │ Tokens │ Size (KB) │ Savings │
# ├────────┼────────┼───────────┼─────────┤
# │ YAML   │    450 │      12.3 │ baseline│
# │ TOON   │    120 │       3.1 │   73.3% │
# │ JSON   │    380 │      10.8 │   15.6% │
# └────────┴────────┴───────────┴─────────┘
```

### Batch Compilation (CI/CD)

```bash
# In CI/CD pipeline
lattice compile --all \
  --format toon \
  --normalize \
  --output .lattice-lock/compiled/toon/ \
  --validate-roundtrip \
  --stats \
  --fail-on-roundtrip-error

# Generate manifest
lattice compile --manifest > .lattice-lock/compiled/_manifest.json
```

---

## Token Tracker Integration

### Token Tracker Features

1. **Per-File Token Counting**
   - Count tokens for each config file
   - Compare across formats (YAML, TOON, JSON)
   - Track savings percentage

2. **Cost Estimation**
   - Estimate input/output costs by provider
   - Support for GPT-4, Claude, Gemini pricing
   - Configurable pricing tables

3. **Historical Tracking**
   - Track token usage over time
   - Identify optimization opportunities
   - Alert on token budget thresholds

4. **Dashboard Integration**
   - Visualize token usage by config type
   - Show format comparison charts
   - Display cost projections

### Token Tracker API

```python
from lattice_lock.compiler import TokenTracker, TokenStats

tracker = TokenTracker()

# Analyze single file
stats = tracker.analyze("config.yaml", format_type="yaml")
# TokenStats(token_count=450, char_count=12345, estimated_cost_input=0.00135)

# Compare formats
comparison = tracker.compare_formats("config.yaml")
# {
#     "yaml": TokenStats(token_count=450, ...),
#     "toon": TokenStats(token_count=120, ...),
#     "json": TokenStats(token_count=380, ...),
#     "best_format": "toon",
#     "max_savings_percent": 73.3
# }

# Estimate costs
costs = tracker.estimate_costs("config.yaml", provider="anthropic", model="claude-3-5-sonnet")
# {"input_cost": 0.00135, "output_cost": 0.00675, "total": 0.0081}

# Batch analysis
batch_stats = tracker.analyze_directory("agents/", recursive=True)
# {"total_tokens": 45000, "files": [...], "by_format": {...}}
```

### Placeholder: Token Tracker Dashboard Widget

```
┌─────────────────────────────────────────────────────────────────────┐
│ TOKEN USAGE DASHBOARD                                     [Refresh] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Config Type        │ YAML Tokens │ TOON Tokens │ Savings          │
│  ───────────────────┼─────────────┼─────────────┼──────────        │
│  Agent Definitions  │     45,000  │     12,000  │  73.3%           │
│  Lattice Schemas    │     15,000  │      4,000  │  73.3%           │
│  Model Registry     │      1,200  │        350  │  70.8%           │
│  ───────────────────┼─────────────┼─────────────┼──────────        │
│  TOTAL              │     61,200  │     16,350  │  73.3%           │
│                                                                     │
│  Estimated Monthly Cost (at 100 reads/day):                        │
│    YAML: $54.72  │  TOON: $14.72  │  Savings: $39.98/month        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Migration Phases

### Phase 0: Foundation (Week 1-2)

**Objectives:**
- Set up TOON library dependency
- Create compiler module structure
- Establish testing framework

**Tasks:**

- [ ] Add `toon-format` to dependencies (pyproject.toml)
- [ ] Create `src/lattice_lock/compiler/` module structure
- [ ] Implement `LatticeCompiler` core class
- [ ] Implement format detection utilities
- [ ] Create basic round-trip tests
- [ ] Update CI/CD to run compiler tests

**Deliverables:**
- `src/lattice_lock/compiler/__init__.py`
- `src/lattice_lock/compiler/core.py`
- `src/lattice_lock/compiler/formats.py`
- `tests/compiler/test_core.py`
- `tests/compiler/test_formats.py`

**Success Criteria:**
- Can parse YAML, JSON, TOON files
- Can serialize to YAML, JSON, TOON
- Basic round-trip tests pass

---

### Phase 1: Normalizer Implementation (Week 3-4)

**Objectives:**
- Implement normalization strategies
- Create specialized normalizers for each config type
- Implement denormalization for JSON hedge

**Tasks:**

- [ ] Implement `Normalizer` base class
- [ ] Implement `AgentNormalizer` for agent definitions
- [ ] Implement `SchemaNormalizer` for lattice.yaml
- [ ] Implement `ModelNormalizer` for model registry
- [ ] Implement denormalization (tables → hierarchy)
- [ ] Create normalization tests

**Deliverables:**
- `src/lattice_lock/compiler/normalizer.py`
- `tests/compiler/test_normalizer.py`
- `tests/compiler/fixtures/` (test data)

**Success Criteria:**
- Agent definitions normalize to tables
- Schemas normalize to tables
- Denormalization reconstructs original structure
- Round-trip validation passes

---

### Phase 2: Token Tracker (Week 5-6)

**Objectives:**
- Implement token counting
- Add cost estimation
- Create comparison utilities

**Tasks:**

- [ ] Add `tiktoken` dependency
- [ ] Implement `TokenTracker` class
- [ ] Implement `TokenStats` dataclass
- [ ] Add cost estimation by provider
- [ ] Create format comparison utilities
- [ ] Add token stats to compilation results

**Deliverables:**
- `src/lattice_lock/compiler/token_tracker.py`
- `tests/compiler/test_token_tracker.py`

**Success Criteria:**
- Token counts match tiktoken directly
- Cost estimates are accurate
- Format comparisons show savings

---

### Phase 3: CLI Integration (Week 7-8)

**Objectives:**
- Add compile command enhancements
- Add convert command
- Add stats/compare options

**Tasks:**

- [ ] Enhance `lattice compile` with format options
- [ ] Add `lattice convert` command
- [ ] Add `--stats` flag for token statistics
- [ ] Add `--compare` flag for format comparison
- [ ] Add `--validate-roundtrip` flag
- [ ] Update CLI documentation

**Deliverables:**
- Updated `src/lattice_lock/cli/commands/compile.py`
- New `src/lattice_lock/cli/commands/convert.py`
- Updated CLI help and documentation

**Success Criteria:**
- `lattice compile --format toon` works
- `lattice convert` works bidirectionally
- Token stats display correctly

---

### Phase 4: Batch Compilation & CI/CD (Week 9-10)

**Objectives:**
- Implement batch compilation
- Add manifest generation
- Integrate with CI/CD

**Tasks:**

- [ ] Implement `--all` flag for batch compilation
- [ ] Create manifest generator
- [ ] Add pre-commit hook for compilation
- [ ] Add GitHub Action for TOON compilation
- [ ] Create `.lattice-lock/compiled/` structure

**Deliverables:**
- Batch compilation feature
- `_manifest.json` generation
- `.github/workflows/compile-toon.yml`
- `.pre-commit-config.yaml` updates

**Success Criteria:**
- All configs compile to TOON
- Manifest tracks all compiled files
- CI/CD validates round-trip on PR

---

### Phase 5: Dashboard Integration (Week 11-12)

**Objectives:**
- Add token usage to dashboard
- Create visualization widgets
- Add cost projections

**Tasks:**

- [ ] Create TokenUsage API endpoint
- [ ] Add token stats to dashboard
- [ ] Create format comparison chart
- [ ] Add cost projection widget
- [ ] Create historical tracking view

**Deliverables:**
- Dashboard token usage widgets
- API endpoints for token data
- Historical tracking storage

**Success Criteria:**
- Dashboard shows token usage
- Format comparison is visual
- Cost projections are displayed

---

### Phase 6: Documentation & Rollout (Week 13-14)

**Objectives:**
- Complete documentation
- Team training
- Production rollout

**Tasks:**

- [ ] Write user documentation
- [ ] Write developer documentation
- [ ] Create migration guide
- [ ] Team training sessions
- [ ] Gradual rollout to production

**Deliverables:**
- `docs/guides/toon-migration.md`
- `docs/reference/compiler-api.md`
- Training materials
- Rollout plan

**Success Criteria:**
- Team understands TOON format
- Documentation is complete
- Production using TOON compilation

---

## Test Strategy

### Test Categories

1. **Unit Tests** (`tests/compiler/`)
   - Parser tests for each format
   - Serializer tests for each format
   - Normalizer tests
   - Token tracker tests

2. **Integration Tests** (`tests/compiler/integration/`)
   - Full compilation pipeline
   - CLI command tests
   - Batch compilation tests

3. **Round-Trip Tests** (`tests/compiler/roundtrip/`)
   - YAML → TOON → YAML
   - YAML → JSON → YAML
   - TOON → JSON → TOON
   - Normalized → Denormalized → Normalized

4. **Fixture Tests** (`tests/compiler/fixtures/`)
   - All example lattice.yaml files
   - All agent definition files
   - All model registry files

### Test Matrix

| Test Type | YAML | JSON | TOON | Normalized |
|-----------|------|------|------|------------|
| Parse     | ✓    | ✓    | ✓    | N/A        |
| Serialize | ✓    | ✓    | ✓    | N/A        |
| Round-trip| ✓    | ✓    | ✓    | ✓          |
| Normalize | N/A  | N/A  | N/A  | ✓          |
| Denormalize| N/A | N/A  | N/A  | ✓          |

### Existing Test Updates

The following existing test files need updates:

1. **`tests/test_lattice_examples.py`**
   - Add TOON compilation tests
   - Add round-trip validation
   - Add token comparison

2. **`tests/core/test_compile_lattice.py`**
   - Add TOON output option
   - Test normalized output
   - Validate JSON hedge output

3. **`tests/conftest.py`**
   - Add compiler fixtures
   - Add TOON test utilities

---

## Risk Mitigations

### Risk 1: TOON Library Unavailable

**Mitigation:** JSON-first mode flag
```python
config = CompilerConfig(json_first_mode=True)  # Bypass TOON entirely
```

### Risk 2: Round-Trip Data Loss

**Mitigation:** Mandatory validation
```python
config = CompilerConfig(validate_roundtrip=True)  # Fail if not lossless
```

### Risk 3: LLM Unfamiliarity with TOON

**Mitigation:** Include format examples in prompts
```python
TOON_PROMPT = """
Data is provided in TOON format. Example:
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user
"""
```

### Risk 4: Normalization Breaks Semantics

**Mitigation:** Denormalization tests
```python
def test_normalize_denormalize_equivalence():
    original = load_yaml("agent.yaml")
    normalized = normalizer.normalize(original)
    restored = normalizer.denormalize(normalized)
    assert original == restored
```

### Risk 5: Token Tracking Inaccuracy

**Mitigation:** Use official tokenizers
```python
# Use tiktoken with same encoding as target model
tracker = TokenTracker(tokenizer="cl100k_base")  # GPT-4/Claude
```

---

## File Structure

### New Files to Create

```
src/lattice_lock/
├── compiler/
│   ├── __init__.py              # Module exports
│   ├── core.py                  # LatticeCompiler class
│   ├── formats.py               # Format detection utilities
│   ├── normalizer.py            # Normalization strategies
│   ├── token_tracker.py         # Token counting/costs
│   └── schemas.py               # Pydantic schemas for compiler
│
├── cli/commands/
│   └── convert.py               # New convert command

tests/
├── compiler/
│   ├── __init__.py
│   ├── test_core.py             # Core compiler tests
│   ├── test_formats.py          # Format detection tests
│   ├── test_normalizer.py       # Normalization tests
│   ├── test_token_tracker.py    # Token tracking tests
│   ├── test_roundtrip.py        # Round-trip validation
│   ├── integration/
│   │   ├── test_cli.py          # CLI integration tests
│   │   └── test_batch.py        # Batch compilation tests
│   └── fixtures/
│       ├── sample_agent.yaml
│       ├── sample_schema.yaml
│       └── sample_models.yaml

docs/
├── guides/
│   └── toon-migration.md        # Migration guide
└── reference/
    └── compiler-api.md          # API reference
```

### Files to Update

```
pyproject.toml                   # Add toon-format, tiktoken deps
src/lattice_lock/cli/__main__.py # Register convert command
src/lattice_lock/cli/commands/compile.py  # Add format options
tests/test_lattice_examples.py   # Add TOON tests
tests/conftest.py                # Add compiler fixtures
```

---

## Dependencies

### New Dependencies

```toml
# pyproject.toml additions

[project.dependencies]
# ... existing deps ...

[project.optional-dependencies]
toon = [
    "toon-format>=0.9.0",        # TOON encoding/decoding
    "tiktoken>=0.5.0",           # Token counting
]

dev = [
    # ... existing dev deps ...
    "toon-format>=0.9.0",
    "tiktoken>=0.5.0",
]
```

### Dependency Notes

1. **toon-format** (toon-python)
   - PyPI: `pip install toon-format` (when published)
   - GitHub: `pip install git+https://github.com/toon-format/toon-python.git`
   - Status: Beta (v0.9.x)

2. **tiktoken**
   - PyPI: `pip install tiktoken`
   - Used for: Token counting
   - Status: Stable

---

## Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Token Savings | ≥70% | Compare YAML vs TOON tokens |
| Round-trip Fidelity | 100% | All configs round-trip losslessly |
| Compilation Speed | <1s per file | Time to compile single config |
| Test Coverage | ≥90% | Coverage of compiler module |
| CI/CD Integration | Pass | All PR checks pass |

### Qualitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Developer Experience | Positive | Team feedback |
| Documentation Quality | Complete | All features documented |
| Error Messages | Helpful | Clear, actionable errors |
| Fallback Reliability | Seamless | JSON hedge works perfectly |

---

## Appendix A: TOON Format Reference

### Basic Syntax

```
# Simple object
name: Alice
age: 30

# Primitive array
tags[3]: python,yaml,toon

# Tabular array (uniform objects)
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user

# Nested object
user:
  name: Alice
  email: alice@example.com
```

### Key Features

1. **Array Length Markers**: `[N]` declares array length
2. **Field Headers**: `{field1,field2}` declares schema
3. **Inline Arrays**: `[N]: value1,value2`
4. **Tabular Data**: Rows are comma-separated values
5. **Indentation**: YAML-like nesting

### TOON vs YAML Comparison

| Feature | YAML | TOON |
|---------|------|------|
| Key repetition | Every item | Once in header |
| Array length | Implicit | Explicit `[N]` |
| Validation markers | None | Length + fields |
| Token efficiency | Baseline | 30-60% savings |
| Human editing | Excellent | Good |
| LLM familiarity | High | Low (new format) |

---

## Appendix B: Quick Reference

### Compiler Config Options

```python
CompilerConfig(
    mode="standard",           # standard, normalized, minified, pretty
    normalize_for_toon=True,   # Enable TOON optimization
    include_metadata=True,     # Add _meta block
    validate_roundtrip=True,   # Verify lossless conversion
    fallback_to_json=True,     # Use JSON if TOON fails
    json_first_mode=False,     # Emergency hedge flag
    indent=2,                  # Indentation for pretty output
    toon_delimiter=",",        # Delimiter (comma, tab, pipe)
    track_tokens=True,         # Enable token tracking
)
```

### CLI Quick Reference

```bash
# Compile
lattice compile config.yaml --format toon
lattice compile --all --format toon

# Convert
lattice convert input.yaml --to toon
lattice convert input.toon --to json

# Analyze
lattice compile config.yaml --stats
lattice compile config.yaml --compare

# Validate
lattice compile config.yaml --validate-roundtrip
```

---

## Appendix C: Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | TBD | Initial release |

---

*Document Version: 1.0.0*
*Last Updated: 2025-01-01*
*Author: Lattice Lock Team*
