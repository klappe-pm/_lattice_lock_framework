# Prompt 5.1.1 - Prompt Architect Agent Core Setup

**Tool:** Devin AI
**Epic:** 5.1 - Prompt Architect Core
**Phase:** 5 - Prompt Automation

## Context

The Lattice Lock Framework now has a Prompt Architect Agent defined at `agent_definitions/prompt_architect_agent/` with four subagents (spec_analyzer, roadmap_parser, tool_matcher, prompt_generator). This agent is designed to automatically generate LLM prompts from project specifications and roadmaps.

The agent definitions follow the v2.1 specification format at `agent_specifications/agent_instructions_file_format_v2_1.md`. The agent memory file is at `agent_memory/agents/agent_prompt_architect_memory.md`.

## Goal

Implement the core orchestration logic for the Prompt Architect Agent that coordinates the four subagents to generate prompts from specifications.

## Steps

1. Create `src/lattice_lock_agents/prompt_architect/__init__.py` with:
   - `PromptArchitectAgent` class that loads the YAML definition
   - Methods to invoke each subagent in sequence
   - State management for tracking prompt generation progress

2. Create `src/lattice_lock_agents/prompt_architect/orchestrator.py` with:
   - `orchestrate_prompt_generation(spec_path, roadmap_path)` function
   - Pipeline: spec_analyzer -> roadmap_parser -> tool_matcher -> prompt_generator
   - Error handling and retry logic for each stage

3. Create `src/lattice_lock_agents/prompt_architect/models.py` with Pydantic models:
   - `SpecificationAnalysis` - output from spec_analyzer
   - `RoadmapStructure` - output from roadmap_parser
   - `ToolAssignment` - output from tool_matcher
   - `GeneratedPrompt` - output from prompt_generator

4. Add CLI command to `scripts/orchestrator_cli.py`:
   - `generate-prompts` subcommand
   - Options: `--spec`, `--roadmap`, `--output-dir`, `--dry-run`

5. Create unit tests at `tests/test_prompt_architect.py`:
   - Test orchestration pipeline
   - Test each subagent invocation
   - Test error handling

6. Update `agent_memory/agents/agent_prompt_architect_memory.md` with implementation status

## Do NOT Touch

- `src/lattice_lock_cli/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI)
- `developer_documentation/` (owned by Claude Code Website)
- Existing agent definitions in `agent_definitions/` (except prompt_architect_agent)
- `project_prompts/` prompt files (owned by prompt_generator subagent)

## Success Criteria

- `PromptArchitectAgent` class can load and parse YAML definition
- Orchestration pipeline executes all four subagents in sequence
- CLI command `./scripts/orchestrator_cli.py generate-prompts --help` works
- Unit tests pass with >80% coverage
- Agent memory file updated with implementation status

## Notes

- Use the existing Model Orchestrator for LLM calls
- Follow the delegation protocol in the agent definition
- Respect the model selection strategy (local/deepseek-r1:70b as default)
- Pre-existing broken tests are out of scope - do not try to fix them
