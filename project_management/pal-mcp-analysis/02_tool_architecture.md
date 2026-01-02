# Module 2: Tool/Feature Architecture Comparison

## Executive Summary

Lattice Lock uses an **integrated module architecture** with deep coupling between components, while PAL MCP employs a **flat, self-contained tool pattern**. Both approaches serve different purposes: Lattice Lock's tight integration supports governance workflows, while PAL MCP's loose coupling enables rapid tool addition and runtime toggling.

---

## Core Component Mapping

### Lattice Lock → PAL MCP Feature Equivalence

| Lattice Lock | PAL MCP Equivalent | Notes |
|--------------|-------------------|-------|
| `ModelOrchestrator` | `chat.py` + provider routing | Lattice Lock has richer selection logic |
| `ConsensusEngine` | `consensus.py` | Similar voting; PAL adds stance steering |
| `ConsensusOrchestrator` | `consensus.py` synthesis | Nearly identical pattern |
| `ChainOrchestrator` | `planner.py` | Lattice Lock is more structured |
| `Sheriff` | `codereview.py` (partial) | Sheriff is static; codereview is dynamic |
| `Gauntlet` | `precommit.py` (partial) | Gauntlet generates tests; precommit runs them |
| `lattice ask` CLI | `chat` tool | Direct equivalent |
| `lattice chain` CLI | N/A | PAL lacks structured pipelines |
| N/A | `clink` (CLI bridge) | Lattice Lock lacks agent delegation |
| N/A | `thinkdeep` | Extended reasoning mode |

---

## Lattice Lock Tool Architecture

### Core Modules

```
src/lattice_lock/
├── orchestrator/           # Model routing & selection
│   ├── core.py             # ModelOrchestrator (284 lines)
│   │   ├── route_request() # Main entry point
│   │   ├── _handle_fallback() # Fallback logic
│   │   └── get_available_providers()
│   ├── consensus/
│   │   ├── ConsensusEngine     # Voting-based consensus
│   │   └── ConsensusOrchestrator # Synthesis consensus
│   ├── chain.py            # ChainOrchestrator, Pipeline, PipelineStep
│   ├── analysis/           # TaskAnalyzer
│   ├── scoring/            # ModelScorer
│   ├── selection/          # ModelSelector
│   ├── providers/          # 11 provider clients
│   └── registry.py         # ModelRegistry
│
├── sheriff/                # Static analysis
│   ├── sheriff.py          # run_sheriff(), validate_file()
│   ├── ast_visitor.py      # AST traversal
│   ├── rules.py            # Violation definitions
│   ├── config.py           # SheriffConfig
│   ├── cache.py            # Result caching
│   └── formatters.py       # Output formatting
│
├── gauntlet/               # Runtime testing
│   ├── generator.py        # GauntletGenerator
│   ├── parser.py           # LatticeParser
│   ├── validator.py        # Runtime validation
│   └── templates/          # Test templates
│
├── validator/              # Rule validation
│   └── [validation rules and helpers]
│
└── cli/commands/           # 13 CLI commands
    ├── ask.py              # lattice ask
    ├── chain.py            # lattice chain
    ├── compile.py          # lattice compile
    ├── doctor.py           # lattice doctor
    ├── gauntlet.py         # lattice test/gauntlet
    ├── handoff.py          # Agent handoff
    ├── sheriff.py          # lattice validate
    ├── validate.py         # Rule validation
    ├── admin.py            # Admin commands
    ├── feedback.py         # User feedback
    ├── init.py             # Project init
    └── rollback.py         # Rollback changes
```

### Key Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `ModelOrchestrator` | 284 | Central routing with fallback |
| `ConsensusEngine` | 60 | Vote-based consensus (approve/reject) |
| `ConsensusOrchestrator` | 90 | Multi-model synthesis |
| `ChainOrchestrator` | 96 | Pipeline execution |
| `GauntletGenerator` | 102 | Pytest test generation |
| `run_sheriff` | 284 | Static analysis orchestration |

---

## PAL MCP Tool Pattern

