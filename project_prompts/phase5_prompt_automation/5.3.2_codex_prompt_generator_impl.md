# Prompt 5.3.2 - Prompt Generator Implementation

**Tool:** Codex CLI
**Epic:** 5.3 - Prompt Generation Engine
**Phase:** 5 - Prompt Automation

## Context

The prompt_generator subagent (`agent_definitions/prompt_architect_agent/subagents/prompt_generator.yaml`) generates detailed prompts with context, goals, steps, and constraints. It can access `/specifications`, `/developer_documentation`, `/project_prompts`, and `/agent_definitions`, and can modify `/project_prompts` (prompt files only).

Generated prompts must follow the format established in existing prompts (see `project_prompts/phase1_foundation/` for examples).

## Goal

Implement the prompt generator that creates detailed, actionable prompts for each task assignment.

## Steps

1. Create `src/lattice_lock_agents/prompt_architect/subagents/prompt_generator.py`:
   - `PromptGenerator` class that loads the subagent YAML definition
   - `generate(assignment: ToolAssignment) -> GeneratedPrompt` method
   - Template-based generation with LLM enhancement

2. Implement prompt template system:
   - Load template from existing prompts as reference
   - Sections: Context, Goal, Steps (4-8), Do NOT Touch, Success Criteria, Notes
   - Variable substitution for task-specific content
   - Markdown formatting

3. Create `src/lattice_lock_agents/prompt_architect/subagents/templates/prompt_template.md`:
   - Base template matching existing prompt format
   - Placeholders for all required sections
   - Comments explaining each section's purpose

4. Implement LLM-assisted step generation:
   - Use local/codellama:34b for step generation (per model selection)
   - Use deepseek-r1:70b for validation
   - Ensure steps are specific and actionable
   - Limit to 4-8 steps per guardrails

5. Add prompt file writing:
   - Generate filename following convention: `{phase}.{epic}.{task}_{tool}.md`
   - Write to appropriate phase directory
   - Update project_prompts_state.json

6. Create unit tests at `tests/test_prompt_generator.py`:
   - Test template loading
   - Test prompt generation
   - Test file writing
   - Test state file updates

## Do NOT Touch

- Existing prompt files in `project_prompts/phase1_foundation/` through `phase4_documentation/`
- `src/lattice_lock_cli/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- `PromptGenerator` creates prompts matching existing format
- Generated prompts have all required sections
- Steps are specific and actionable (4-8 per prompt)
- Files written to correct directories with correct naming
- project_prompts_state.json updated correctly
- Unit tests pass

## Notes

- Follow the guardrails in prompt_generator.yaml
- Never generate prompts without success criteria
- Use existing prompts as reference for quality
- Pre-existing broken tests are out of scope - do not try to fix them
