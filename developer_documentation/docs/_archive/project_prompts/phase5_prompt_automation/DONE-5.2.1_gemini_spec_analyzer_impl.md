# Prompt 5.2.1 - Specification Analyzer Implementation

**Tool:** Gemini CLI
**Epic:** 5.2 - Specification Analysis
**Phase:** 5 - Prompt Automation

## Context

The spec_analyzer subagent (`agent_definitions/prompt_architect_agent/subagents/spec_analyzer.yaml`) is responsible for analyzing project specifications and extracting structured requirements. It has read-only access to `/specifications`, `/developer_documentation`, and `/WARP.md`.

The analyzer should extract phases, components, requirements, and constraints from specification documents to feed into the prompt generation pipeline.

## Goal

Implement the specification analyzer that parses project specifications into structured data for prompt generation.

## Steps

1. Create `src/lattice_lock_agents/prompt_architect/subagents/spec_analyzer.py`:
   - `SpecAnalyzer` class that loads the subagent YAML definition
   - `analyze(spec_path: str) -> SpecificationAnalysis` method
   - Support for markdown, YAML, and JSON specification formats

2. Implement specification parsing logic:
   - Extract project phases from roadmap sections
   - Identify components and their dependencies
   - Parse requirements (functional, non-functional)
   - Extract constraints and guardrails

3. Create `src/lattice_lock_agents/prompt_architect/subagents/parsers/spec_parser.py`:
   - `MarkdownSpecParser` for `.md` files
   - `YAMLSpecParser` for `.yaml` files
   - `JSONSpecParser` for `.json` files
   - Common `SpecParser` interface

4. Add LLM-assisted extraction for complex specifications:
   - Use local/deepseek-r1:70b for document analysis (per model selection)
   - Fallback to claude-opus-4.1 for complex cases
   - Structured output using Pydantic models

5. Create unit tests at `tests/test_spec_analyzer.py`:
   - Test each parser type
   - Test LLM-assisted extraction
   - Test with sample specifications from the framework

## Do NOT Touch

- `specifications/` (read-only access)
- `developer_documentation/` (read-only access, owned by Claude Code Website)
- `src/lattice_lock_cli/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/schema.py` (owned by Gemini CLI - different epic)
- `src/lattice_lock_validator/env.py` (owned by Gemini CLI - different epic)

## Success Criteria

- `SpecAnalyzer` can parse markdown specifications
- Structured output matches `SpecificationAnalysis` Pydantic model
- LLM-assisted extraction works with local models
- Unit tests pass with sample specifications
- Parser correctly identifies phases, components, requirements

## Notes

- Follow the model selection strategy in spec_analyzer.yaml
- Use read-only access to specification files
- Output should be JSON-serializable for pipeline passing
- Pre-existing broken tests are out of scope - do not try to fix them
