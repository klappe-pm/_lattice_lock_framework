# Prompt 5.3.1 - Tool Matcher Implementation

**Tool:** Codex CLI
**Epic:** 5.3 - Prompt Generation Engine
**Phase:** 5 - Prompt Automation

## Context

The tool_matcher subagent (`agent_definitions/prompt_architect_agent/subagents/tool_matcher.yaml`) matches tasks to appropriate tools based on capabilities and file ownership. It has read-only access to `/agent_definitions` and `/project_prompts`.

The matcher uses tool profiles for: Devin, Gemini CLI, Codex CLI, Claude Code CLI, Claude Code App, and Claude Code Website.

## Goal

Implement the tool matcher that assigns tasks to the most appropriate AI tools based on capabilities and file ownership rules.

## Steps

1. Create `src/lattice_lock_agents/prompt_architect/subagents/tool_matcher.py`:
   - `ToolMatcher` class that loads the subagent YAML definition
   - `match(tasks: List[Task]) -> List[ToolAssignment]` method
   - Load tool profiles from YAML definition

2. Implement tool capability matching:
   - Parse tool profiles (strengths, file_patterns, preferred_tasks)
   - Score task-tool affinity based on task type
   - Consider file ownership rules from work_breakdown_structure.md
   - Handle multi-tool tasks (split or assign to primary)

3. Create `src/lattice_lock_agents/prompt_architect/subagents/tool_profiles.py`:
   - `ToolProfile` Pydantic model
   - `load_tool_profiles()` function
   - Capability scoring algorithm

4. Implement conflict resolution:
   - Detect file ownership conflicts
   - Apply resolution strategies (split, delegate, escalate)
   - Generate "Do NOT Touch" lists automatically
   - Balance workload across tools

5. Create unit tests at `tests/test_tool_matcher.py`:
   - Test capability matching
   - Test file ownership detection
   - Test conflict resolution
   - Test workload balancing

## Do NOT Touch

- `agent_definitions/` (read-only access, except prompt_architect_agent)
- `project_prompts/` prompt files (owned by prompt_generator)
- `src/lattice_lock_cli/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/agents.py` (owned by Codex CLI - different epic)
- `src/lattice_lock_validator/structure.py` (owned by Codex CLI - different epic)

## Success Criteria

- `ToolMatcher` correctly assigns tasks to tools
- File ownership rules respected
- Conflicts detected and resolved
- "Do NOT Touch" lists generated automatically
- Unit tests pass with sample task sets

## Notes

- Follow the model selection strategy in tool_matcher.yaml
- Use local/llama3.1:8b for matching, qwen2.5:32b for conflict resolution
- Tool profiles defined in the YAML should be the source of truth
- Pre-existing broken tests are out of scope - do not try to fix them
