# Lattice Lock Framework Error Codes

This document lists the standardized error codes used throughout the Lattice Lock Framework. All errors inherit from `LatticeError` and follow the `LL-XXX` format.

## Error Code Ranges

| Range | Error Type | Description |
|-------|------------|-------------|
| **LL-000** | `LatticeError` | Base framework error. Used for generic or unclassified errors. |
| **LL-100 - LL-199** | `SchemaValidationError` | Issues with `lattice.yaml` schema or Meta-Schema validation. |
| **LL-200 - LL-299** | `SheriffViolationError` | Static analysis violations (AST compliance, import bans, type hints). |
| **LL-300 - LL-399** | `GauntletFailureError` | Semantic contract failures (pytest execution on generated code). |
| **LL-400 - LL-499** | `LatticeRuntimeError` | Runtime failures during orchestration or model execution. |
| **LL-500 - LL-599** | `ConfigurationError` | Missing credentials, invalid env vars, or malformed config files. |
| **LL-600 - LL-699** | `NetworkError` | API connection failures, timeouts, or provider outages. |
| **LL-700 - LL-799** | `AgentError` | failures in agent orchestration, sub-agent communication, or memory. |

## Detailed Error Types

### LL-100 Series: Validation
- **LL-100**: General Schema Validation Error.
- _Specific codes within this range may be added for granular schema issues._

### LL-200 Series: Sheriff (Static Analysis)
- **LL-200**: General Sheriff Violation.
- _Used when the generated code violates strict structural rules._

### LL-300 Series: Gauntlet (Semantic Testing)
- **LL-300**: General Gauntlet Failure.
- _Used when generated code fails to pass the contract test suite._

### LL-400 Series: Runtime
- **LL-400**: General Runtime Error.
- _Orchestrator failures that don't fit other categories._

### LL-500 Series: Configuration
- **LL-500**: General Configuration Error.
- _e.g., `LATTICE_API_KEY` missing._

### LL-600 Series: Network
- **LL-600**: General Network Error.
- _Includes `APIClientError` from providers._

### LL-700 Series: Agents
- **LL-700**: General Agent Error.
- _Failures in the multi-agent negotiation or context sharing._
