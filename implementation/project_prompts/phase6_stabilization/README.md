# Phase 6: Core Stabilization & Governance

**Purpose:** Fix critical issues identified in the codebase review and complete missing core functionality.

**Created:** December 2025
**Status:** Pending

---

## Overview

This phase addresses issues identified during a comprehensive code review:
- **Tier 0 (6.1):** Breaking issues that cause runtime errors
- **Tier 1 (6.2):** Missing governance core loop
- **Tier 2 (6.3):** Incomplete orchestrator features
- **Tier 3 (6.4):** Engineering framework polish

---

## Task Summary

### Phase 6.1 - Breaking Issues / Orchestrator Contract Hardening

| Task ID | Title | Tool | Status |
|---------|-------|------|--------|
| 6.1.1 | Orchestrator Capabilities Contract Design | Gemini Antimatter | Pending |
| 6.1.2 | Align ModelCapabilities and CLI Implementation | Devin AI | Pending |
| 6.1.3 | Provider Client and Fallback Strategy Design | Gemini Antimatter | Pending |
| 6.1.4 | Provider Client Hardening & Bedrock Behavior | Devin AI | Pending |

**Issues Addressed:**
- `AttributeError` when CLI accesses `model.supports_reasoning`, `model.code_specialized`, `model.task_scores`
- `TaskType.VISION` not defined in enum
- `BedrockClient` raises `NotImplementedError`

### Phase 6.2 - Governance Core Loop

| Task ID | Title | Tool | Status |
|---------|-------|------|--------|
| 6.2.1 | Governance Core & lattice.yaml Specification | Gemini Antimatter | Pending |
| 6.2.2 | lattice.yaml Examples and Test Fixtures | Devin AI | Pending |
| 6.2.3 | compile_lattice Python API & CLI Entry | Devin AI | Pending |
| 6.2.4 | End-to-End Governance Core Documentation | Gemini Antimatter | Pending |

**Issues Addressed:**
- No canonical `lattice.yaml` example exists
- No `compile_lattice` entrypoint
- No end-to-end documentation of governance workflow

### Phase 6.3 - Orchestrator Feature Completeness

| Task ID | Title | Tool | Status |
|---------|-------|------|--------|
| 6.3.1 | Model Registry Source-of-Truth Design | Gemini Antimatter | Pending |
| 6.3.2 | Configurable Registry Implementation | Devin AI | Pending |
| 6.3.3 | Cost & Telemetry Strategy Design | Gemini Antimatter | Pending |
| 6.3.4 | Cost Tracking Implementation | Devin AI | Pending |
| 6.3.5 | Multi-Model Consensus Strategy Design | Gemini Antimatter | Pending |
| 6.3.6 | Consensus Strategy Implementation | Devin AI | Pending |
| 6.3.7 | Task Analyzer v2 Design | Gemini Antimatter | Pending |
| 6.3.8 | Task Analyzer v2 Implementation | Devin AI | Pending |

**Issues Addressed:**
- Model registry hardcoded (~10 models) vs documented 63 models
- Cost tracking not implemented (`show_cost_report()` returns "not yet implemented")
- Consensus patterns not implemented
- TaskAnalyzer uses simple keyword matching

### Phase 6.4 - Engineering Framework & Tooling

| Task ID | Title | Tool | Status |
|---------|-------|------|--------|
| 6.4.1 | Engineering Framework CLI UX Design | Gemini Antimatter | Pending |
| 6.4.2 | Core CLI Wrapper Implementation | Devin AI | Pending |
| 6.4.3 | CI Templates & Workflows Design | Gemini Antimatter | Pending |
| 6.4.4 | CI Templates & Dependency Hardening | Devin AI | Pending |

**Issues Addressed:**
- Missing unified CLI experience
- `pyproject.toml` missing dependencies (test collection fails)
- CI templates need updating

---

## Execution Order

### Global Order
1. **Phase 6.1** - Unblock the framework (runtime errors)
2. **Phase 6.2** - Make governance core loop real
3. **Phase 6.3** - Feature-complete the orchestrator (can parallel with 6.4)
4. **Phase 6.4** - Polish engineering experience

### Within Each Phase
1. **Gemini Antimatter** tasks first (design/specs)
2. **Devin AI** tasks second (implementation/tests)

### Dependency Graph

```
6.1.1 ──► 6.1.2
6.1.1 ──► 6.1.3 ──► 6.1.4

6.2.1 ──► 6.2.2 ──┬──► 6.2.4
         6.2.3 ──┘

6.3.1 ──► 6.3.2
6.3.3 ──► 6.3.4
6.3.5 ──► 6.3.6
6.3.7 ──► 6.3.8

6.4.1 ──► 6.4.2
6.4.3 ──► 6.4.4
```

---

## Tool Assignment

| Tool | Tasks |
|------|-------|
| **Gemini Antimatter** | 6.1.1, 6.1.3, 6.2.1, 6.2.4, 6.3.1, 6.3.3, 6.3.5, 6.3.7, 6.4.1, 6.4.3 |
| **Devin AI** | 6.1.2, 6.1.4, 6.2.2, 6.2.3, 6.3.2, 6.3.4, 6.3.6, 6.3.8, 6.4.2, 6.4.4 |

---

## Exit Criteria

**Phase 6.1 Complete When:**
- [ ] `orchestrator_cli.py list --verbose` runs without errors
- [ ] `orchestrator_cli.py analyze "prompt"` works for all task types
- [ ] No `NotImplementedError` during normal operation

**Phase 6.2 Complete When:**
- [ ] Canonical `lattice.yaml` examples exist
- [ ] `compile_lattice` function and CLI work
- [ ] End-to-end walkthrough documentation exists

**Phase 6.3 Complete When:**
- [ ] Model registry loads from YAML config
- [ ] Cost tracking works and `cost` command shows data
- [ ] Consensus command executes multi-model requests
- [ ] Task analyzer has >80% accuracy on test set

**Phase 6.4 Complete When:**
- [ ] `lattice-lock validate` runs all validations
- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `pytest --collect-only` has no import errors
- [ ] GitHub Actions CI passes
