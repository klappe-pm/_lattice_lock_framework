# Prompt 3.2.1 - Rollback State Management

**Tool:** Gemini CLI
**Epic:** 3.2 - Automatic Rollback Mechanism
**Phase:** 3 - Error Handling & Admin

## Context

The Lattice Lock Framework needs automatic rollback capabilities when validation fails. This requires tracking state changes and maintaining rollback points that can be restored.

## Goal

Implement state management for rollback functionality.

## Steps

1. Create `src/lattice_lock/rollback/` module:
   ```
   rollback/
   ├── __init__.py
   ├── state.py
   ├── checkpoint.py
   └── storage.py
   ```

2. Create `state.py`:
   - `RollbackState` dataclass with timestamp, files, config
   - State serialization/deserialization
   - State comparison for diff detection

3. Create `checkpoint.py`:
   - `create_checkpoint()` - capture current state
   - `list_checkpoints()` - list available rollback points
   - `get_checkpoint(id)` - retrieve specific checkpoint
   - `delete_checkpoint(id)` - remove old checkpoints

4. Create `storage.py`:
   - File-based storage for checkpoints
   - `.lattice-lock/checkpoints/` directory
   - Compression for large states
   - Retention policy (keep last N checkpoints)

5. Implement state tracking:
   - Track file changes (hash-based)
   - Track configuration changes
   - Track schema version changes

6. Write unit tests in `tests/test_rollback_state.py`:
   - Test checkpoint creation
   - Test state serialization
   - Test storage operations

## Do NOT Touch

- `src/lattice_lock_validator/agents.py` (owned by Codex CLI)
- `src/lattice_lock_validator/structure.py` (owned by Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/` (owned by Claude Code CLI/App)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- Checkpoints capture complete state
- State can be serialized and restored
- Storage handles large states efficiently
- Unit tests pass

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use JSON for state serialization
- Consider git-like object storage for efficiency
