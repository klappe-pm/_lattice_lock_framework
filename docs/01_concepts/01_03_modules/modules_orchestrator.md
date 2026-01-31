---
title: Orchestrator Module
type: reference
status: stable
categories:
  - Technical
  - Modules
sub_categories:
  - Orchestrator
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids:
  - mod-orchestrator-001
tags:
  - orchestrator
  - routing
  - architecture
---

# Orchestrator Module

The Orchestrator is the core component responsible for intelligent model selection and request routing.

## Architecture

The Orchestrator follows a pipeline approach:

1.  **Analysis**: The `TaskAnalyzer` evaluates the incoming user prompt to determine the `TaskType` (e.g., `CODE_GENERATION`, `REASONING`) and complexity requirements.
2.  **Selection**: The `ModelSelector` queries the `ModelRegistry` to find models that meet the requirements (context window, cost, specialized scores) and picks the optimal candidate.
3.  **Execution**: The `ConversationExecutor` handles the actual API interaction, managing context, token tracking, and tool execution loops.
4.  **Fallback**: If the primary model fails (API error, rate limit), the system automatically attempts pre-configured fallback models defined in the `ModelGuide`.

## Configuration

Configuration is managed via `src/lattice_lock/orchestrator/models.yaml` (default) or a custom guide.

### Helper Components

-   **Persistence**: Saves session state to `.lattice/sessions` to allow for multi-step workflow resumption (`--continue-from`).
-   **Cost Tracker**: Aggregates token usage and estimated costs across all providers.
