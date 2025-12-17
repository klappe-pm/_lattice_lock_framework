# Prompt 5.4.1 - Tracker Integration

**Tool:** Claude Code App
**Epic:** 5.4 - Tracker Integration
**Phase:** 5 - Prompt Automation

## Context

The project_prompts system has a tracker at `project_prompts/project_prompts_tracker.md` and a state file at `project_prompts/project_prompts_state.json`. The tracker script at `scripts/prompt_tracker.py` provides CLI commands for managing prompt execution state.

The Prompt Architect Agent needs to integrate with this tracker system to automatically update state when prompts are generated.

## Goal

Integrate the Prompt Architect Agent with the existing prompt tracker system for automatic state management.

## Steps

1. Update `scripts/prompt_tracker.py` to add new commands:
   - `add-prompt` - Add a newly generated prompt to state
   - `batch-add` - Add multiple prompts at once
   - `validate-state` - Ensure state matches actual prompt files

2. Create `src/lattice_lock_agents/prompt_architect/tracker_client.py`:
   - `TrackerClient` class for interacting with tracker
   - Methods: `add_prompt()`, `update_prompt()`, `get_next_prompt()`
   - Sync state between agent and tracker

3. Update prompt_generator to use TrackerClient:
   - Automatically add generated prompts to state
   - Set initial status (picked_up=false, done=false, merged=false)
   - Include metadata (phase, epic, tool)

4. Add tracker regeneration after prompt generation:
   - Call `regenerate` command after adding prompts
   - Ensure markdown tracker stays in sync with JSON state
   - Validate all prompts have corresponding files

5. Create integration tests at `tests/integration/test_tracker_integration.py`:
   - Test prompt addition workflow
   - Test state synchronization
   - Test tracker regeneration

## Do NOT Touch

- `src/lattice_lock_cli/commands/validate.py` (owned by Claude Code App - different epic)
- `src/lattice_lock_cli/commands/doctor.py` (owned by Claude Code App - different epic)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `add-prompt` command works correctly
- Generated prompts automatically added to state
- Tracker markdown regenerated after additions
- State validates against actual prompt files
- Integration tests pass

## Notes

- Follow existing tracker conventions
- Maintain backward compatibility with existing prompts
- Use JSON state as source of truth
- Pre-existing broken tests are out of scope - do not try to fix them
