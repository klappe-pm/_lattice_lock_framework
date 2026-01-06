---
title: "Consensus Module"
type: reference
status: stable
categories: [Technical, Modules]
sub_categories: [Consensus]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [mod-consensus-001]
tags: [consensus, voting, strategy]
author: AI Agent
---

# Consensus Module

The Consensus Engine aggregates outputs from multiple models to achieve higher accuracy and reliability for critical tasks.

## Workflow

1.  **Request**: A `ConsensusRequest` defines the task, candidate responses, and desired strategy.
2.  **Strategy Execution**: The engine delegates to a specific `ConsensusStrategy`.
3.  **Consolidation**: The strategy processes the candidates and returns a single, synthesized string.

## Strategies

### Majority Vote (`majority`)
-   **Logic**: simple frequency count.
-   **Use Case**: Classification tasks, multiple choice.
-   **Requirement**: > 50% agreement.

### Unanimity (`unanimous`)
-   **Logic**: All candidates must be identical.
-   **Use Case**: High-stakes security checks where disagreement implies risk.

### Synthesis (`synthesis` / `weighted`)
-   **Logic**: Uses a strong LLM to reason over conflicting answers and generate a superior response.
-   **Stance**: Can be steered with a "Persona" or "Stance" (e.g., "Prioritize security over performance").

### Debate (`debate`)
-   **Logic**: Multi-round refinement. The orchestrator acts as a moderator, critiquing candidates and iteratively improving the answer.
-   **Cost**: Higher (multiple calls), but generally yields higher quality reasoning.