### Flat Tool Structure
```
tools/
├── chat.py           # Basic chat with any model
├── thinkdeep.py      # Extended reasoning (thinking modes)
├── planner.py        # Project planning workflow
├── consensus.py      # Multi-model debate w/ stance steering
├── codereview.py     # Code review workflow (phased)
├── precommit.py      # Pre-commit validation
├── debug.py          # Debugging workflow
├── clink.py          # CLI-to-CLI bridge (spawn subagents)
└── apilookup.py      # Knowledge freshness via web search
```

### Key PAL MCP Patterns Not in Lattice Lock

#### 1. DISABLED_TOOLS Pattern
```bash
DISABLED_TOOLS=analyze,refactor,testgen,secaudit,docgen,tracer
```
- Runtime feature toggling via environment
- No code changes needed to disable features

#### 2. continuation_id Threading
```python
# Every tool response includes:
{
    "continuation_id": "abc123",
    "step_number": 2,
    "total_steps": 5,
    "next_step_required": true
}
```
- Cross-tool conversation memory
- Context revival after CLI reset

#### 3. Confidence Levels
```python
confidence_levels = [
    "exploring",     # Initial research
    "low",           # Uncertain
    "medium",        # Reasonable confidence
    "high",          # Strong confidence
    "very_high",     # Very confident
    "almost_certain", # Near certain
    "certain"        # Definitive
]
```
- Self-assessment prevents rushed analysis
- Forces multi-step workflows

#### 4. Stance Steering (Consensus)
```python
consensus(
    topic="Redis vs Memcached",
    models=["gemini-pro", "gpt-5", "o3"],
    stance_steering={
        "gemini-pro": "advocate_for_redis",
        "gpt-5": "advocate_for_memcached",
        "o3": "neutral_arbiter"
    }
)
```
- Forces models to argue specific positions
- Produces richer debate

#### 5. CLI Bridge (clink)
```bash
# From Claude, spawn Gemini as subagent
clink with gemini planner to draft migration strategy
```
- Agent-to-agent delegation
- Context isolation per subagent

---

## Comparison: Similar Features

### Consensus Engines

| Aspect | Lattice Lock ConsensusEngine | PAL MCP consensus |
|--------|------------------------------|-------------------|
| Voting | ✅ `execute_voting()` | ✅ Similar |
| Synthesis | ✅ `ConsensusOrchestrator` | ✅ Similar |
| Parallelism | ✅ `asyncio.gather()` | ✅ Similar |
| Stance steering | ❌ Not implemented | ✅ Forces positions |
| Confidence output | ❌ Basic ratio only | ✅ Named levels |

**Recommendation:** Add stance steering to ConsensusEngine.

### Multi-Step Workflows

| Aspect | Lattice Lock ChainOrchestrator | PAL MCP workflows |
|--------|--------------------------------|-------------------|
| YAML definition | ✅ `from_yaml()` | ❌ Code-defined |
| Template rendering | ✅ `{{variable}}` | ❌ Manual |
| Step tracking | ⚠️ Basic logging | ✅ step_number/total_steps |
| Continuity | ❌ Session-only | ✅ continuation_id |

**Recommendation:** Add `step_number`, `total_steps` to ChainOrchestrator output.

### Static Analysis

| Aspect | Lattice Lock Sheriff | PAL MCP codereview |
|--------|---------------------|-------------------|
| Type | Static AST analysis | LLM-based review |
| Speed | ✅ Fast (no API calls) | ❌ Slow (API calls) |
| Custom rules | ✅ lattice.yaml | ⚠️ Prompt-based |
| Phased workflow | ❌ Single pass | ✅ Multi-phase |
| Auto-fix | ⚠️ `--fix` flag exists | ✅ Suggest fixes |
**Questions:**
1. What is the user value created by implementing an LLM-based review alongside the existing Static AST Analysis?
	1. Can the LLM-based review improve the Static AST analysis over time?
	2. What capabilities does each of these options provide the framework?
	3. What is 
**Recommendation:** 
2. Sheriff could add phased analysis (quick scan → deep analysis).

---

## Gap Analysis: Missing Patterns

### P0 - High Value, Low Effort

