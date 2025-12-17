# Task 6.3.7: Task Analyzer v2 Design

**Status:** Approved
**Owner:** Gemini Antimatter
**Implementation Task:** 6.3.8 (Devin AI)

---

## 1. Shortcomings of v1
Current implementation checks if keywords like "code", "debug", "test" appear in the prompt.
*   *Failure Mode:* "Write a test plan for this code" -> Detected as `TESTING`. Correct.
*   *Failure Mode:* "I am testing my patience with this bug" -> Detected as `TESTING`. Incorrect (Should be `DEBUGGING` or `GENERAL`).

## 2. v2 Hybrid Architecture

We will implement a **Hybrid Classifier**:

### Stage 1: Fast Heuristics (Regex)
Improved regex patterns with negative lookaheads.
*   High confidence matches short-circuit the process.
*   Example: `^def .*:` or `import .*` -> `CODE_GENERATION` (Confidence: High).

### Stage 2: Semantic Router (LLM Light)
If heuristics are low confidence (< 0.8), use a lightweight model (e.g., `gpt-4o-mini` or `gemini-flash`) to classify.

**Prompt:**
```text
Classify the following user prompt into one category:
[CODE_GENERATION, DEBUGGING, ARCHITECTURAL_DESIGN, DOCUMENTATION, TESTING, DATA_ANALYSIS, VISION, GENERAL]

Prompt: "{user_prompt}"

Return JSON: {"type": "...", "confidence": 0.9}
```

## 3. Caching
Classifications are cached by prompt hash (SHA-256) in an LRU cache (size=1000) to minimize latency for repeated queries.

## 4. Implementation Specifications

**`src/lattice_lock_orchestrator/routing/analyzer.py`**

```python
class TaskAnalyzer:
    def analyze(self, prompt: str) -> TaskRequirements:
        # 1. Check Cache
        # 2. Run Heuristics
        # 3. If ambiguous, Run LLM Router
        # 4. Return Requirements (TaskType + Min Specs)
```

## 5. Validation Set
Create `tests/data/prompts.json` with 100 examples labeled with correct TaskType to benchmark accuracy. Target > 90% accuracy.
