---
title: "Orchestrator Capabilities Contract"
type: design
status: stable
categories: [Architecture, Design]
sub_categories: [Orchestrator]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [cap-contract-001]
tags: [design, contract, capabilities]
author: Gemini Antimatter
---

# Orchestrator Capabilities Contract Design

**Task ID:** 6.1.1
**Author:** Gemini Antimatter (Design Doc)
**Phase:** 6.1 - Breaking Issues / Orchestrator Contract Hardening
**Status:** Design Complete
**Date:** 2024-12-10

---

## Executive Summary

The CLI (`scripts/orchestrator_cli.py`) references several attributes on `ModelCapabilities` that do not exist in the current type definition (`src/lattice_lock_orchestrator/types.py`), causing `AttributeError` at runtime. This document defines the complete contract for `ModelCapabilities` and provides a migration strategy.

---

## 1. Contract Definition

### 1.1 Current State Analysis

**Existing `ModelCapabilities` fields (types.py:27-44):**
| Field | Type | Required |
|-------|------|----------|
| `name` | `str` | ✓ |
| `api_name` | `str` | ✓ |
| `provider` | `ModelProvider` | ✓ |
| `context_window` | `int` | ✓ |
| `input_cost` | `float` | ✓ |
| `output_cost` | `float` | ✓ |
| `reasoning_score` | `float` | ✓ |
| `coding_score` | `float` | ✓ |
| `speed_rating` | `float` | ✓ |
| `supports_vision` | `bool` | Optional (default: False) |
| `supports_function_calling` | `bool` | Optional (default: False) |

**CLI references non-existent attributes:**
| Location | Attribute | Current Status |
|----------|-----------|----------------|
| Line 87 | `model.supports_reasoning` | ❌ Does not exist |
| Line 88 | `model.code_specialized` | ❌ Does not exist |
| Lines 95, 150 | `model.task_scores` | ❌ Does not exist |
| Line 277 | `TaskType.VISION` | ❌ Not in enum |
| Line 146 | `requirements.requires_vision` | ❌ Should be `require_vision` |
| Line 148 | `requirements.requires_reasoning` | ❌ Does not exist |

### 1.2 Complete Contract Definition

```python
@dataclass
class ModelCapabilities:
    """Defines the capabilities and costs of a specific model."""

    # === REQUIRED FIELDS ===
    name: str                      # Human-readable name
    api_name: str                  # API identifier for requests
    provider: ModelProvider        # Provider enum
    context_window: int            # Max tokens
    input_cost: float              # Per 1M tokens
    output_cost: float             # Per 1M tokens
    reasoning_score: float         # 0-100 scale
    coding_score: float            # 0-100 scale
    speed_rating: float            # 0-10 scale

    # === OPTIONAL FIELDS (with defaults) ===
    supports_vision: bool = False
    supports_function_calling: bool = False

    # === NEW DERIVED PROPERTIES ===
    @property
    def supports_reasoning(self) -> bool:
        """Model is strong at reasoning tasks (score >= 85)."""
        return self.reasoning_score >= 85.0

    @property
    def code_specialized(self) -> bool:
        """Model is specialized for code tasks (score >= 85)."""
        return self.coding_score >= 85.0

    @property
    def task_scores(self) -> Dict[TaskType, float]:
        """Derived task scores based on capability scores."""
        return {
            TaskType.CODE_GENERATION: self.coding_score / 100,
            TaskType.DEBUGGING: (self.coding_score * 0.6 + self.reasoning_score * 0.4) / 100,
            TaskType.ARCHITECTURAL_DESIGN: (self.reasoning_score * 0.7 + self.coding_score * 0.3) / 100,
            TaskType.DOCUMENTATION: self.reasoning_score * 0.8 / 100,
            TaskType.TESTING: (self.coding_score * 0.5 + self.reasoning_score * 0.5) / 100,
            TaskType.DATA_ANALYSIS: self.reasoning_score / 100,
            TaskType.GENERAL: (self.reasoning_score + self.coding_score) / 200,
            TaskType.REASONING: self.reasoning_score / 100,
            TaskType.VISION: 1.0 if self.supports_vision else 0.0,
        }

    @property
    def blended_cost(self) -> float:
        """Average cost per 1M tokens (assuming 3:1 input:output ratio)."""
        return (self.input_cost * 3 + self.output_cost) / 4
```

---

## 2. Field Semantics

### 2.1 Recommendation: Derived Properties over Explicit Booleans

**Decision: Use derived properties**

**Rationale:**
1. **Single Source of Truth**: `reasoning_score` and `coding_score` already capture the numeric capability. Explicit booleans would be redundant and could drift out of sync.
2. **Flexible Thresholds**: Using properties allows threshold adjustment without updating every model definition.
3. **Backwards Compatibility**: Properties add attributes without breaking existing model instantiations.
4. **No Registry Changes**: All 63+ models in the registry remain valid with zero modifications.

**Threshold Definitions:**
- `supports_reasoning`: `reasoning_score >= 85.0` (top-tier reasoning)
- `code_specialized`: `coding_score >= 85.0` (top-tier coding)

