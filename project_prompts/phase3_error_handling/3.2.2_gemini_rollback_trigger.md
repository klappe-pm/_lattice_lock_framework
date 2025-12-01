# Prompt 3.2.2 - Rollback Trigger System

**Tool:** Gemini CLI
**Epic:** 3.2 - Automatic Rollback Mechanism
**Phase:** 3 - Error Handling & Admin

## Context

The rollback state management needs a trigger system that automatically initiates rollback when validation fails or errors occur. This includes both automatic triggers and manual rollback commands.

## Goal

Implement the rollback trigger system with automatic and manual rollback capabilities.

## Steps

1. Create `src/lattice_lock/rollback/trigger.py`:
   - `RollbackTrigger` class
   - Automatic trigger conditions
   - Manual trigger interface
   - Rollback execution logic

2. Implement automatic triggers:
   - Validation failure trigger
   - Sheriff violation trigger
   - Gauntlet failure trigger
   - Runtime error trigger (configurable)

3. Implement rollback execution:
   - Restore files from checkpoint
   - Restore configuration
   - Verify restored state
   - Log rollback action

4. Add CLI command for manual rollback:
   ```python
   @click.command()
   @click.option('--checkpoint', help='Checkpoint ID to restore')
   @click.option('--latest', is_flag=True, help='Restore latest checkpoint')
   def rollback(checkpoint, latest):
       ...
   ```

5. Implement rollback hooks:
   - Pre-rollback hook (for cleanup)
   - Post-rollback hook (for verification)
   - Notification hook (for alerts)

6. Write unit tests in `tests/test_rollback_trigger.py`:
   - Test automatic triggers fire correctly
   - Test manual rollback works
   - Test rollback restores state correctly

## Do NOT Touch

- `src/lattice_lock_validator/agents.py` (owned by Codex CLI)
- `src/lattice_lock_validator/structure.py` (owned by Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Automatic rollback triggers on validation failure
- Manual rollback restores correct state
- Rollback is atomic and complete
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Ensure rollback is atomic (all or nothing)
- Log all rollback actions for audit
