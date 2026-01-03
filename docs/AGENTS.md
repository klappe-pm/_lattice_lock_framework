# AI Agent Capabilities

Lattice Lock is designed to be fully navigable and operable by AI agents (like Claude, ChatGPT, etc.). This document outlines the capabilities and interfaces exposed specifically for agents.

## Core Interfaces


### 1. Lattice CLI
The primary interface for agents is the terminal CLI. All commands support JSON output for machine parsing.

- **Status Check**: `lattice doctor --json`
- **Configuration**: `lattice init` (interactive, avoid for agents unless scripting inputs)
- **Validation**: `lattice validate --json`

### 2. MCP Server
Lattice Lock exposes a Model Context Protocol (MCP) server.

- **Tools**: `validate_code`, `ask_orchestrator`, `run_tests`
- **Prompts**: `governance-check`, `code-review`
- **Transport**: stdio (over stdin/stdout)

## Agent Workflows

### Code Review
Agents should use `lattice validate` or the `validate_code` MCP tool to check compliance before submitting code.

### Architecture Decisions
Use `lattice ask` or `ask_orchestrator` to consult the Lattice Lock internal knowledge base for architectural guidance.

## Context Files

- `CLAUDE.md`: High-level instructions for AI assistants.
- `lattice.yaml`: Project governance definitions.
- `models.yaml`: Model registry configuration.