### 2.2 task_scores Implementation

**Decision: Derived at runtime via property**

**Rationale:**
1. **Consistency**: Scores are computed uniformly across all models using the same formula.
2. **Maintainability**: Formula updates propagate automatically to all models.
3. **No Storage Overhead**: No additional data to maintain in model definitions.
4. **Extensibility**: New task types can be added to the formula without touching registry.

**Formula Design:**
```python
TaskType.CODE_GENERATION    → coding_score / 100
TaskType.DEBUGGING          → coding_score * 0.6 + reasoning_score * 0.4
TaskType.ARCHITECTURAL_DESIGN → reasoning_score * 0.7 + coding_score * 0.3
TaskType.DOCUMENTATION      → reasoning_score * 0.8
TaskType.TESTING            → coding_score * 0.5 + reasoning_score * 0.5
TaskType.DATA_ANALYSIS      → reasoning_score
TaskType.GENERAL            → (reasoning_score + coding_score) / 2
TaskType.REASONING          → reasoning_score
TaskType.VISION             → 1.0 if supports_vision else 0.0
```

---

## 3. TaskType Enum Updates

### 3.1 Decision: Add VISION to TaskType

**Recommendation: YES - Add `TaskType.VISION`**

**Rationale:**
1. **CLI Reference**: Line 277 references `TaskType.VISION` for task detection tests.
2. **Semantic Completeness**: Vision tasks are a distinct category (image analysis, OCR, visual QA).
3. **Model Differentiation**: Many models support vision (GPT-4o, Gemini, Claude 3.5), making routing decisions meaningful.
4. **Future-Proofing**: Multimodal capabilities are increasingly important.

**Semantics:**
- `TaskType.VISION`: Tasks requiring image/visual input processing
- Detection triggers: "image", "picture", "photo", "visual", "screenshot", "diagram", "analyze this image"

### 3.2 Updated TaskType Enum

```python
class TaskType(Enum):
    """Categorizes the nature of the request to optimize model selection."""
    CODE_GENERATION = auto()
    DEBUGGING = auto()
    ARCHITECTURAL_DESIGN = auto()
    DOCUMENTATION = auto()
    TESTING = auto()
    DATA_ANALYSIS = auto()
    GENERAL = auto()
    REASONING = auto()
    VISION = auto()  # NEW: Image/visual processing tasks
```

### 3.3 Other Missing Task Types (Not Adding Now)

Evaluated but deferred:
- `CHAT` / `CONVERSATION`: Covered by GENERAL
- `SUMMARIZATION`: Covered by DOCUMENTATION
- `TRANSLATION`: Could be added in future phase
- `CREATIVE_WRITING`: Could be added in future phase

---

## 4. Migration Strategy

### 4.1 Safe Defaults (Backwards Compatibility)

All new attributes are **derived properties**, not stored fields. This means:

- ✅ Zero changes required to existing `ModelCapabilities` instantiations
- ✅ Zero changes required to registry model definitions
- ✅ All existing tests continue to pass
- ✅ Serialization/deserialization unchanged

### 4.2 CLI Fix Requirements

| File | Line | Current | Fix |
|------|------|---------|-----|
| `orchestrator_cli.py` | 146 | `requirements.requires_vision` | `requirements.require_vision` |
| `orchestrator_cli.py` | 148 | `requirements.requires_reasoning` | Remove or derive from task_type |

### 4.3 TaskRequirements Update

Add optional field for reasoning requirement:

```python
@dataclass
class TaskRequirements:
    """Defines the requirements for a specific task."""
    task_type: TaskType
    min_context: int = 4000
    max_cost: Optional[float] = None
    min_reasoning: float = 0.0
    min_coding: float = 0.0
    priority: str = "balanced"
    require_vision: bool = False
    require_functions: bool = False
    require_reasoning: bool = False  # NEW: Explicit reasoning requirement
```

### 4.4 Validation

Add runtime validation to ensure contract compliance:

```python
def validate_model_capabilities(model: ModelCapabilities) -> List[str]:
    """Validate model has all required attributes."""
    errors = []

    # Numeric range validation
    if not 0 <= model.reasoning_score <= 100:
        errors.append(f"reasoning_score must be 0-100, got {model.reasoning_score}")
    if not 0 <= model.coding_score <= 100:
        errors.append(f"coding_score must be 0-100, got {model.coding_score}")
    if not 0 <= model.speed_rating <= 10:
        errors.append(f"speed_rating must be 0-10, got {model.speed_rating}")
    if model.context_window <= 0:
        errors.append(f"context_window must be positive, got {model.context_window}")
    if model.input_cost < 0:
        errors.append(f"input_cost cannot be negative, got {model.input_cost}")
    if model.output_cost < 0:
        errors.append(f"output_cost cannot be negative, got {model.output_cost}")

    return errors
```

---

## 5. Implementation Tasks for Devin AI

### Task 6.1.2: Align Model Capabilities with Contract

**Priority:** Critical (Blocking)

#### 5.1 Update types.py

**File:** `src/lattice_lock_orchestrator/types.py`

