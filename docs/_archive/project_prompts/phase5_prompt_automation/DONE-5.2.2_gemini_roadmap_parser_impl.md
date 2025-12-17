# Prompt 5.2.2 - Roadmap Parser Implementation

**Tool:** Gemini CLI
**Epic:** 5.2 - Specification Analysis
**Phase:** 5 - Prompt Automation

## Context

The roadmap_parser subagent (`agent_definitions/prompt_architect_agent/subagents/roadmap_parser.yaml`) parses roadmaps and phase plans into structured task hierarchies. It has read-only access to `/developer_documentation` and `/project_prompts/work_breakdown_structure.md`.

The parser should extract epics, tasks, dependencies, and sizing information from roadmap documents.

## Goal

Implement the roadmap parser that converts project roadmaps into structured task hierarchies for prompt generation.

## Steps

1. Create `src/lattice_lock_agents/prompt_architect/subagents/roadmap_parser.py`:
   - `RoadmapParser` class that loads the subagent YAML definition
   - `parse(roadmap_path: str) -> RoadmapStructure` method
   - Support for work breakdown structure format

2. Implement roadmap parsing logic:
   - Extract phases with exit criteria
   - Parse epics with owner tool assignments
   - Identify task dependencies (blocking, parallel)
   - Extract sizing estimates (story points, hours)

3. Create `src/lattice_lock_agents/prompt_architect/subagents/parsers/roadmap_parser.py`:
   - `WorkBreakdownParser` for WBS markdown format
   - `GanttParser` for timeline-based roadmaps
   - `KanbanParser` for board-style roadmaps
   - Common `RoadmapParser` interface

4. Add dependency graph construction:
   - Build directed acyclic graph (DAG) of tasks
   - Identify critical path
   - Detect circular dependencies
   - Calculate parallel execution opportunities

5. Create unit tests at `tests/test_roadmap_parser.py`:
   - Test WBS parsing with existing work_breakdown_structure.md
   - Test dependency graph construction
   - Test critical path calculation
   - Test error handling for malformed roadmaps

## Do NOT Touch

- `developer_documentation/` (read-only access, owned by Claude Code Website)
- `project_prompts/work_breakdown_structure.md` (read-only access)
- `src/lattice_lock_cli/` (owned by Claude Code CLI)
- `src/lattice_lock_validator/` (owned by Gemini CLI and Codex CLI - different epic)

## Success Criteria

- `RoadmapParser` can parse work_breakdown_structure.md
- Structured output matches `RoadmapStructure` Pydantic model
- Dependency graph correctly identifies task relationships
- Critical path calculation works
- Unit tests pass with existing roadmap files

## Notes

- Follow the model selection strategy in roadmap_parser.yaml
- Use local/qwen2.5:32b for parsing, deepseek-r1:70b for analysis
- Output should include tool ownership from WBS
- Pre-existing broken tests are out of scope - do not try to fix them
