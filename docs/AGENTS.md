# Lattice Lock Agents

Catalog of available agents and tools within the framework.

## Sheriff (`validate_code`)

**Role**: Governance Enforcer

The Sheriff agent enforces coding standards, security policies, and architectural consistency. It acts as a gatekeeper, preventing non-compliant code from entering the repository.

**Capabilities**:
- Static analysis via `bandit` and custom rules.
- Policy enforcement (imports, structure, types).
- Auto-fix suggestions for common violations.

## Gauntlet (`run_tests`)

**Role**: Quality Assurance

The Gauntlet agent manages the testing lifecycle. It executes test suites, measures coverage, and ensures functional correctness.

**Capabilities**:
- Unit test execution (`pytest`).
- Integration testing.
- Test generation (via MCP templates).

## Orchestrator (`ask_orchestrator`)

**Role**: System Coordinator

The Orchestrator agent is the central nervous system, routing requests to the most appropriate underlying model (LLM) based on task complexity, cost, and specific capabilities.

**Capabilities**:
- **Semantic Routing**: Analyzes prompts to select the best model (e.g., Claude 3.5 Sonnet for coding, GPT-4o for reasoning).
- **Fallback Chains**: Automatically retries with alternative models if the primary fails.
- **Consensus**: Runs multi-model voting or debate strategies for critical decisions.
