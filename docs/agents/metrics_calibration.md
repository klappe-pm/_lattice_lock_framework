# Metrics Calibration & Cost Estimation
**Version**: 1.0.0
**Status**: Active

## Overview
This document defines the baseline metrics and complexity weights used by the Lattice Lock Framework agents to estimate task costs and effort. These values are calibrated based on the `gpt-4o` and `claude-3.5-sonnet` pricing models as of Q4 2025.

## Complexity Weights
Agents use these multipliers to estimate the "Predicted Task Size":

| Task Type | Weight | Description |
|-----------|--------|-------------|
| **Code Modification** | 1.5x | Editing existing files requires context reading + applying diffs. |
| **New File Creation** | 1.2x | Generating new content is cleaner but requires verification. |
| **Read-Only Analysis** | 0.8x | Reading and summarizing is low-risk and token-efficient. |
| **Testing & Verification** | 2.0x | Requires multiple round-trips of run -> analyze -> fix. |
| **Architectural Design** | 3.0x | High-context reasoning, often involving large context windows. |

## Cost Baselines (per step)
- **Standard Step**: $0.05 (Input: 2k tokens, Output: 500 tokens)
- **Complex Step**: $0.15 (Input: 10k tokens, Output: 1k tokens)
- **Reasoning Loop**: $0.30 (Chain-of-thought intensive)

## Thresholds (USD)

### Warning Thresholds
If a task planning phase estimates cost above these values, the user must be notified:
- **Single Agent Task**: $1.00
- **Multi-Agent Orchestration**: $5.00

### Hard Limits
Agents will auto-terminate if session cost exceeds:
- **Default Hard Limit**: $10.00

## Calibration Log
- **2025-12-20**: Initial calibration. Assumes standard rates.
