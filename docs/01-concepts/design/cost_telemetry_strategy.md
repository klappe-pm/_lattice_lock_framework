---
title: "Cost & Telemetry Strategy"
type: design
status: draft
categories: [Architecture, Telemetry]
sub_categories: [Core]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [cost-telemetry-001]
aliases: [cost-tracking-design]
tags: [design, cost, telemetry]
author: Gemini Antimatter
---

# Cost & Telemetry Strategy Design

**Task ID:** 6.3.3
**Author:** Gemini Antimatter (Design Doc)
**Phase:** 6.3 - Orchestrator Feature Completeness
**Dependencies:** None (can run parallel with 6.3.1)
**Status:** Design Complete
**Date:** 2024-12-10

---

## Executive Summary

The framework advertises cost tracking but `show_cost_report()` returns "not yet implemented in v3.1". This document defines the complete cost tracking infrastructure including data models, storage strategy, API surface, and CLI integration.

---

## 1. Current State Analysis

### 1.1 What Exists

| Component | Location | Status |
|-----------|----------|--------|
| `ModelCapabilities.input_cost` | types.py:33 | Per 1M tokens, defined |
| `ModelCapabilities.output_cost` | types.py:34 | Per 1M tokens, defined |
| `ModelCapabilities.blended_cost` | types.py:42-44 | Property, computed |
| `APIResponse.usage` | types.py:77 | Dict with input_tokens, output_tokens |
| `show_cost_report()` | orchestrator_cli.py:207 | Stub, returns "not implemented" |

### 1.2 What's Missing

- **No storage**: Usage data is computed per-call but never persisted
- **No aggregation**: No session, model, or provider totals
- **No tracking class**: No `CostTracker` or equivalent
- **No integration**: `core.py` doesn't call any cost recording

### 1.3 Data Flow Gap

```
Current:  API Call → APIResponse.usage → [LOST]
Desired:  API Call → APIResponse.usage → CostTracker.record() → Storage → Reports
```

---

## 2. Cost Tracking Scope

### 2.1 Tracking Granularity

| Level | Description | Use Case |
|-------|-------------|----------|
| **Per-Call** | Each API request | Debugging, audit trail |
| **Per-Session** | Accumulated during runtime | Budget monitoring |
| **Per-Model** | Breakdown by model_id | Model comparison |
| **Per-Provider** | Breakdown by provider | Vendor cost analysis |
| **Per-Task-Type** | Breakdown by task classification | Workflow optimization |
| **Time-Based** | Daily, weekly, monthly aggregates | Budget planning |

### 2.2 Metrics to Track

```python
# Per-call metrics
- timestamp: When the call was made
- model_id: Which model was used
- provider: Which provider
- input_tokens: Tokens sent to model
- output_tokens: Tokens received from model
- cost: Calculated cost in USD
- latency_ms: Response time
- task_type: Classification of the request
- request_id: Unique identifier for correlation
- success: Whether call succeeded
```

---

## 3. Data Model

### 3.1 Core Types

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
import uuid

@dataclass
class UsageRecord:
    """Single API call usage record."""
    timestamp: datetime
    model_id: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency_ms: int
    task_type: str  # TaskType.value
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    success: bool = True
    error_message: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

@dataclass
class CostReport:
    """Aggregated cost report."""
    start_time: datetime
    end_time: datetime
    total_cost: float
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    by_model: Dict[str, float]
    by_provider: Dict[str, float]
    by_task_type: Dict[str, float]
    average_latency_ms: float
    success_rate: float

@dataclass
class SessionSummary:
    """Current session summary."""
    session_id: str
    start_time: datetime
    total_cost: float
    request_count: int
    models_used: List[str]
    providers_used: List[str]
