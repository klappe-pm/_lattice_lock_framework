# Prompt 2.4.2 - Sheriff AST Rules Engine

**Tool:** Gemini CLI
**Epic:** 2.4 - Sheriff CLI Wrapper
**Phase:** 2 - CI/CD Integration

## Context

Sheriff needs a configurable AST rules engine that can enforce import discipline, type hints, and custom rules defined in lattice.yaml. The rules engine should be extensible for future rule types.

## Goal

Implement the AST rules engine for Sheriff validation.

## Steps

1. Create `src/lattice_lock_sheriff/` module:
   ```
   lattice_lock_sheriff/
   ├── __init__.py
   ├── rules.py
   ├── ast_visitor.py
   └── config.py
   ```

2. Create `rules.py` with rule definitions:
   - `ImportDisciplineRule`: Check imports against forbidden list
   - `TypeHintRule`: Ensure all functions have return type hints
   - `VersionComplianceRule`: Check lattice version usage
   - Base `Rule` class for extensibility

3. Create `ast_visitor.py`:
   - Custom AST visitor that applies rules
   - Collect violations with line numbers
   - Support for `# lattice:ignore` comments

4. Create `config.py`:
   - Load rules from lattice.yaml `config.forbidden_imports`
   - Support custom rule configuration
   - Default rules when no config provided

5. Implement rule interface:
   ```python
   class Rule(ABC):
       @abstractmethod
       def check(self, node: ast.AST, context: RuleContext) -> list[Violation]
   ```

6. Write unit tests in `tests/test_sheriff_rules.py`:
   - Test each rule type
   - Test rule configuration loading
   - Test ignore comments work

## Do NOT Touch

- `src/lattice_lock_validator/agents.py` (owned by Codex CLI)
- `src/lattice_lock_validator/structure.py` (owned by Codex CLI)
- `src/lattice_lock/__init__.py` (owned by Devin AI)
- `pyproject.toml` (owned by Devin AI)
- `src/lattice_lock_cli/__main__.py` (owned by Claude Code CLI)
- `developer_documentation/` (owned by Claude Code Website)

## Success Criteria

- All rule types implemented and tested
- Rules configurable via lattice.yaml
- Extensible rule interface
- Unit tests pass with >80% coverage

## Notes

- Pre-existing broken tests are out of scope - do not try to fix them
- Use Python's ast module
- Keep rules fast and efficient