1. Add `VISION = auto()` to `TaskType` enum (after line 14)

2. Add derived properties to `ModelCapabilities` class (after line 44):
   ```python
   @property
   def supports_reasoning(self) -> bool:
       """Model is strong at reasoning tasks (score >= 85)."""
       return self.reasoning_score >= 85.0

   @property
   def code_specialized(self) -> bool:
       """Model is specialized for code tasks (score >= 85)."""
       return self.coding_score >= 85.0

   @property
   def task_scores(self) -> Dict["TaskType", float]:
       """Derived task scores based on capability scores."""
       return {
           TaskType.CODE_GENERATION: self.coding_score / 100,
           TaskType.DEBUGGING: (self.coding_score * 0.6 + self.reasoning_score * 0.4) / 100,
           TaskType.ARCHITECTURAL_DESIGN: (self.reasoning_score * 0.7 + self.coding_score * 0.3) / 100,
           TaskType.DOCUMENTATION: self.reasoning_score * 0.8 / 100,
           TaskType.TESTING: (self.coding_score * 0.5 + self.reasoning_score * 0.5) / 100,
           TaskType.DATA_ANALYSIS: self.reasoning_score / 100,
           TaskType.GENERAL: (self.reasoning_score + self.coding_score) / 200,
           TaskType.REASONING: self.reasoning_score / 100,
           TaskType.VISION: 1.0 if self.supports_vision else 0.0,
       }
   ```

3. Add `require_reasoning: bool = False` to `TaskRequirements` dataclass (after line 56)

#### 5.2 Fix CLI References

**File:** `scripts/orchestrator_cli.py`

1. Line 146: Change `requirements.requires_vision` → `requirements.require_vision`
2. Line 148: Change `requirements.requires_reasoning` → `requirements.require_reasoning`

#### 5.3 Update Task Analyzer

**File:** `src/lattice_lock_orchestrator/analyzer.py` (or equivalent)

1. Add detection for `TaskType.VISION`:
   - Keywords: "image", "picture", "photo", "visual", "screenshot", "diagram", "analyze this image"
   - Set `require_vision = True` when VISION task detected

#### 5.4 Write Tests

**File:** `tests/test_model_capabilities_contract.py` (new file)

```python
import pytest
from lattice_lock_orchestrator.types import ModelCapabilities, ModelProvider, TaskType

def test_supports_reasoning_derived():
    """Test supports_reasoning is derived from reasoning_score."""
    model = ModelCapabilities(
        name="Test", api_name="test", provider=ModelProvider.OPENAI,
        context_window=8000, input_cost=1.0, output_cost=2.0,
        reasoning_score=90.0, coding_score=50.0, speed_rating=5.0
    )
    assert model.supports_reasoning is True

    model2 = ModelCapabilities(
        name="Test2", api_name="test2", provider=ModelProvider.OPENAI,
        context_window=8000, input_cost=1.0, output_cost=2.0,
        reasoning_score=70.0, coding_score=50.0, speed_rating=5.0
    )
    assert model2.supports_reasoning is False

def test_code_specialized_derived():
    """Test code_specialized is derived from coding_score."""
    model = ModelCapabilities(
        name="Test", api_name="test", provider=ModelProvider.OPENAI,
        context_window=8000, input_cost=1.0, output_cost=2.0,
        reasoning_score=50.0, coding_score=90.0, speed_rating=5.0
    )
    assert model.code_specialized is True

def test_task_scores_computed():
    """Test task_scores property returns correct dict."""
    model = ModelCapabilities(
        name="Test", api_name="test", provider=ModelProvider.OPENAI,
        context_window=8000, input_cost=1.0, output_cost=2.0,
        reasoning_score=80.0, coding_score=90.0, speed_rating=5.0,
        supports_vision=True
    )
    scores = model.task_scores

    assert TaskType.CODE_GENERATION in scores
    assert TaskType.VISION in scores
    assert scores[TaskType.CODE_GENERATION] == 0.9  # 90/100
    assert scores[TaskType.VISION] == 1.0  # supports_vision=True

def test_task_type_vision_exists():
    """Test VISION is in TaskType enum."""
    assert hasattr(TaskType, 'VISION')
    assert TaskType.VISION.value is not None
```

#### 5.5 Validation

After implementation:
1. Run `pytest tests/test_model_capabilities_contract.py`
2. Run `python scripts/orchestrator_cli.py list --verbose` (should not crash)
3. Run `python scripts/orchestrator_cli.py test` (should pass all tests)

---

## 6. Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Boolean capabilities | Derived properties | Single source of truth, no registry changes |
| task_scores | Computed property | Consistency, maintainability |
| TaskType.VISION | Add to enum | CLI reference, semantic completeness |
| Migration | Property-based | Zero changes to existing models |

**Files to Modify:**
1. `src/lattice_lock_orchestrator/types.py` - Add properties and VISION
2. `scripts/orchestrator_cli.py` - Fix attribute references
3. `src/lattice_lock_orchestrator/analyzer.py` - Add VISION detection
4. `tests/test_model_capabilities_contract.py` - New test file

**Estimated Implementation Time:** 2-3 hours