```

### 3.2 Cost Calculation

```python
def calculate_cost(
    model: ModelCapabilities,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate cost for a single API call.

    Model costs are per 1M tokens, so:
    cost = (input_tokens * input_cost + output_tokens * output_cost) / 1_000_000
    """
    input_cost = (input_tokens * model.input_cost) / 1_000_000
    output_cost = (output_tokens * model.output_cost) / 1_000_000
    return input_cost + output_cost
```

---

## 4. Storage Strategy

### 4.1 Options Analysis

| Option | Pros | Cons | Persistence | Complexity |
|--------|------|------|-------------|------------|
| **In-Memory** | Fast, zero setup | Lost on restart | None | Low |
| **JSON File** | Human-readable, portable | Slow for large data, concurrent access issues | Per-session | Low |
| **SQLite** | ACID, queryable, single file | Requires schema management | Full | Medium |
| **PostgreSQL** | Scalable, full SQL | External dependency, setup overhead | Full | High |

### 4.2 Recommendation: Hybrid (In-Memory + SQLite)

**Rationale:**
1. **In-Memory**: Fast access for current session metrics (no I/O for hot path)
2. **SQLite**: Persistent storage for historical data (optional, enabled by config)
3. **Zero Config Default**: Works out-of-box with in-memory only
4. **Opt-in Persistence**: Enable SQLite via environment variable or config

**Configuration:**
```python
# Environment variables
LATTICE_COST_TRACKING = "memory"  # "memory", "sqlite", "disabled"
LATTICE_COST_DB_PATH = "~/.lattice_lock/costs.db"  # SQLite path
```

### 4.3 SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS usage_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    request_id TEXT UNIQUE NOT NULL,
    model_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cost REAL NOT NULL,
    latency_ms INTEGER NOT NULL,
    task_type TEXT NOT NULL,
    success INTEGER NOT NULL DEFAULT 1,
    error_message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usage_timestamp ON usage_records(timestamp);
CREATE INDEX idx_usage_session ON usage_records(session_id);
CREATE INDEX idx_usage_model ON usage_records(model_id);
CREATE INDEX idx_usage_provider ON usage_records(provider);
```

---

## 5. API Surface

### 5.1 CostTracker Class

```python
class CostTracker:
    """
    Tracks API usage costs with optional persistence.

    Usage:
        tracker = CostTracker()
        tracker.record_usage(response, model, task_type)
        print(f"Session cost: ${tracker.get_session_cost():.4f}")
    """

    def __init__(
        self,
        storage_mode: str = "memory",  # "memory", "sqlite", "disabled"
        db_path: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Initialize cost tracker with storage backend."""
        ...

    # === Recording ===

    def record_usage(
        self,
        response: APIResponse,
        model: ModelCapabilities,
        task_type: TaskType,
        request_id: Optional[str] = None
    ) -> UsageRecord:
        """Record usage from an API response. Returns the created record."""
        ...

    def record_manual(
        self,
        model_id: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        task_type: TaskType,
        latency_ms: int = 0
    ) -> UsageRecord:
        """Record usage manually (for external API calls)."""
        ...

    # === Session Queries ===

    def get_session_cost(self) -> float:
        """Get total cost for current session."""
        ...

    def get_session_summary(self) -> SessionSummary:
        """Get summary of current session."""
        ...

    def get_session_records(self) -> List[UsageRecord]:
        """Get all records for current session."""
        ...

    # === Aggregation Queries ===

    def get_cost_by_model(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Get cost breakdown by model."""
        ...

    def get_cost_by_provider(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Get cost breakdown by provider."""
        ...

    def get_cost_by_task_type(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Get cost breakdown by task type."""
        ...

    # === Reports ===

    def get_cost_report(
        self,
        start: datetime,
        end: datetime
    ) -> CostReport:
        """Generate comprehensive cost report for time range."""
        ...

    def get_daily_costs(
        self,
        days: int = 30
    ) -> Dict[str, float]:
        """Get daily cost totals for last N days."""
        ...

    # === Export ===

    def export_csv(
        self,
        path: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> int:
        """Export records to CSV. Returns number of records exported."""
        ...

    def export_json(
        self,
        path: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> int:
        """Export records to JSON. Returns number of records exported."""
        ...

    # === Management ===

    def clear_session(self) -> int:
        """Clear current session records. Returns count cleared."""
        ...

    def clear_all(self) -> int:
        """Clear all records (requires confirmation). Returns count cleared."""
        ...
```

### 5.2 Singleton Access

```python
# Global tracker instance
_tracker: Optional[CostTracker] = None

def get_cost_tracker() -> CostTracker:
    """Get or create the global cost tracker instance."""
    global _tracker
    if _tracker is None:
        storage_mode = os.getenv("LATTICE_COST_TRACKING", "memory")
        db_path = os.getenv("LATTICE_COST_DB_PATH", "~/.lattice_lock/costs.db")
        _tracker = CostTracker(storage_mode=storage_mode, db_path=db_path)
    return _tracker

def reset_cost_tracker() -> None:
    """Reset the global tracker (for testing)."""
    global _tracker
    _tracker = None
```

---

## 6. CLI Commands

### 6.1 Cost Command Structure

```bash
# Show current session cost
orchestrator_cli.py cost

# Show detailed breakdown
orchestrator_cli.py cost --detailed

# Show cost by model
orchestrator_cli.py cost --by-model

# Show cost by provider
orchestrator_cli.py cost --by-provider

# Show historical costs
orchestrator_cli.py cost --history 7d  # Last 7 days
orchestrator_cli.py cost --history 30d # Last 30 days

# Export to file
orchestrator_cli.py cost --export costs.csv
orchestrator_cli.py cost --export costs.json

# Clear session
orchestrator_cli.py cost --clear-session
```

### 6.2 CLI Output Examples

**Basic (`orchestrator_cli.py cost`):**
```
╭─────────────────── Session Cost Summary ───────────────────╮
│ Total Cost:      $0.1234                                   │
│ Requests:        42                                        │
│ Input Tokens:    15,230                                    │
│ Output Tokens:   8,450                                     │
│ Session Start:   2024-12-10 14:30:00                       │
╰────────────────────────────────────────────────────────────╯
```

**Detailed (`orchestrator_cli.py cost --detailed`):**
```
╭─────────────────── Cost Report ───────────────────╮
│ Session: abc123                                   │
│ Duration: 2h 15m                                  │
│ Total Cost: $0.1234                               │
╰───────────────────────────────────────────────────╯

By Model:
┌─────────────────────┬──────────┬──────────┬─────────┐
│ Model               │ Requests │ Tokens   │ Cost    │
├─────────────────────┼──────────┼──────────┼─────────┤
│ gpt-4o              │ 15       │ 12,500   │ $0.0875 │
│ claude-3-5-sonnet   │ 20       │ 8,200    │ $0.0328 │
│ gemini-2.5-flash    │ 7        │ 2,980    │ $0.0031 │
└─────────────────────┴──────────┴──────────┴─────────┘

By Provider:
┌─────────────────────┬──────────┬─────────┐
│ Provider            │ Requests │ Cost    │
├─────────────────────┼──────────┼─────────┤
│ openai              │ 15       │ $0.0875 │
│ anthropic           │ 20       │ $0.0328 │
│ google              │ 7        │ $0.0031 │
└─────────────────────┴──────────┴─────────┘
```

---

## 7. Integration Points

### 7.1 Core.py Integration

**Location:** `ModelOrchestrator._call_model()` (core.py:108-196)

**Integration Point:** After successful API call, before returning response

```python
async def _call_model(self, model: ModelCapabilities, prompt: str, **kwargs) -> APIResponse:
    """Call the specific model API"""
    client = self._get_client(model.provider.value)

    # ... existing code ...

    response = await client.chat_completion(...)

    # === NEW: Record usage ===
    if self.cost_tracker:
        self.cost_tracker.record_usage(
            response=response,
            model=model,
            task_type=kwargs.get('task_type', TaskType.GENERAL)
        )

    return response
```

**Constructor Update:**
```python
def __init__(self, guide_path: Optional[str] = None, enable_cost_tracking: bool = True):
    # ... existing init ...
    self.cost_tracker = get_cost_tracker() if enable_cost_tracking else None
```

### 7.2 API Response Token Extraction

**Current:** All clients return `usage` dict with `input_tokens` and `output_tokens`

**Mapping by Provider:**

| Provider | Response Path | Input Key | Output Key |
|----------|---------------|-----------|------------|
| OpenAI | `data['usage']` | `prompt_tokens` | `completion_tokens` |
| Anthropic | `data['usage']` | `input_tokens` | `output_tokens` |
| Google | `data['usageMetadata']` | `promptTokenCount` | `candidatesTokenCount` |
| xAI | `data['usage']` | `prompt_tokens` | `completion_tokens` |
| Ollama | `data['usage']` (if present) | `prompt_tokens` | `completion_tokens` |
| Azure | `data['usage']` | `prompt_tokens` | `completion_tokens` |

---

## 8. Unknown Cost Handling

### 8.1 Scenarios

| Scenario | Cause | Strategy |
|----------|-------|----------|
| Missing token count | Provider doesn't return usage | Estimate from prompt length |
| Unknown model cost | Model not in registry | Use provider average or warn |
| Local model (Ollama) | Cost is $0 | Record tokens, cost = 0 |
| New model | Not yet added to registry | Warn user, use default estimate |

### 8.2 Estimation Strategies

```python
def estimate_tokens(text: str) -> int:
    """
    Estimate token count from text.
    Rule of thumb: ~4 characters per token for English.
    """
    return len(text) // 4

def get_default_cost(provider: str) -> Tuple[float, float]:
    """
    Get default input/output cost for unknown models.
    Returns (input_cost, output_cost) per 1M tokens.
    """
    defaults = {
        "openai": (5.0, 15.0),      # GPT-4o average
        "anthropic": (3.0, 15.0),   # Claude average
        "google": (1.25, 5.0),      # Gemini average
        "xai": (2.0, 6.0),          # Grok average
        "azure": (5.0, 15.0),       # Same as OpenAI
        "ollama": (0.0, 0.0),       # Local, free
        "local": (0.0, 0.0),        # Local, free
    }
    return defaults.get(provider, (5.0, 15.0))  # Conservative default
```

### 8.3 User Warnings

```python
# When cost is estimated
logger.warning(
    f"Cost estimated for unknown model '{model_id}'. "
    f"Add to registry for accurate tracking."
)

# When tokens are estimated
logger.warning(
    f"Token count estimated for provider '{provider}' "
    f"(provider did not return usage data)."
)
```

---

## 9. Implementation Tasks for Devin AI

### Task 6.3.4: Cost Tracking Implementation

**Priority:** Medium

#### 9.1 Create Cost Tracker Module

**File:** `src/lattice_lock_orchestrator/cost_tracker.py` (new file)

1. Implement `UsageRecord` dataclass
2. Implement `CostReport` dataclass
3. Implement `SessionSummary` dataclass
4. Implement `CostTracker` class with:
   - In-memory storage (list of UsageRecord)
   - Optional SQLite backend
   - All query methods from API Surface section
5. Implement `get_cost_tracker()` singleton
6. Implement `calculate_cost()` helper

#### 9.2 Create SQLite Storage Backend

**File:** `src/lattice_lock_orchestrator/cost_storage.py` (new file)

1. Implement `CostStorage` abstract base class
2. Implement `MemoryStorage` class
3. Implement `SQLiteStorage` class with:
   - Auto-create database and tables
   - Connection pooling
   - Thread-safe operations

#### 9.3 Integrate with Core

**File:** `src/lattice_lock_orchestrator/core.py`

1. Add `cost_tracker` to `ModelOrchestrator.__init__`
2. Call `cost_tracker.record_usage()` in `_call_model()`
3. Add `get_cost_report()` method to `ModelOrchestrator`

#### 9.4 Update CLI

**File:** `scripts/orchestrator_cli.py`

1. Replace stub `show_cost_report()` with real implementation
2. Add `--detailed`, `--by-model`, `--by-provider` flags
3. Add `--history` flag for time-based reports
4. Add `--export` flag for CSV/JSON export
5. Add `--clear-session` flag

#### 9.5 Update Types

**File:** `src/lattice_lock_orchestrator/types.py`

1. Add `UsageRecord` to exports
2. Add `CostReport` to exports
3. Consider adding `TaskType` to `APIResponse` if not present

#### 9.6 Write Tests

**File:** `tests/test_cost_tracker.py` (new file)

```python
def test_record_usage():
    """Test recording a single usage record."""
    ...

def test_session_cost_aggregation():
    """Test session cost calculation."""
    ...

def test_cost_by_model():
    """Test cost breakdown by model."""
    ...

def test_cost_by_provider():
    """Test cost breakdown by provider."""
    ...

def test_sqlite_persistence():
    """Test SQLite storage backend."""
    ...

def test_csv_export():
    """Test CSV export functionality."""
    ...

def test_unknown_model_handling():
    """Test handling of unknown models."""
    ...

def test_missing_token_count():
    """Test estimation when tokens not returned."""
    ...
```

#### 9.7 Add Configuration

**File:** `src/lattice_lock_orchestrator/config.py` (new or update)

1. Add `LATTICE_COST_TRACKING` environment variable handling
2. Add `LATTICE_COST_DB_PATH` environment variable handling
3. Add configuration validation

---

## 10. Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage | Hybrid (Memory + SQLite) | Zero-config default, opt-in persistence |
| Token estimation | ~4 chars/token | Industry standard approximation |
| Unknown model cost | Provider average | Conservative fallback |
| Integration point | `_call_model()` | Single point of capture |
| CLI design | Rich tables | Consistent with existing CLI style |

**Files to Create:**
1. `src/lattice_lock_orchestrator/cost_tracker.py` - Main tracker
2. `src/lattice_lock_orchestrator/cost_storage.py` - Storage backends
3. `tests/test_cost_tracker.py` - Tests

**Files to Modify:**
1. `src/lattice_lock_orchestrator/core.py` - Integration
2. `scripts/orchestrator_cli.py` - CLI commands
3. `src/lattice_lock_orchestrator/types.py` - Type exports

**Estimated Implementation Time:** 4-6 hours