| Pattern | Status | Recommendation |
|---------|--------|----------------|
| `DISABLED_TOOLS` env var | ❌ Missing | Add `DISABLED_FEATURES` for Sheriff/Gauntlet |
| Confidence levels | ❌ Missing | Add to Sheriff violations, Consensus output |
| Step tracking | ⚠️ Partial | Add `step_number`, `total_steps` to pipeline results |

### P1 - High Value, Medium Effort

| Pattern | Status | Recommendation |
|---------|--------|----------------|
| `continuation_id` | ❌ Missing | Add conversation threading to orchestrator |
| Stance steering | ❌ Missing | Add to ConsensusEngine |
| Phased workflows | ⚠️ Partial | Add phases to Sheriff (quick → deep) |

### P2 - Consider for Future

| Pattern | Status | Notes |
|---------|--------|-------|
| CLI bridge (clink) | ❌ Missing | Different use case; Lattice Lock is framework, not CLI |
| thinkdeep modes | ❌ Missing | Could add reasoning depth to scorer |
| apilookup | ❌ Missing | Knowledge freshness for orchestrator |

---

## Feature Enable/Disable Pattern

### Current State

Lattice Lock lacks runtime feature toggling. All features are always enabled.

### Proposed Implementation

```bash
# .env
LATTICE_DISABLED_FEATURES=gauntlet,feedback,rollback
```

```python
# config.py
DISABLED_FEATURES = os.getenv("LATTICE_DISABLED_FEATURES", "").split(",")

def is_feature_enabled(feature: str) -> bool:
    return feature not in DISABLED_FEATURES
```

**Benefits:**
- Lightweight deployments (disable unused features)
- Gradual rollouts
- Debugging (isolate feature issues)

---

## CLI Command Comparison

### Lattice Lock CLI (13 commands)

| Command | Purpose | Phase |
|---------|---------|-------|
| `lattice ask` | Single model query | Execution |
| `lattice chain` | Multi-step pipeline | Execution |
| `lattice compile` | Compile lattice.yaml | Build |
| `lattice validate` | Static analysis (Sheriff) | Validation |
| `lattice test` | Runtime tests (Gauntlet) | Validation |
| `lattice doctor` | System diagnostics | Debug |
| `lattice init` | Project scaffolding | Setup |
| `lattice admin` | Admin operations | Admin |
| `lattice feedback` | User feedback | Feedback |
| `lattice handoff` | Agent handoff | Orchestration |
| `lattice rollback` | Undo changes | Recovery |

### PAL MCP Tools (9 tools)

| Tool | Purpose | Equivalent in Lattice Lock |
|------|---------|---------------------------|
| `chat` | Basic chat | `lattice ask` |
| `thinkdeep` | Extended reasoning | ❌ Not available |
| `planner` | Project planning | `lattice chain` (partial) |
| `consensus` | Multi-model debate | `ConsensusEngine` (internal) |
| `codereview` | Code review | `lattice validate` (static only) |
| `precommit` | Pre-commit checks | `lattice validate` + `lattice test` |
| `debug` | Debugging workflow | `lattice doctor` |
| `clink` | CLI bridge | ❌ Not available |
| `apilookup` | Knowledge freshness | ❌ Not available |

---

## Recommendations

### Adopt from PAL MCP

1. **Confidence Levels** - Add to Sheriff and Consensus output
2. **Step Tracking** - Add `step_number`, `total_steps` to pipeline results
3. **Feature Flags** - Add `LATTICE_DISABLED_FEATURES` env var
4. **Stance Steering** - Add to ConsensusEngine
5. **continuation_id** - Add conversation threading (if multi-turn workflows needed)

### Preserve from Lattice Lock

1. **Static Analysis** - Sheriff's AST-based approach is faster than LLM review
2. **Test Generation** - Gauntlet's pytest generation is unique
3. **YAML Pipelines** - ChainOrchestrator's declarative approach is cleaner
4. **Deep Module Hierarchy** - Suits governance domain

### Skip from PAL MCP

1. **clink (CLI bridge)** - Lattice Lock is a framework, not a CLI-spawning tool
2. **Flat tool structure** - Deep hierarchy serves governance better
3. **LLM-based code review** - Sheriff's static analysis is more reliable

---

*Module 2 completed. Next: Module 3 - Configuration & Environment Management*
