# Prompt 5.1.2 - Prompt Architect Integration with Project Agent

**Tool:** Devin AI
**Epic:** 5.1 - Prompt Architect Core
**Phase:** 5 - Prompt Automation

## Context

The Prompt Architect Agent needs to integrate with the existing Project Agent (`agent_definitions/project_agent/`) to access project scope, goals, and planning information. The Project Agent has subagents for task management, planning, analysis, and status writing.

The integration should follow the agent-to-agent interaction patterns defined in the Universal Memory Directive at `agent_memory/universal_memory_directive.md`.

## Goal

Implement integration between Prompt Architect Agent and Project Agent to enable automatic prompt generation based on project plans.

## Steps

1. Create `src/lattice_lock_agents/prompt_architect/integrations/project_agent.py`:
   - `ProjectAgentClient` class for querying project state
   - Methods: `get_project_scope()`, `get_current_phase()`, `get_pending_tasks()`
   - Parse project_planner subagent outputs

2. Update `src/lattice_lock_agents/prompt_architect/orchestrator.py`:
   - Add `--from-project` option to use Project Agent as input source
   - Implement automatic spec/roadmap discovery from project state

3. Create `src/lattice_lock_agents/prompt_architect/integrations/__init__.py`:
   - Export all integration clients
   - Registry pattern for available integrations

4. Add agent-to-agent interaction logging:
   - Log interactions to both agent memory files
   - Track token usage across agent boundaries
   - Update interaction tables in memory files

5. Create integration tests at `tests/integration/test_prompt_project_integration.py`:
   - Test Project Agent client
   - Test automatic discovery workflow
   - Test memory file updates

## Do NOT Touch

- `agent_definitions/project_agent/` (read-only access)
- `src/lattice_lock_cli/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `ProjectAgentClient` can query project state
- `--from-project` option works in CLI
- Agent-to-agent interactions logged in both memory files
- Integration tests pass
- Token usage tracked across agent boundaries

## Notes

- Use read-only access to Project Agent definitions
- Follow the Universal Memory Directive for interaction logging
- Respect the scope contract boundaries defined in agent definitions
- Pre-existing broken tests are out of scope - do not try to fix them
