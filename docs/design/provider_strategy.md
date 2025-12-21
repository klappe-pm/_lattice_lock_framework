# Provider Client and Fallback Strategy Design

## 1. Provider Maturity Tiers

To manage the stability and reliability of different model providers, we introduce a maturity tier system. This allows us to integrate experimental providers without compromising the stability of critical workflows.

### Tiers

| Tier | Description | Usage |
| :--- | :--- | :--- |
| **PRODUCTION** | Fully tested, reliable, stable API, verified credentials. | Default for all critical workflows (Coding, Architecture). |
| **BETA** | Functional but may have occasional instability or changing APIs. | Opt-in for specific tasks; fallback targets. |
| **EXPERIMENTAL** | In development, unverified, or requires complex setup (e.g., custom VPC). | gated behind explicit configuration flags. |

### Classification

| Provider | Tier | Notes |
| :--- | :--- | :--- |
| OpenAI | PRODUCTION | Industry standard, high reliability. |
| Anthropic | PRODUCTION | High reliability, strong reasoning. |
| Google | BETA | Strong capabilities, but API subject to changes. |
| xAI (Grok) | BETA | Newer provider, rapid evolution. |
| Ollama | BETA | Local dependency, variable performance. |
| Azure | BETA | Enterprise setup dependencies. |
| Bedrock | EXPERIMENTAL | Requires AWS credentials/roles, complex signature signing. |

## 2. Bedrock Integration Decision

**Decision: GATE**

Amazon Bedrock requires AWS Signature V4 signing and valid AWS credentials (profile or environment variables). Given the complexity of verifying these in all environments and the current lack of `boto3` as a hard dependency in some contexts, we will **GATE** Bedrock integration.

-   **Implementation**: The `BedrockAPIClient` will exist but will raise `NotImplementedError` or a specific `ConfigurationError` if instantiated without explicit "experimental" flags or if `boto3` is missing.
-   **Future Work**: Full implementation will require a dedicated AWS auth module.

## 3. Credential Validation Strategy

Each provider client must implement a lightweight validation mechanism to ensure credentials are correct before attempting heavy workloads.

### Mechanism
-   **Method**: `validate_credentials() -> bool`
-   **Behavior**:
    -   Performs a minimal API call (e.g., list models, or a token/hello-world prompt).
    -   Returns `True` if successful, `False` on 401/403 errors.
    -   Catches connection errors but logs them (soft fail vs hard auth fail).

## 4. Fallback Behavior and Retry Logic

Robustness is achieved through a multi-layer fallback strategy.

### Layers

1.  **Retry Layer (Per-Request)**:
    -   Handling transient network errors (timeouts, 5xx).
    -   Strategy: Exponential backoff (already partially implemented with `tenacity`).

2.  **Model Fallback (Same Provider)**:
    -   If a specific model fails (e.g., `gpt-4o` overload), try an equivalent model within the same provider (e.g., `gpt-4-turbo`).
    -   *Constraint*: Must have same capability class (e.g., Vision).

3.  **Provider Fallback (Cross-Provider)**:
    -   If an entire provider is down or credentials fail.
    -   Strategy: Switch to a predefined backup provider of equal maturity.
    -   Example: `OpenAI (Prime)` -> `Anthropic (Backup)`.

### Logic
```python
async def execute_with_fallback(task, preferred_provider):
    try:
        return await preferred_provider.execute(task)
    except (AuthError, ServiceUnavailable):
        backup = get_backup_provider(preferred_provider)
        if backup and backup.is_healthy():
            return await backup.execute(task)
        raise
```

## 5. Health Check Mechanisms

Proactive health monitoring to remove unhealthy providers from the rotation.

### Mechanism
-   **Method**: `health_check() -> HealthStatus`
-   **Frequency**: On startup and periodically (background task) or Lazy (on failure).
-   **States**: `HEALTHY`, `DEGRADED` (high latency/errors), `UNHEALTHY` (auth fail/down).
