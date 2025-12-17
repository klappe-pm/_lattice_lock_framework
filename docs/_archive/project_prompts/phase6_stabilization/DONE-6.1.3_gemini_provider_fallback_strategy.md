# Task 6.1.3: Provider Client and Fallback Strategy Design

**Status:** Approved
**Owner:** Gemini Antimatter
**Implementation Task:** 6.1.4 (Devin AI)

---

## 1. Provider Maturity Classification

We define four levels of maturity for model providers to set user expectations and guide fallback behavior.

| Tier | Definition | Providers | Behavior |
|------|------------|-----------|----------|
| **Production** | Battle-tested, stable API, high reliability. | `openai`, `anthropic` | Enabled by default. Warnings on failure. |
| **Beta** | Functional but evolving. May have rate limit issues or API quirks. | `google`, `xai` (Grok) | Enabled by default. Detailed logging on failure. |
| **Experimental** | New integration, potentially unstable or partial feature set. | `bedrock`, `azure`, `ollama` | Disabled by default. Requires explicit opt-in via config or flag. |
| **Planned** | Roadmap only. | N/A | Hard error if requested. |

## 2. Bedrock Decision

**Recommendation: Option A (Minimal Working Client)**

Given that AWS Bedrock is a major enterprise requirement, we cannot skip it. However, due to the complexity of its varied models (Titan, Claude via Bedrock, etc.), we will implement a focused client.

*   **Scope:** Support `anthropic.claude-3` models via Bedrock initially.
*   **Status:** Mark as **Experimental** in the registry.
*   **Rationale:** "Perfect is the enemy of done." A working client for the most popular Bedrock model is better than nothing.
*   **Fallback:** If Bedrock fails, fall back to direct Anthropic API if configured, or fail.

## 3. Required Environment Variables

The system will validate these at startup (lazy validation is also acceptable but startup is preferred for CLI).

| Provider | Required Env Vars | Validation Behavior |
|----------|-------------------|---------------------|
| OpenAI | `OPENAI_API_KEY` | Warn if missing, disable provider. |
| Anthropic | `ANTHROPIC_API_KEY` | Warn if missing, disable provider. |
| Google | `GOOGLE_API_KEY` | Warn if missing, disable provider. |
| xAI | `XAI_API_KEY` | Warn if missing, disable provider. |
| Azure | `AZURE_OPENAI_KEY`, `AZURE_ENDPOINT` | Silent if missing (Experimental). |
| Bedrock | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` | Silent if missing (Experimental). |
| Ollama | N/A (Local) | Check `OLLAMA_HOST` (default localhost:11434). |

**Error Message Standard:**
`"Provider '{provider}' configured but credentials '{missing_var}' not found in environment. Skipping."`

## 4. Fallback Behavior

### Strategy
We implement a **"Best Effort Waterfall"** strategy.

1.  **Primary Selection:** The orchestrator selects the optimal model based on the task (e.g., `o1-pro` for reasoning).
2.  **Availability Check:** Check if the provider is enabled and has credentials.
    *   *If No:* Move to next best model in the same class (e.g., `claude-3-5-sonnet` or `gemini-1.5-pro`).
    *   *If Yes:* Attempt request.
3.  **Runtime Failure:**
    *   If API error (500, 503, RateLimit): Log error, attempt **Immediate Retry** (backoff).
    *   If Retry fails: Trigger **Cross-Provider Fallback**.
        *   Find next best model with `capability >= required`.
        *   Log: `"Falling back from {failed_model} to {backup_model} due to {error}"`.
4.  **Terminal Failure:** If no models available, raise `ProviderUnavailableError`.

### Configuration
Fallback chains can be implicit (score-based) or explicit in `lattice.yaml` (future). For 6.1, we use implicit score-based fallback.

## 5. Provider Health Checks

*   **Startup:** `ProviderManager` initializes all registered providers.
    *   For each: Check env vars.
    *   Status set to `ACTIVE` or `MISCONFIGURED`.
*   **Runtime:**
    *   Track `consecutive_failures`.
    *   If `consecutive_failures > 3`: detailed health probe (simple generation request) before next blocking call.
    *   **Circuit Breaker:** If provider fails 5x in 1 min, mark `DEGRADED` for 5 mins.

## 6. Implementation Tasks (For Devin AI)

1.  **[ ] Create `src/lattice_lock_orchestrator/providers/fallback.py`:**
    *   Implement `FallbackManager` class.
    *   Logic for selecting next-best model.
2.  **[ ] Update `ProviderManager` in `registry.py`:**
    *   Add `validate_credentials()` method.
    *   Add `get_health_status(provider)` method.
3.  **[ ] Implement `BedrockClient` in `src/lattice_lock_orchestrator/providers/bedrock.py`:**
    *   Use `boto3`.
    *   Map `anthropic.claude-3` requests.
4.  **[ ] Add Unit Tests:**
    *   Mock failures and verify fallback.
    *   Verify env var validation.
5.  **[ ] Update `README`:**
    *   Document new provider requirements.
