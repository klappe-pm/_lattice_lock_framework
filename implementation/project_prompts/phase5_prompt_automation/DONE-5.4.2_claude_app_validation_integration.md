# Prompt 5.4.2 - Prompt Validation Integration

**Tool:** Claude Code App
**Epic:** 5.4 - Tracker Integration
**Phase:** 5 - Prompt Automation

## Context

Generated prompts need to be validated against the agent specification v2.1 format and existing prompt conventions. The validation should ensure prompts are complete, actionable, and follow the established patterns.

The agent specification is at `agent_specifications/agent_instructions_file_format_v2_1.md` and example prompts are in `project_prompts/phase1_foundation/`.

## Goal

Implement prompt validation to ensure generated prompts meet quality standards and follow conventions.

## Steps

1. Create `src/lattice_lock_agents/prompt_architect/validators/prompt_validator.py`:
   - `PromptValidator` class
   - `validate(prompt_path: str) -> ValidationResult` method
   - Check all required sections present

2. Implement section validation:
   - Context: Must reference relevant files/specs
   - Goal: Must be single, clear objective
   - Steps: Must be 4-8 specific, actionable items
   - Do NOT Touch: Must list files owned by other tools
   - Success Criteria: Must be measurable
   - Notes: Optional but recommended

3. Create `src/lattice_lock_agents/prompt_architect/validators/convention_checker.py`:
   - Check filename convention: `{phase}.{epic}.{task}_{tool}.md`
   - Check tool assignment matches file ownership matrix
   - Check phase directory placement
   - Check markdown formatting

4. Add LLM-assisted quality scoring:
   - Score prompt clarity (1-10)
   - Score step actionability (1-10)
   - Score completeness (1-10)
   - Flag prompts below threshold for review

5. Integrate validation into generation pipeline:
   - Validate before writing to file
   - Retry generation if validation fails
   - Log validation results

6. Create unit tests at `tests/test_prompt_validator.py`:
   - Test section validation
   - Test convention checking
   - Test quality scoring
   - Test with existing prompts

## Do NOT Touch

- `src/lattice_lock_cli/commands/validate.py` (owned by Claude Code App - different purpose)
- `src/lattice_lock_cli/commands/doctor.py` (owned by Claude Code App - different purpose)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `PromptValidator` catches missing sections
- Convention checker validates filename and placement
- Quality scoring provides meaningful feedback
- Validation integrated into generation pipeline
- All existing prompts pass validation
- Unit tests pass

## Notes

- Use existing prompts as ground truth for conventions
- Quality threshold should be configurable
- Validation errors should be actionable
- Pre-existing broken tests are out of scope - do not try to fix them
