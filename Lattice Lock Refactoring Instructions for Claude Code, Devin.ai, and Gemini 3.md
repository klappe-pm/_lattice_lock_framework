# LLM-Optimized Refactoring Instructions for lattice-lock-framework

**Target Agent:** Claude Code, DevinAI, Gemini 3.
**Task Type:** Code refactoring with file modifications
**Execution Mode:** Concurrent task completion with verification steps and PR documentation

---
## Tasks
This is the summary of tasks to complete. Tasks are logically grouped. Tasks are assigned to one of three agents: Claude Code, Devin.AI, or Gemini 3. Agents are provided the entire task list. Agents are then instructed to execute the tasks assigned to the agent. Agents are instructed to optimize for concurrent execution by using multiple sub-agents the agent delegates too. Agents are instructed to ensure tasks are executed in the correct order of dependencies (if they exist). Agents are instructed to execute as many tasks concurrently as possible. Agents are instructed to rview the work of all other agents (reviewing the PRs created) to ensure accuracy, and resolve issues.

All agents must follow the PR guidelines.

## Prerequisites for LLM Execution

Before starting any task:
1. Confirm you have read access to the repository structure
2. Verify you can read the current state of files before modifying them
3. For each file modification, show the exact lines being changed with before/after context
4. After each task group, run the verification commands to confirm success
5. **After completing all tasks in a group, generate a comprehensive Pull Request document**

---

## Pull Request Documentation Requirements

**After completing each Group (A, B, C, D, E, F), you MUST generate a Pull Request document following this exact template:**

### PR Document Structure

Create a file named: `PR_GROUP_[LETTER]_[SHORT_DESCRIPTION].md`

Example: `PR_GROUP_A_CI_Test_Infrastructure.md`

**Template:**

```markdown
# Pull Request: [Group Name]

## Summary

[2-3 sentence executive summary of what this PR accomplishes]

## Motivation and Context

### Problem Statement
[Detailed explanation of the issues this PR addresses]

### Why This Matters
- [Business impact]
- [Technical debt addressed]
- [Security improvements]
- [Developer experience improvements]

## Changes Made

### Overview
[High-level description of the approach taken]

### Detailed Changes

#### [Component/File 1]
**File:** `path/to/file1.py`

**Changes:**
- [Specific change 1]
- [Specific change 2]

**Before:**
```python
[relevant code snippet showing old implementation]
```

**After:**
```python
[relevant code snippet showing new implementation]
```

**Rationale:** [Why this change was necessary]

#### [Component/File 2]
[Repeat structure for each significant file]

### Files Modified
- [ ] `file/path1.py` - [brief description]
- [ ] `file/path2.py` - [brief description]
- [ ] `file/path3.md` - [brief description]

### Files Created
- [ ] `new/file/path1.py` - [brief description]

### Files Deleted
- [ ] `old/file/path.py` - [brief description]

## Testing

### Test Strategy
[Description of how changes were tested]

### Tests Added/Modified
- [ ] `tests/test_file1.py` - [what it tests]
- [ ] `tests/test_file2.py` - [what it tests]

### Verification Steps

#### Automated Tests
```bash
[Commands to run automated tests]
```

**Expected Output:**
```
[Expected test results]
```

#### Manual Verification
1. [Step-by-step manual verification instructions]
2. [Include expected outcomes]

### Test Results

**Before Changes:**
```
[Test output showing failures/issues]
```

**After Changes:**
```
[Test output showing fixes]
```

### Coverage Impact
- **Before:** [coverage percentage]
- **After:** [coverage percentage]
- **Net Change:** [+/X%]

## Security Considerations

### Vulnerabilities Addressed
- [Snyk/security finding 1] - [How fixed]
- [Snyk/security finding 2] - [How fixed]

### Security Scan Results
```bash
[Command to run security scan]
```

**Results:**
- [X] vulnerabilities resolved
- [Y] vulnerabilities remaining (if any, with explanation)

### New Security Measures
- [Any new security patterns introduced]

## Performance Impact

### Expected Performance Changes
- [Performance improvement/degradation areas]
- [Benchmarks if applicable]

### Resource Impact
- Memory: [impact]
- CPU: [impact]
- Dependencies: [new dependencies added]

## Breaking Changes

### API Changes
- [ ] No breaking changes
- [ ] Breaking changes (documented below)

[If breaking changes exist:]
- **Changed:** [what changed]
- **Migration Path:** [how users should update]
- **Deprecation Timeline:** [if applicable]

## Documentation Updates

### Documentation Changed
- [ ] README.md
- [ ] API documentation
- [ ] Configuration guides
- [ ] Other: [specify]

### Documentation Added
- [ ] New guides
- [ ] New examples
- [ ] Other: [specify]

## Dependencies

### Dependency Changes
- **Added:** [list new dependencies with versions]
- **Updated:** [list updated dependencies]
- **Removed:** [list removed dependencies]

### Dependency Justification
[For each new dependency, explain why it's necessary]

## Deployment Notes

### Pre-Deployment Checklist
- [ ] Database migrations (if applicable)
- [ ] Configuration changes required
- [ ] Environment variables to set

### Rollback Plan
[How to rollback if issues occur]

### Monitoring
[What to monitor after deployment]

## Review Checklist

### Code Quality
- [ ] Code follows project style guide
- [ ] No commented-out code remains
- [ ] No debug print statements
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate

### Testing
- [ ] All tests pass
- [ ] New code has test coverage
- [ ] Integration tests pass
- [ ] Manual testing completed

### Documentation
- [ ] Code is well-commented
- [ ] Public APIs are documented
- [ ] README is updated
- [ ] CHANGELOG is updated

### Security
- [ ] Security scan passes
- [ ] No credentials in code
- [ ] Input validation present
- [ ] Path traversal prevented

## Related Issues

Closes #[issue-number]
Relates to #[issue-number]

## Screenshots/Recordings

[If UI changes, include before/after screenshots]
[If CLI changes, include terminal recordings or output examples]

## Additional Context

[Any other relevant information]

## Reviewer Notes

### Focus Areas
[Areas that need particular attention during review]

### Questions for Reviewers
- [Question 1]
- [Question 2]

## Post-Merge Tasks

- [ ] Update documentation site
- [ ] Notify team in Slack/Discord
- [ ] Update related issues
- [ ] Create follow-up issues (if needed)

---

**PR Author:** [Your name/LLM identifier]
**Date:** [YYYY-MM-DD]
**Estimated Review Time:** [X minutes/hours]
```

---

## Group A: CI and Test Infrastructure (BLOCKING - Complete First)

### Task A1: Fix Test Path References

**Objective:** Align Makefile and CI configuration to use correct test directory path.

**Files to modify:**
1. `Makefile` (line 13)
2. `.github/workflows/ci.yml` (line 49)

**Instructions:**

1. Open `Makefile`
   - Locate line 13 (should contain `pytest tests/unit`)
   - Replace entire line with: `pytest tests/ -m "not integration" --tb=short`

2. Open `.github/workflows/ci.yml`
   - Locate line 49 (should contain `pytest tests/unit`)
   - Replace with: `pytest tests/ -m "not integration" --tb=short`

3. Verify `.github/workflows/python-app.yml` line 43
   - Confirm it contains: `pytest tests/ -v --tb=short`
   - If different, update to match

**Verification command:**
```bash
make test
```

**Expected output:** Test suite runs without "directory not found" errors.

**Success criteria:** All three files reference `tests/` not `tests/unit/`.

---

### Task A2: Fix Failing Tests

**Objective:** Resolve 16 test failures in Gauntlet and Bedrock test suites.

**Phase 1: Diagnose Gauntlet Tests (13 failures)**

Run:
```bash
pytest tests/test_gauntlet_cli.py -v --tb=short
```

**Expected issue:** Tests invoke `lattice-lock gauntlet` command which doesn't exist.

**Action:**
- If error message contains "command not found: gauntlet", mark this task as BLOCKED until Task B1 is complete
- Alternatively, update test files to use `lattice-lock test` instead:
  - Search for all occurrences of `lattice-lock gauntlet` in `tests/test_gauntlet_cli.py`
  - Replace with `lattice-lock test`
  - Repeat for `tests/test_gauntlet_ci.py`

**Phase 2: Diagnose Bedrock Tests (3 failures)**

Run:
```bash
pytest tests/test_bedrock_implementation.py -v --tb=short
```

**Common issues to check:**

1. **Constructor signature mismatch:**
   - Read the BedrockClient class definition in `src/lattice_lock_orchestrator/bedrock.py`
   - Compare `__init__` parameters with test file instantiation
   - If parameters don't match, update test file to provide correct arguments

2. **Mock signature mismatch:**
   - Check if tests use `@patch` decorators
   - Verify mocked method names match actual method names in implementation
   - Update mock paths if imports have changed

**Verification command:**
```bash
pytest tests/ --tb=short
```

**Success criteria:**
- Output shows "918 passed" (or higher)
- Zero failures
- Skipped tests are acceptable

---

### Group A: Pull Request Documentation

**After completing Tasks A1 and A2, generate:** `PR_GROUP_A_CI_Test_Infrastructure.md`

**Required sections to populate:**

1. **Summary**: "Fixes CI pipeline failures by correcting test directory paths and resolving 16 failing tests in Gauntlet and Bedrock test suites."

2. **Motivation and Context**:
   - Problem: CI failing due to non-existent `tests/unit/` directory reference
   - Problem: 16 tests failing, blocking all CI runs
   - Impact: Development velocity blocked, PRs cannot merge

3. **Detailed Changes**:
   - Document exact line changes in Makefile
   - Document exact line changes in both CI workflow files
   - Document all test file modifications
   - Include before/after diffs for each file

4. **Testing**:
   - Show output of `make test` before changes (failing)
   - Show output of `make test` after changes (passing)
   - Document test count: before vs after
   - Include full pytest output showing 0 failures

5. **Files Modified**:
   ```
   - [x] Makefile - Updated test path from tests/unit to tests/
   - [x] .github/workflows/ci.yml - Updated test path
   - [x] .github/workflows/python-app.yml - Verified correct path
   - [x] tests/test_gauntlet_cli.py - Updated command references
   - [x] tests/test_gauntlet_ci.py - Updated command references
   - [x] tests/test_bedrock_implementation.py - Fixed [specific issue]
   ```

6. **Breaking Changes**: None (internal test infrastructure only)

7. **Deployment Notes**: None (no deployment impact, CI fixes only)

---

## Group B: CLI Command Consolidation

### Task B1: Add "gauntlet" Command Alias

**Objective:** Make both `lattice-lock test` and `lattice-lock gauntlet` work identically.

**File to modify:** `src/lattice_lock_cli/__main__.py`

**Instructions:**

1. Open `src/lattice_lock_cli/__main__.py`

2. Locate line 62 (should read: `cli.add_command(gauntlet_command, name="test")`)

3. After line 62, insert new line:
   ```python
   cli.add_command(gauntlet_command, name="gauntlet")  # Alias for backward compatibility
   ```

4. Verify the change by showing 5 lines before and after your insertion

**Verification command:**
```bash
lattice-lock test --help
lattice-lock gauntlet --help
```

**Success criteria:**
- Both commands output identical help text
- Both show the same available options
- Exit code 0 for both

**Documentation updates (separate commits):**

After CLI change is verified, update these files:

1. `developer_documentation/reference/cli/index.md`
   - Find the table row for the `test` command
   - Update description to: `Generate and run semantic tests from lattice.yaml (alias: gauntlet)`

2. `developer_documentation/reference/cli/gauntlet.md`
   - In the "Synopsis" section, add a note:
     ```markdown
     **Note:** This command is also available as `lattice-lock test`. Both names are supported.
     ```

3. `specifications/lattice_lock_framework_specifications.md`
   - Search for all occurrences of `lattice-lock gauntlet`
   - Replace with `lattice-lock test`
   - Should affect approximately lines 216-218

---

### Task B2: Consolidate Orchestrator CLI

**Objective:** Eliminate duplication between `scripts/orchestrator_cli.py` and `lattice-lock orchestrator` command.

**Phase 1: Audit Command Coverage**

1. Read `scripts/orchestrator_cli.py`
2. List all commands in the `if __name__ == "__main__"` block's argument parser
3. Read `src/lattice_lock_cli/groups/orchestrator.py`
4. Create comparison table:

| Command | In Script? | In Packaged CLI? | Action Needed |
|---------|-----------|------------------|---------------|
| list | | | |
| analyze | | | |
| route | | | |
| consensus | | | |
| cost | | | |
| test | | | |
| generate-prompts | | | |

**Phase 2: Migrate Missing Commands**

For each command where "In Script? = Yes" and "In Packaged CLI? = No":

**Example for 'route' command:**

1. Read the `route` function implementation in `scripts/orchestrator_cli.py`
2. Extract the core logic (excluding argparse boilerplate)
3. Open `src/lattice_lock_cli/groups/orchestrator.py`
4. Add new Click command:
   ```python
   @orchestrator_group.command()
   @click.argument('task_description')
   @click.option('--format', type=click.Choice(['json', 'table']), default='table')
   def route(task_description: str, format: str):
       """Route a task description to the optimal model."""
       # [paste extracted logic here]
   ```

**Phase 3: Deprecate Script File**

1. Open `scripts/orchestrator_cli.py`
2. Replace entire file content with:
   ```python
   #!/usr/bin/env python3
   """
   DEPRECATED: This script is superseded by 'lattice-lock orchestrator'.

   This file remains for backward compatibility only.
   Please update your workflows to use: lattice-lock orchestrator <command>
   """
   import sys
   import warnings

   warnings.warn(
       "orchestrator_cli.py is deprecated. Use 'lattice-lock orchestrator' instead.",
       DeprecationWarning,
       stacklevel=2
   )

   from lattice_lock_cli.__main__ import cli

   if __name__ == "__main__":
       sys.exit(cli())
   ```

**Verification command:**
```bash
lattice-lock orchestrator --help
python scripts/orchestrator_cli.py --help
```

**Success criteria:**
- `lattice-lock orchestrator` shows all commands from the old script
- Running the old script shows deprecation warning
- Both invocations produce functionally equivalent results

---

### Group B: Pull Request Documentation

**After completing Tasks B1 and B2, generate:** `PR_GROUP_B_CLI_Consolidation.md`

**Required sections to populate:**

1. **Summary**: "Adds backward-compatible 'gauntlet' command alias and consolidates duplicated orchestrator CLI functionality into unified command structure."

2. **Motivation and Context**:
   - Problem: Documentation references `lattice-lock gauntlet` but command is actually `test`
   - Problem: Duplicate orchestrator CLIs (script vs packaged) causing maintenance burden
   - Why: Improves UX consistency and reduces code duplication
   - Impact: Fixes 13 test failures, improves maintainability

3. **Breaking Changes**:
   ```markdown
   ## Breaking Changes

   ### API Changes
   - [x] No breaking changes (backward-compatible alias added)

   ### Deprecations
   - **Deprecated:** `scripts/orchestrator_cli.py`
   - **Replacement:** `lattice-lock orchestrator` command
   - **Timeline:** Script will be removed in v3.0.0 (6 months)
   - **Migration:** Replace `python scripts/orchestrator_cli.py [cmd]` with `lattice-lock orchestrator [cmd]`
   ```

4. **Detailed Changes**:
   - Document the alias addition with exact code
   - Document each migrated orchestrator subcommand
   - Show the deprecation wrapper implementation
   - Include command comparison table (before/after)

5. **Testing**:
   ```bash
   # Test alias works
   lattice-lock test --help
   lattice-lock gauntlet --help
   diff <(lattice-lock test --help) <(lattice-lock gauntlet --help)

   # Test orchestrator consolidation
   lattice-lock orchestrator list
   lattice-lock orchestrator analyze "example task"

   # Test deprecation warning
   python scripts/orchestrator_cli.py 2>&1 | grep DEPRECATION
   ```

6. **Documentation Updates**:
   - List all files where `gauntlet` references were updated to mention alias
   - Include diff showing specification updates

7. **Files Modified**:
   ```
   - [x] src/lattice_lock_cli/__main__.py - Added gauntlet alias
   - [x] src/lattice_lock_cli/groups/orchestrator.py - Added [X] commands
   - [x] scripts/orchestrator_cli.py - Deprecated with wrapper
   - [x] developer_documentation/reference/cli/index.md - Updated descriptions
   - [x] developer_documentation/reference/cli/gauntlet.md - Added alias note
   - [x] specifications/lattice_lock_framework_specifications.md - Updated examples
   ```

8. **Post-Merge Tasks**:
   - [ ] Update README with deprecation notice for orchestrator_cli.py
   - [ ] Create GitHub issue to track v3.0.0 script removal
   - [ ] Announce deprecation in changelog

---

## Group C: Shared Utility Refactoring (Security)

### Task C1: Centralize Jinja2 Environment Configuration

**Objective:** Fix 4 Snyk findings for missing autoescape configuration by creating shared Jinja2 utility.

**Phase 1: Create Utility Module**

1. Create new file: `src/lattice_lock/utils/jinja.py`
2. Insert this complete module:

```python
"""Centralized Jinja2 environment configuration.

This module provides secure Jinja2 environment creation with explicit
autoescape policies to prevent XSS vulnerabilities.
"""
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, select_autoescape

def create_template_env(template_dir: Path, **kwargs: Any) -> Environment:
    """Create a Jinja2 environment with explicit autoescape policy.

    Args:
        template_dir: Directory containing template files
        **kwargs: Additional arguments passed to Environment()

    Returns:
        Configured Jinja2 Environment

    Notes:
        - Autoescape is enabled for HTML/XML files (prevents XSS)
        - Disabled for YAML, Markdown, Python (preserves code generation)
        - Default for string templates is False (safe for code generation)
    """
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "htm", "xml"),
            default_for_string=False,
            default=False,
        ),
        **kwargs
    )

def template_from_string(env: Environment, template_str: str):
    """Create a template from a string using environment's autoescape policy.

    Args:
        env: Jinja2 environment (from create_template_env)
        template_str: Template content as string

    Returns:
        Compiled Jinja2 template
    """
    return env.from_string(template_str)
```

**Phase 2: Update Existing Files**

**File 1:** `src/lattice_lock_cli/templates/__init__.py`

Current state (line 18):
```python
from jinja2 import Environment, FileSystemLoader
```

Action:
1. Replace the import on line 18 with:
   ```python
   from lattice_lock.utils.jinja import create_template_env
   ```

2. Find the function that creates the Environment (likely named `get_template_env()`)

3. Replace the Environment instantiation with:
   ```python
   def get_template_env() -> Environment:
       return create_template_env(
           TEMPLATES_DIR,
           trim_blocks=True,
           lstrip_blocks=True,
           keep_trailing_newline=True,
       )
   ```

**File 2:** `src/lattice_lock_gauntlet/generator.py`

Current state (line 20):
```python
from jinja2 import Environment, FileSystemLoader
```

Action:
1. Replace import with:
   ```python
   from lattice_lock.utils.jinja import create_template_env
   ```

2. Find the GauntletGenerator class `__init__` method

3. Locate where `Environment()` is instantiated (likely: `self.env = Environment(…)`)

4. Replace with:
   ```python
   self.env = create_template_env(Path(__file__).parent / "templates")
   ```

**File 3:** `src/lattice_lock_agents/prompt_architect/subagents/prompt_generator.py`

Current state (lines 147, 316):
```python
from jinja2 import Template
# Later: Template(template_content)
```

Action:
1. Add import at top of file:
   ```python
   from lattice_lock.utils.jinja import create_template_env, template_from_string
   ```

2. In the class `__init__` method, add:
   ```python
   self._jinja_env = create_template_env(Path(__file__).parent / "templates")
   ```

3. Find line 147, replace `Template(template_content)` with:
   ```python
   template = template_from_string(self._jinja_env, template_content)
   ```

4. Find line 316, replace `Template(template_content)` with:
   ```python
   template = template_from_string(self._jinja_env, template_content)
   ```

**Verification:**
```bash
# Check imports are correct
grep -r "from jinja2 import Environment" src/
# Should return ONLY: src/lattice_lock/utils/jinja.py

# Run affected tests
pytest tests/test_gauntlet_generator.py -v
pytest tests/test_cli_templates.py -v
```

**Success criteria:**
- No direct `Environment()` or `Template()` instantiation outside utility module
- All tests pass
- Snyk scan shows 4 fewer "autoescape unset" findings

---

### Task C2: Centralize Path Validation (Path Traversal Fix)

**Objective:** Fix 8 Snyk path traversal vulnerabilities by creating shared path validation utility.

**Phase 1: Create Utility Module**

1. Create new file: `src/lattice_lock/utils/safe_path.py`
2. Insert this complete module:

```python
"""Safe path handling utilities to prevent path traversal attacks.

This module provides utilities for validating user-provided paths
before performing file system operations.
"""
from pathlib import Path
from typing import Union

class PathTraversalError(ValueError):
    """Raised when a path attempts to escape its allowed root directory."""
    pass

def resolve_safe_path(
    user_path: Union[str, Path],
    root: Path,
    must_exist: bool = False,
    allow_outside_root: bool = False
) -> Path:
    """Resolve a user-provided path safely within an allowed root directory.

    Args:
        user_path: Path from user input (CLI argument, env var, config file)
        root: The allowed root directory (paths must be within this)
        must_exist: If True, raise FileNotFoundError if path doesn't exist
        allow_outside_root: If True, skip containment check (use cautiously)

    Returns:
        Resolved absolute path

    Raises:
        PathTraversalError: If path escapes root and allow_outside_root=False
        FileNotFoundError: If must_exist=True and path doesn't exist

    Example:
        >>> safe_path = resolve_safe_path("../../etc/passwd", Path.cwd())
        PathTraversalError: Path '/etc/passwd' is outside allowed root '/home/user/project'

        >>> safe_path = resolve_safe_path("configs/app.yaml", Path.cwd(), must_exist=True)
        PosixPath('/home/user/project/configs/app.yaml')
    """
    root = root.resolve()
    resolved = Path(user_path).expanduser().resolve()

    if not allow_outside_root:
        try:
            resolved.relative_to(root)
        except ValueError:
            raise PathTraversalError(
                f"Path '{resolved}' is outside allowed root '{root}'"
            )

    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved}")

    return resolved
```

**Phase 2: Update Affected Files**

For each file listed below, follow this pattern:

1. Add import at top:
   ```python
   from lattice_lock.utils.safe_path import resolve_safe_path, PathTraversalError
   ```

2. Find the vulnerable line (line numbers provided)
3. Wrap the path operation with validation
4. Add error handling

**File 1:** `src/lattice_lock/agents/prompt_architect/cli.py` (lines 172, 200)

Locate both lines that read user-provided paths. For each:

Before:
```python
output_path = Path(output_arg)  # Vulnerable
```

After:
```python
try:
    output_path = resolve_safe_path(
        output_arg,
        root=Path.cwd(),
        must_exist=False,
        allow_outside_root=False
    )
except PathTraversalError as e:
    click.echo(f"Error: {e}", err=True)
    raise click.Abort()
```

**File 2:** `src/lattice_lock_validator/structure.py` (lines 30, 179)

Similar pattern, but validation root should be the lattice file's parent:

```python
try:
    resolved_path = resolve_safe_path(
        user_provided_path,
        root=self.lattice_file.parent,
        must_exist=True
    )
except PathTraversalError as e:
    self.errors.append(f"Invalid path reference: {e}")
    return False
except FileNotFoundError as e:
    self.errors.append(f"Referenced file not found: {e}")
    return False
```

**File 3:** `scripts/prompt_tracker.py` (line 417)

```python
try:
    state_file = resolve_safe_path(
        args.state_file,
        root=Path.cwd(),
        must_exist=True
    )
except PathTraversalError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

**Files 4-8:** Apply same pattern to:
- `src/lattice_lock/sheriff.py` (line 422)
- `src/lattice_lock_orchestrator/grok_api.py` (line 105)
- `src/lattice_lock_gauntlet/plugin.py` (line 107)

**Phase 3: Add CLI Option for Legitimate External Paths**

For CLI commands that legitimately need to accept paths outside the project:

```python
@click.option(
    '--allow-outside-root',
    is_flag=True,
    help='Allow paths outside project directory (use with caution)'
)
def command_name(allow_outside_root: bool):
    path = resolve_safe_path(
        user_input,
        root=Path.cwd(),
        allow_outside_root=allow_outside_root
    )
```

**Verification:**
```bash
# Test path traversal protection
lattice-lock validate --schema-only ../../etc/passwd
# Should error with: "Path '/etc/passwd' is outside allowed root"

# Test legitimate relative paths still work
lattice-lock validate --schema-only configs/lattice.yaml
# Should succeed

# Run security scan
pytest tests/test_safe_path.py -v
```

**Success criteria:**
- All 8 Snyk path traversal findings are marked as resolved
- Legitimate relative paths continue to work
- Absolute paths outside project root are rejected with clear error message

---

### Group C: Pull Request Documentation

**After completing Tasks C1 and C2, generate:** `PR_GROUP_C_Security_Utilities.md`

**Required sections to populate:**

1. **Summary**: "Centralizes Jinja2 environment configuration and implements path validation utilities to address 12 security vulnerabilities (4 XSS, 8 path traversal)."

2. **Motivation and Context**:
   ```markdown
   ### Problem Statement
   - **Snyk Finding 1-4:** Missing autoescape configuration in Jinja2 templates (XSS vulnerability)
   - **Snyk Finding 5-12:** Direct path operations on user input (path traversal vulnerability)
   - **Root Cause:** No centralized security patterns for common operations
   - **Risk Level:** MEDIUM severity, exploitable in production

   ### Why This Matters
   - **Security:** Prevents XSS attacks via template injection
   - **Security:** Prevents unauthorized file system access
   - **Maintainability:** Single source of truth for security patterns
   - **Compliance:** Addresses security scan findings for production deployment
   ```

3. **Security Considerations**:
   ```markdown
   ### Vulnerabilities Addressed

   #### XSS via Template Injection (4 findings)
   - **Location:** Jinja2 Environment instantiation without autoescape
   - **Files:** generator.py, templates/__init__.py, prompt_generator.py
   - **Fix:** Centralized `create_template_env()` with explicit autoescape policy
   - **Policy:** Enabled for HTML/XML, disabled for code generation (YAML, Python)

   #### Path Traversal (8 findings)
   - **Attack Vector:** User input like `../../etc/passwd` accessing files outside project
   - **Files:** cli.py (2), structure.py (2), prompt_tracker.py, sheriff.py, grok_api.py, plugin.py
   - **Fix:** Centralized `resolve_safe_path()` with root containment check
   - **Mitigation:** All paths validated before file operations

   ### Security Scan Results
   ```bash
   # Before
   snyk test
   # 12 MEDIUM severity findings

   # After
   snyk test
   # 0 MEDIUM severity findings (12 resolved)
   ```

   ### New Security Measures
   - Path validation utility with explicit allow_outside_root flag
   - Jinja2 autoescape policy: enabled for user-facing content, disabled for code gen
   - PathTraversalError exception for clear security violation messages
   ```

4. **Detailed Changes**:

   Create subsections for EACH modified file showing:
   - Exact before/after code
   - Line numbers
   - Rationale for the specific change
   - How it addresses the security finding

   Example:
   ```markdown
   #### src/lattice_lock_gauntlet/generator.py

   **File:** `src/lattice_lock_gauntlet/generator.py`
   **Lines:** 20, 45
   **Snyk Finding:** SNYK-PYTHON-JINJA2-001 (Missing autoescape)

   **Changes:**
   - Removed direct Environment instantiation
   - Uses centralized create_template_env()

   **Before:**
   ```python
   from jinja2 import Environment, FileSystemLoader

   class GauntletGenerator:
       def __init__(self, …):
           self.env = Environment(
               loader=FileSystemLoader(template_dir)
           )  # No autoescape policy
   ```

   **After:**
   ```python
   from lattice_lock.utils.jinja import create_template_env

   class GauntletGenerator:
       def __init__(self, …):
           self.env = create_template_env(
               Path(__file__).parent / "templates"
           )  # Explicit autoescape policy
   ```

   **Rationale:**
   - Generator creates YAML test files (not HTML), autoescape would break syntax
   - Centralized config ensures consistent security policy
   - Explicit configuration makes security posture auditable
   ```

5. **Testing**:
   ```markdown
   ### Test Strategy
   - Unit tests for both utilities
   - Integration tests for path validation in CLI commands
   - Security tests attempting path traversal attacks
   - Regression tests ensuring templates still render correctly

   ### Tests Added/Modified
   - [x] `tests/test_safe_path.py` - New: Path validation unit tests
   - [x] `tests/test_jinja_utils.py` - New: Jinja2 utility unit tests
   - [x] `tests/test_gauntlet_generator.py` - Modified: Uses new Jinja utility
   - [x] `tests/test_path_security.py` - New: Integration tests for path attacks

   ### Verification Steps

   #### Security Test: Path Traversal Prevention
   ```bash
   # Attempt path traversal attack
   lattice-lock validate --schema-only ../../etc/passwd
   # Expected: PathTraversalError: Path '/etc/passwd' is outside allowed root

   # Legitimate path should work
   lattice-lock validate --schema-only configs/lattice.yaml
   # Expected: Success

   # Test with --allow-outside-root flag
   lattice-lock validate --schema-only /tmp/test.yaml --allow-outside-root
   # Expected: Success (explicit override)
   ```

   #### Security Test: Template XSS Prevention
   ```bash
   # Test that autoescape works for HTML
   python -c "
   from lattice_lock.utils.jinja import create_template_env
   from pathlib import Path
   env = create_template_env(Path('/tmp'))
   template = env.from_string('<div>{{ content }}</div>')
   result = template.render(content='<script>alert(1)</script>')
   assert '&lt;script&gt;' in result  # Should be escaped
   "
   # Expected: Success (XSS attempt escaped)

   # Test that autoescape is disabled for code generation
   python -c "
   from lattice_lock.utils.jinja import create_template_env
   env = create_template_env(Path('/tmp'))
   template = env.from_string('def test_{{ name }}(): pass')
   result = template.render(name='user<input>')
   assert '<' in result  # Should NOT be escaped in code
   "
   # Expected: Success (code generation unaffected)
   ```

   ### Test Results
   - All existing tests pass (0 regressions)
   - New security tests pass (12 attack scenarios blocked)
   - Performance impact: negligible (<1ms per path validation)
   ```

6. **Files Modified**:
   ```
   - [x] src/lattice_lock/utils/jinja.py - Created: Centralized Jinja2 config
   - [x] src/lattice_lock/utils/safe_path.py - Created: Path validation utility
   - [x] src/lattice_lock_cli/templates/__init__.py - Uses new Jinja utility
   - [x] src/lattice_lock_gauntlet/generator.py - Uses new Jinja utility
   - [x] src/lattice_lock_agents/prompt_architect/subagents/prompt_generator.py - Uses new Jinja utility
   - [x] src/lattice_lock/agents/prompt_architect/cli.py - Uses path validation (2 locations)
   - [x] src/lattice_lock_validator/structure.py - Uses path validation (2 locations)
   - [x] scripts/prompt_tracker.py - Uses path validation
   - [x] src/lattice_lock/sheriff.py - Uses path validation
   - [x] src/lattice_lock_orchestrator/grok_api.py - Uses path validation
   - [x] src/lattice_lock_gauntlet/plugin.py - Uses path validation
   ```

7. **Dependencies**: None (uses only stdlib + existing dependencies)

8. **Performance Impact**:
   ```markdown
   ### Expected Performance Changes
   - Path validation adds ~0.5ms per file operation (negligible)
   - Jinja2 environment creation happens once at startup (no runtime impact)
   - Memory overhead: <1KB for utility modules

   ### Benchmark Results
   ```bash
   # Before: Direct path operations
   python -m timeit -s "from pathlib import Path" "Path('test.yaml').resolve()"
   # 1000000 loops, best of 5: 0.234 usec per loop

   # After: Safe path validation
   python -m timeit -s "from lattice_lock.utils.safe_path import resolve_safe_path; from pathlib import Path" "resolve_safe_path('test.yaml', Path.cwd())"
   # 100000 loops, best of 5: 0.756 usec per loop

   # Delta: +0.5 usec per operation (acceptable for security benefit)
   ```
   ```

9. **Review Checklist - Security-Specific Items**:
   ```markdown
   - [ ] All path operations use resolve_safe_path()
   - [ ] No direct Environment() instantiation exists
   - [ ] Template autoescape policy is appropriate for content type
   - [ ] PathTraversalError messages don't leak sensitive path information
   - [ ] allow_outside_root flag is only used where necessary
   - [ ] Security tests cover edge cases (symlinks, relative paths, URL-encoded)
   ```

---

## Group D: Documentation Fixes

### Task D1: Fix Import Paths in Documentation

**Objective:** Correct 6+ import statement errors across documentation files.

**File 1:** `README.md` (lines 17-25)

Locate the "Quick Start" code example. It currently shows:

```python
from src.lattice_lock_orchestrator import ModelOrchestrator
```

Replace entire code block with:

```python
from lattice_lock_orchestrator.core import ModelOrchestrator
from lattice_lock_orchestrator.types import TaskType

# Initialize orchestrator
orchestrator = ModelOrchestrator()

# Route a task
result = orchestrator.route_task(
    task_description="Analyze sentiment of customer feedback",
    task_type=TaskType.TEXT_CLASSIFICATION
)
```

**File 2:** `cli_commands/cli_orchestrator.md` (lines 39-42)

Current content:
```python
from model_orchestrator import ModelOrchestrator
from zen_mcp_bridge import ModelRouter
```

Replace with:
```python
from lattice_lock_orchestrator.core import ModelOrchestrator
from lattice_lock_orchestrator.types import TaskType, ModelCapability
```

**File 3:** `developer_documentation/getting_started/installation.md`

Search for version verification output. Find section showing:
```
Lattice Lock Framework v1.0.0
```

Replace with:
```
Lattice Lock Framework v2.1.0
```

**Verification:**
```bash
# Test import statements work
python -c "from lattice_lock_orchestrator.core import ModelOrchestrator; print('OK')"

# Check docs build without errors (if using mkdocs or sphinx)
mkdocs build --strict
```

**Success criteria:**
- All import statements in documentation match actual package structure
- Version numbers are consistent (v2.1.0)
- Code examples can be copy-pasted and executed successfully

---

### Task D2: Generate Missing CLI Documentation

**Objective:** Create documentation for 4 undocumented commands.

**For each command, follow this template:**

**Step 1: Extract Command Information**

Run:
```bash
lattice-lock <COMMAND> --help > /tmp/<COMMAND>_help.txt
```

**Step 2: Create Documentation File**

Create: `developer_documentation/reference/cli/<COMMAND>.md`

Use this template structure:

```markdown
# `lattice-lock <COMMAND>`

## Synopsis

```bash
lattice-lock <COMMAND> [OPTIONS]
```

## Description

[2-3 sentence description of what the command does]

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--option-name` | string | none | Option description |

## Examples

### Basic Usage

```bash
lattice-lock <COMMAND>
```

### With Options

```bash
lattice-lock <COMMAND> --option value
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |

## See Also

- [`lattice-lock <related-command>`](<related-command>.md)
```

**Commands to document:**

1. **compile** - Create file: `developer_documentation/reference/cli/compile.md`
   - Run: `lattice-lock compile --help`
   - Fill template with extracted information

2. **admin** - Create file: `developer_documentation/reference/cli/admin.md`
   - Run: `lattice-lock admin --help`
   - Document the `dashboard` subcommand separately

3. **orchestrator** - Create file: `developer_documentation/reference/cli/orchestrator.md`
   - Run: `lattice-lock orchestrator --help`
   - Document all subcommands: `list`, `analyze`, `route`, etc.

4. **feedback** - Create file: `developer_documentation/reference/cli/feedback.md`
   - Run: `lattice-lock feedback --help`
   - Document category and priority options

**Step 3: Update Index**

Open: `developer_documentation/reference/cli/index.md`

Locate the Commands table, add missing entries:

```markdown
| Command | Description |
|---------|-------------|
| … existing commands … |
| [`compile`](compile.md) | Generate code artifacts from lattice configurations |
| [`admin`](admin.md) | Administrative commands (dashboard, users, etc.) |
| [`orchestrator`](orchestrator.md) | Model orchestration and routing commands |
| [`feedback`](feedback.md) | Submit feedback about CLI or framework issues |
```

**Verification:**
```bash
# Check all documented commands exist
for cmd in compile admin orchestrator feedback; do
  lattice-lock $cmd --help || echo "MISSING: $cmd"
done

# Verify markdown syntax
markdownlint developer_documentation/reference/cli/*.md
```

**Success criteria:**
- Every command shown in `lattice-lock --help` has a documentation file
- Index table is complete and sorted logically
- All markdown files follow consistent structure

---

### Group D: Pull Request Documentation

**After completing Tasks D1 and D2, generate:** `PR_GROUP_D_Documentation_Fixes.md`

**Required sections to populate:**

1. **Summary**: "Corrects import paths, version numbers, and command references across documentation; adds missing CLI command documentation for 4 undocumented commands."

2. **Motivation and Context**:
   ```markdown
   ### Problem Statement
   - **Broken Examples:** Code examples in README use incorrect import paths (src.lattice_lock_*)
   - **Version Drift:** Installation docs show v1.0.0 but actual version is v2.1.0
   - **Missing Docs:** 4 CLI commands (compile, admin, orchestrator, feedback) have no reference documentation
   - **User Impact:** New users cannot successfully run documentation examples
   - **Onboarding:** First-time contributors cannot find CLI command documentation

   ### Why This Matters
   - **Developer Experience:** Documentation is first impression for new users
   - **Support Burden:** Incorrect examples generate support tickets
   - **Adoption:** Missing docs prevent users from discovering features
   - **Maintainability:** Docs drift creates technical debt
   ```

3. **Detailed Changes**:

   For each documentation file:
   ```markdown
   #### README.md (Quick Start Example)

   **File:** `README.md`
   **Lines:** 17-25
   **Issue:** Import path uses src. prefix (internal structure)

   **Before:**
   ```python
   from src.lattice_lock_orchestrator import ModelOrchestrator

   orchestrator = ModelOrchestrator()
   ```

   **After:**
   ```python
   from lattice_lock_orchestrator.core import ModelOrchestrator
   from lattice_lock_orchestrator.types import TaskType

   orchestrator = ModelOrchestrator()
   result = orchestrator.route_task(
       task_description="Analyze sentiment",
       task_type=TaskType.TEXT_CLASSIFICATION
   )
   ```

   **Validation:**
   ```bash
   # Test import works after pip install
   python -c "from lattice_lock_orchestrator.core import ModelOrchestrator"
   # Exit code: 0 ✓
   ```

   **Impact:** First-time users can copy-paste and run example successfully
   ```

   Repeat for all modified files.

4. **Testing**:
   ```markdown
   ### Test Strategy
   - Manual validation: Copy each code example and execute in fresh Python environment
   - Link validation: Check all internal markdown links resolve
   - Command validation: Run every documented CLI command with --help
   - Version validation: Grep for hardcoded version numbers

   ### Tests Added/Modified
   - [x] `tests/test_documentation_examples.py` - New: Extracts and runs code examples from docs
   - [x] `tests/test_markdown_links.py` - New: Validates internal documentation links

   ### Manual Verification Steps

   #### Test Import Examples
   ```bash
   # Create isolated environment
   python -m venv /tmp/doc_test
   source /tmp/doc_test/bin/activate
   pip install -e .

   # Test README example
   python << 'EOF'
   from lattice_lock_orchestrator.core import ModelOrchestrator
   from lattice_lock_orchestrator.types import TaskType
   orchestrator = ModelOrchestrator()
   print("✓ README example works")
   EOF

   # Test cli_orchestrator.md example
   python << 'EOF'
   from lattice_lock_orchestrator.core import ModelOrchestrator
   from lattice_lock_orchestrator.types import TaskType, ModelCapability
   print("✓ CLI orchestrator example works")
   EOF
   ```

   #### Test CLI Documentation Accuracy
   ```bash
   # Verify each documented command exists
   for cmd in compile admin orchestrator feedback; do
     echo "Testing: lattice-lock $cmd"
     lattice-lock $cmd --help > /tmp/help_output_$cmd.txt

     # Compare with documented options in .md file
     # (manual inspection or automated diff)
   done

   # Verify documented options match actual options
   diff <(grep "^\s*\`--" developer_documentation/reference/cli/compile.md | sort) \
        <(lattice-lock compile --help | grep "^\s*--" | sort)
   # Expected: No diff
   ```

   #### Test Documentation Links
   ```bash
   # Install markdown link checker
   npm install -g markdown-link-check

   # Check all docs for broken links
   find developer_documentation/ -name "*.md" -exec markdown-link-check {} \;
   # Expected: 0 dead links
   ```

   ### Test Results
   **Before Changes:**
   - Import examples: 6 failures (ModuleNotFoundError)
   - CLI help output: 4 commands undocumented
   - Broken links: 12 (references to non-existent files)

   **After Changes:**
   - Import examples: 0 failures ✓
   - CLI help output: 100% coverage ✓
   - Broken links: 0 ✓
   ```

5. **Documentation Updates** (meta-documentation):
   ```markdown
   ### New Documentation Files Created
   - [x] `developer_documentation/reference/cli/compile.md` - Complete CLI reference
   - [x] `developer_documentation/reference/cli/admin.md` - Complete CLI reference
   - [x] `developer_documentation/reference/cli/orchestrator.md` - Complete CLI reference
   - [x] `developer_documentation/reference/cli/feedback.md` - Complete CLI reference

   ### Documentation Files Updated
   - [x] `README.md` - Fixed import paths, added complete example
   - [x] `cli_commands/cli_orchestrator.md` - Fixed import paths
   - [x] `developer_documentation/getting_started/installation.md` - Updated version to v2.1.0
   - [x] `developer_documentation/reference/cli/index.md` - Added missing command entries

   ### Documentation Standards Applied
   All new CLI documentation follows the template:
   - Synopsis with command syntax
   - Description (2-3 sentences)
   - Options table with types and defaults
   - Examples (basic + advanced)
   - Exit codes
   - See Also links
   ```

6. **Files Modified**:
   ```
   Documentation Content:
   - [x] README.md - Fixed import paths (lines 17-25)
   - [x] cli_commands/cli_orchestrator.md - Fixed import paths (lines 39-42)
   - [x] developer_documentation/getting_started/installation.md - Version update
   - [x] developer_documentation/reference/cli/index.md - Added 4 commands to index

   Documentation Created:
   - [x] developer_documentation/reference/cli/compile.md - New file
   - [x] developer_documentation/reference/cli/admin.md - New file
   - [x] developer_documentation/reference/cli/orchestrator.md - New file
   - [x] developer_documentation/reference/cli/feedback.md - New file
   ```

7. **Breaking Changes**: None (documentation-only changes)

8. **Screenshots/Recordings**:
   ```markdown
   ### Before: Broken Import Example
   ```bash
   $ python
   >>> from src.lattice_lock_orchestrator import ModelOrchestrator
   ModuleNotFoundError: No module named 'src'
   ```

   ### After: Working Import Example
   ```bash
   $ python
   >>> from lattice_lock_orchestrator.core import ModelOrchestrator
   >>> print("Success!")
   Success!
   ```

   ### CLI Help Output Examples
   [Include terminal screenshots showing `lattice-lock compile --help` etc.]
   ```

9. **Reviewer Notes**:
   ```markdown
   ### Focus Areas
   - **Accuracy:** Verify import statements work in fresh environment
   - **Completeness:** Check all CLI commands now have documentation
   - **Consistency:** Ensure all command docs follow same template structure
   - **Links:** Spot-check internal documentation links

   ### How to Review
   1. Clone repo to fresh directory
   2. Create new virtual environment
   3. Install with `pip install -e .`
   4. Copy-paste each code example from docs and run
   5. Run each documented CLI command with documented options
   6. Check that documented behavior matches actual behavior
   ```

---

## Group E: Code Hygiene

### Task E1: Replace Silent Error Handling

**Objective:** Fix 6 instances of bare `except: pass` that swallow errors silently.

**File 1:** `src/lattice_lock_agents/prompt_architect/subagents/spec_analyzer.py`

**Lines 113-114:**

Current code:
```python
except Exception:
    pass
```

Context: This is in LLM enhancement fallback logic.

Replace with:
```python
except Exception as e:
    logger.warning(
        f"LLM enhancement failed for spec analysis: {e}. "
        f"Falling back to basic parsing."
    )
    # Continue with basic parsing below
```

**Lines 135-136, 141-142, 205-206:**

Apply same pattern to each location. Read surrounding code to understand context, then add appropriate logging message.

**File 2:** `src/lattice_lock_agents/prompt_architect/subagents/tool_matcher.py` (lines 56-61)

Current code:
```python
except Exception:
    pass  # Ownership conflict
```

Context: This handles ownership conflicts between tools.

Replace with:
```python
except OwnershipConflictError as e:
    logger.warning(
        f"Ownership conflict for task {task.id}: "
        f"files owned by both {forced_owner} and {owner}. "
        f"Assigning to first owner: {forced_owner}"
    )
    # Record conflict in task metadata
    task.metadata['ownership_conflict'] = {
        'owners': [forced_owner, owner],
        'resolution': 'assigned_to_first'
    }
```

**General Pattern:**

For each bare `except: pass`:
1. Add `as e` to capture exception
2. Add logger.warning() with descriptive message
3. Add comment explaining fallback behavior
4. If appropriate, record the error in metadata/state

**Verification:**
```bash
# Check no bare pass remains in error handlers
grep -n "except.*:$" -A 1 src/ | grep "pass$"
# Should return empty

# Run tests to ensure fallback logic works
pytest tests/test_spec_analyzer.py -v
pytest tests/test_tool_matcher.py -v
```

**Success criteria:**
- All error handlers log warnings
- Tests pass
- Log output shows warning messages when errors occur

---

### Task E2: Fix Placeholder Return Values

**Objective:** Replace placeholder `pass` statement in code generation with explicit error.

**File:** `src/lattice_lock_gauntlet/generator.py` (line 93)

**Current code:**
```python
return "pass  # Unknown constraint"
```

**Context:** This is in constraint translation for test generation. Returning `pass` creates a test that does nothing.

**Replace with:**

```python
constraint_name = clause.constraint
supported = ['gt', 'lt', 'gte', 'lte', 'unique', 'regex', 'length']
raise ValueError(
    f"Unknown constraint type '{constraint_name}' for field '{clause.field}'. "
    f"Supported constraints: {', '.join(supported)}"
)
```

**Alternative (if you prefer failing tests):**

```python
constraint_name = clause.constraint
field_name = clause.field
return (
    f"pytest.fail("
    f"'Unsupported constraint: {constraint_name} for field {field_name}. "
    f"Please implement this constraint type or update lattice.yaml')"
)
```

**Decision point:** Which approach to use?
- First approach: Fails at generation time (safer, catches issues early)
- Second approach: Generates failing test (provides visibility in test results)

**Verification:**
```bash
# Test with invalid constraint
echo "
constraints:
  - field: username
    constraint: invalid_constraint_type
" > /tmp/test_lattice.yaml

lattice-lock test --generate --file /tmp/test_lattice.yaml
# Should show clear error message, not generate "pass" statement

# Run existing tests
pytest tests/test_gauntlet_generator.py -v
```

**Success criteria:**
- Invalid constraints produce explicit errors
- Error messages guide users to valid constraint types
- No generated test files contain bare `pass` statements

---

### Group E: Pull Request Documentation

**After completing Tasks E1 and E2, generate:** `PR_GROUP_E_Code_Hygiene.md`

**Required sections to populate:**

1. **Summary**: "Replaces 6 instances of silent error handling with explicit logging and converts placeholder code generation to fail-fast error reporting."

2. **Motivation and Context**:
   ```markdown
   ### Problem Statement
   - **Silent Failures:** 6 locations swallow exceptions with bare `except: pass`
   - **Debug Difficulty:** When errors occur, no logs indicate what failed
   - **Placeholder Code:** Test generator returns `pass` for unknown constraints
   - **False Positives:** Tests with `pass` appear to succeed but test nothing

   ### Why This Matters
   - **Debugging:** Silent failures make troubleshooting nearly impossible
   - **Observability:** Logging provides visibility into fallback behaviors
   - **Test Validity:** Placeholder tests give false confidence
   - **User Experience:** Explicit errors guide users to fix configuration issues

   ### Impact Areas
   - Prompt architect LLM fallback behavior (spec_analyzer.py)
   - Tool ownership conflict resolution (tool_matcher.py)
   - Test generation validation (generator.py)
   ```

3. **Detailed Changes**:

   ```markdown
   #### spec_analyzer.py - LLM Enhancement Fallback

   **File:** `src/lattice_lock_agents/prompt_architect/subagents/spec_analyzer.py`
   **Lines:** 113-114, 135-136, 141-142, 205-206 (4 locations)
   **Issue:** LLM enhancement failures are silently swallowed

   **Context:** The spec analyzer attempts to use an LLM to enhance specification parsing. If the LLM fails (API timeout, rate limit, invalid response), it should fall back to basic parsing and log the failure.

   **Before (Line 113-114):**
   ```python
   try:
       enhanced_spec = self._enhance_with_llm(spec_content)
       return enhanced_spec
   except Exception:
       pass  # Silent fallback to basic parsing

   # Basic parsing continues here
   return self._basic_parse(spec_content)
   ```

   **After (Line 113-114):**
   ```python
   try:
       enhanced_spec = self._enhance_with_llm(spec_content)
       return enhanced_spec
   except Exception as e:
       logger.warning(
           f"LLM enhancement failed for spec analysis: {e}. "
           f"Falling back to basic parsing."
       )
       # Continue with basic parsing below

   return self._basic_parse(spec_content)
   ```

   **Impact:**
   - Developers can now see when LLM enhancement fails
   - Can diagnose API issues, rate limits, or network problems
   - Fallback behavior is now documented in logs

   **Similar Changes Applied To:**
   - Line 135-136: Constraint extraction fallback
   - Line 141-142: Entity recognition fallback
   - Line 205-206: Relationship mapping fallback

   ---

   #### tool_matcher.py - Ownership Conflict Resolution

   **File:** `src/lattice_lock_agents/prompt_architect/subagents/tool_matcher.py`
   **Lines:** 56-61
   **Issue:** Tool ownership conflicts silently resolved without tracking

   **Context:** When multiple tools claim ownership of the same files, the system assigns to the first owner but doesn't record the conflict or explain the resolution.

   **Before:**
   ```python
   try:
       if task.owner and task.owner != tool.owner:
           raise OwnershipConflictError(…)
   except Exception:
       pass  # Ownership conflict - silently ignored
   ```

   **After:**
   ```python
   try:
       if task.owner and task.owner != tool.owner:
           raise OwnershipConflictError(…)
   except OwnershipConflictError as e:
       logger.warning(
           f"Ownership conflict for task {task.id}: "
           f"files owned by both {forced_owner} and {owner}. "
           f"Assigning to first owner: {forced_owner}"
       )
       # Record conflict in task metadata for audit trail
       task.metadata['ownership_conflict'] = {
           'owners': [forced_owner, owner],
           'resolution': 'assigned_to_first',
           'timestamp': datetime.now().isoformat()
       }
   ```

   **Impact:**
   - Ownership conflicts are now visible in logs
   - Audit trail in task metadata for debugging
   - Users understand why tasks are assigned to specific tools

   ---

   #### generator.py - Constraint Validation

   **File:** `src/lattice_lock_gauntlet/generator.py`
   **Lines:** 93
   **Issue:** Unknown constraints generate placeholder `pass` statements

   **Context:** When test generator encounters an unknown constraint type, it generates a test containing only `pass`, which appears to succeed but tests nothing.

   **Before:**
   ```python
   def _translate_constraint(self, clause):
       if clause.constraint == 'gt':
           return f"assert value > {clause.value}"
       elif clause.constraint == 'lt':
           return f"assert value < {clause.value}"
       # … other constraints …
       else:
           return "pass  # Unknown constraint"  # Silent placeholder
   ```

   **After (Option A: Fail Fast):**
   ```python
   def _translate_constraint(self, clause):
       if clause.constraint == 'gt':
           return f"assert value > {clause.value}"
       elif clause.constraint == 'lt':
           return f"assert value < {clause.value}"
       # … other constraints …
       else:
           constraint_name = clause.constraint
           supported = ['gt', 'lt', 'gte', 'lte', 'unique', 'regex', 'length']
           raise ValueError(
               f"Unknown constraint type '{constraint_name}' for field '{clause.field}'. "
               f"Supported constraints: {', '.join(supported)}"
           )
   ```

   **After (Option B: Failing Test):**
   ```python
   def _translate_constraint(self, clause):
       # … existing constraints …
       else:
           constraint_name = clause.constraint
           field_name = clause.field
           return (
               f"pytest.fail("
               f"'Unsupported constraint: {constraint_name} for field {field_name}. "
               f"Please implement this constraint type or update lattice.yaml')"
           )
   ```

   **Decision:** This PR uses **Option A (Fail Fast)** because:
   - Catches configuration errors at generation time (earlier)
   - Prevents false sense of security from passing tests
   - Clear error message guides user to fix lattice.yaml
   - Fails immediately, not after running entire test suite

   **Impact:**
   - Invalid constraints caught immediately
   - Clear error messages guide users to valid options
   - No more false-passing tests
   ```

4. **Testing**:
   ```markdown
   ### Test Strategy
   - Unit tests for each modified error handler
   - Integration tests triggering fallback paths
   - Log output validation
   - Error message clarity testing

   ### Tests Added/Modified
   - [x] `tests/test_spec_analyzer_fallback.py` - New: Tests LLM fallback logging
   - [x] `tests/test_tool_matcher_conflicts.py` - Modified: Validates conflict logging
   - [x] `tests/test_generator_constraints.py` - Modified: Tests constraint validation
   - [x] `tests/test_error_logging.py` - New: Validates log output format

   ### Manual Verification Steps

   #### Test Error Logging (spec_analyzer.py)
   ```bash
   # Set up test environment
   export LATTICE_LOG_LEVEL=DEBUG

   # Trigger LLM failure (mock API timeout)
   python << 'EOF'
   import logging
   from lattice_lock_agents.prompt_architect.subagents.spec_analyzer import SpecAnalyzer

   logging.basicConfig(level=logging.DEBUG)

   analyzer = SpecAnalyzer()
   # Mock API failure by disconnecting network or using invalid API key
   result = analyzer.analyze("test_spec.yaml")

   # Expected log output:
   # WARNING - LLM enhancement failed for spec analysis: ConnectionError…
   # INFO - Falling back to basic parsing
   EOF
   ```

   #### Test Ownership Conflict Logging (tool_matcher.py)
   ```bash
   # Create scenario with ownership conflict
   python << 'EOF'
   from lattice_lock_agents.prompt_architect.subagents.tool_matcher import ToolMatcher

   matcher = ToolMatcher()
   # Create task with overlapping file ownership
   task = Task(id="test", files=["shared.py"])
   tool1 = Tool(name="formatter", owner="tool-a")
   tool2 = Tool(name="linter", owner="tool-b")

   # Both tools claim same files
   result = matcher.assign(task, [tool1, tool2])

   # Expected log output:
   # WARNING - Ownership conflict for task test: files owned by both tool-a and tool-b
   # Expected metadata:
   assert 'ownership_conflict' in task.metadata
   assert task.metadata['ownership_conflict']['owners'] == ['tool-a', 'tool-b']
   EOF
   ```

   #### Test Constraint Validation (generator.py)
   ```bash
   # Test with invalid constraint
   cat > /tmp/test_lattice.yaml << 'EOF'
   tests:
     - name: user_validation
       constraints:
         - field: username
           constraint: invalid_type
           value: 10
   EOF

   # Run generator
   lattice-lock test --generate --file /tmp/test_lattice.yaml

   # Expected output:
   # ERROR: Unknown constraint type 'invalid_type' for field 'username'.
   # Supported constraints: gt, lt, gte, lte, unique, regex, length
   # Exit code: 1

   # Test with valid constraint
   cat >

/tmp/test_lattice.yaml << 'EOF'
   tests:
     - name: user_validation
       constraints:
         - field: age
           constraint: gt
           value: 18
   EOF

   lattice-lock test --generate --file /tmp/test_lattice.yaml
   # Expected: Success, generates valid test
   ```

   ### Test Results

   **Before Changes:**
   ```
   # spec_analyzer.py - No log output on LLM failure
   $ pytest tests/test_spec_analyzer.py -v -s
   …………………………..
   32 passed (no warnings about failures)

   # tool_matcher.py - No visibility into conflicts
   $ pytest tests/test_tool_matcher.py -v -s
   ……………………
   24 passed (conflicts silently resolved)

   # generator.py - Invalid constraints generate pass statements
   $ lattice-lock test --generate --file bad_lattice.yaml
   Generated 5 tests successfully
   $ pytest generated_tests/
   ===== 5 passed in 0.23s =====  # False positives!
   ```

   **After Changes:**
   ```
   # spec_analyzer.py - Clear warning logs
   $ pytest tests/test_spec_analyzer.py -v -s
   …………………………..
   WARNING - LLM enhancement failed: timeout
   WARNING - LLM enhancement failed: rate limit
   32 passed, 2 warnings (fallback behavior visible)

   # tool_matcher.py - Conflict visibility
   $ pytest tests/test_tool_matcher.py -v -s
   ……………………
   WARNING - Ownership conflict for task test_123
   24 passed, 3 warnings (conflicts logged and tracked)

   # generator.py - Explicit error on invalid constraints
   $ lattice-lock test --generate --file bad_lattice.yaml
   ERROR: Unknown constraint type 'invalid_type' for field 'username'.
   Supported constraints: gt, lt, gte, lte, unique, regex, length

   $ echo $?
   1  # Proper error exit code
   ```

   ### Coverage Impact
   - **Before:** Error handling paths had 0% coverage (untestable due to silent failures)
   - **After:** Error handling paths have 85% coverage
   - **Net Change:** +8% overall project coverage
   ```

5. **Code Quality Improvements**:
   ```markdown
   ### Code Smells Eliminated
   - **Bare except:** All 6 instances replaced with specific exception handling
   - **Magic comments:** "# pass" comments replaced with explicit behavior
   - **Silent failures:** All error paths now have observable side effects
   - **False positives:** Placeholder tests eliminated

   ### Observability Improvements
   - **Log levels:** INFO for expected fallbacks, WARNING for conflicts
   - **Log format:** Consistent structure: `{component} failed: {reason}. {action}`
   - **Metadata tracking:** Conflicts recorded in structured data
   - **Error messages:** Include actionable next steps

   ### Developer Experience
   - **Debugging:** Logs provide clear breadcrumbs for troubleshooting
   - **Monitoring:** Can alert on WARNING logs in production
   - **Testing:** Error paths are now testable and covered
   ```

6. **Files Modified**:
   ```
   - [x] src/lattice_lock_agents/prompt_architect/subagents/spec_analyzer.py - Fixed 4 silent error handlers
   - [x] src/lattice_lock_agents/prompt_architect/subagents/tool_matcher.py - Fixed ownership conflict logging
   - [x] src/lattice_lock_gauntlet/generator.py - Replaced placeholder with validation
   - [x] tests/test_spec_analyzer_fallback.py - New test coverage
   - [x] tests/test_tool_matcher_conflicts.py - Enhanced test coverage
   - [x] tests/test_generator_constraints.py - Added validation tests
   ```

7. **Breaking Changes**:
   ```markdown
   ### Behavioral Changes
   - **generator.py constraint handling:**
     - **Before:** Unknown constraints generated tests with `pass` (always passing)
     - **After:** Unknown constraints raise ValueError at generation time
     - **Migration:** Users with invalid constraints in lattice.yaml must fix or remove them
     - **Detection:** Run `lattice-lock test --generate` to identify issues

   ### Non-Breaking Changes
   - All logging additions are backward compatible
   - Fallback behaviors unchanged (only visibility added)
   - No API signature changes
   ```

8. **Deployment Notes**:
   ```markdown
   ### Post-Deployment Monitoring
   Monitor these new log patterns:
   - `WARNING - LLM enhancement failed` - Check API connectivity/rate limits
   - `WARNING - Ownership conflict` - Review tool configuration if frequent
   - `ERROR: Unknown constraint type` - User education opportunity

   ### Expected Log Volume Increase
   - Baseline: ~100 log lines/hour
   - Post-deployment: ~150 log lines/hour (mostly INFO/DEBUG)
   - WARNING logs: <5/hour in normal operation

   ### Rollback Plan
   If excessive logging causes issues:
   1. Set `LATTICE_LOG_LEVEL=ERROR` environment variable
   2. Revert PR (all changes are additive, no data loss)
   ```

---

## Group F: Security Hardening (Decision Required)

### Task F1: Fix XML External Entity (XXE) Vulnerability

**Objective:** Resolve 15 Snyk findings for insecure XML parsing.

**⚠️ DECISION REQUIRED BEFORE PROCEEDING:**

You must choose one of these approaches:

**Option A: Add defusedxml dependency (Recommended)**
- Pros: Fixes all vulnerabilities, supports Python 3.10+
- Cons: Adds external dependency

**Option B: Drop Python 3.10 support**
- Pros: No new dependencies (Python 3.11+ has secure XML by default)
- Cons: Breaks compatibility for users on Python 3.10

**If you choose Option A, proceed with these instructions:**

**Step 1: Update Dependencies**

Open: `pyproject.toml`

Locate the `[project.dependencies]` section.

Add new line:
```toml
"defusedxml>=0.7.1",
```

**Step 2: Update Sheriff Formatter**

File: `src/lattice_lock_sheriff/formatters.py`

Current import (approximate line 15):
```python
from xml.dom import minidom
```

Replace with:
```python
from defusedxml import minidom
```

**Step 3: Update Test Files**

Search for all test files using XML parsing:
```bash
grep -r "from xml.etree" tests/
```

For each file found, replace:
```python
from xml.etree.ElementTree import fromstring
```

With:
```python
from defusedxml.ElementTree import fromstring
```

**Step 4: Update Any Other XML Usage**

Search entire codebase:
```bash
grep -r "import xml" src/
```

For each match:
1. Check if it uses `ElementTree`, `minidom`, or XML parsing
2. Replace with defusedxml equivalent

**Verification:**
```bash
# Install new dependency
pip install -e ".[dev]"

# Run security scan
pip install safety
safety check

# Run tests that use XML
pytest tests/ -k xml -v

# Verify Snyk findings are resolved
snyk test
```

**Success criteria:**
- All imports changed to defusedxml
- Tests pass
- Snyk shows 15 fewer XML parser vulnerabilities

**If you choose Option B (drop Python 3.10):**

1. Update `pyproject.toml`:
   ```toml
   requires-python = ">=3.11"
   ```

2. Update CI workflows to remove Python 3.10 from test matrix

3. Add migration note to CHANGELOG.md

---

### Task F2: Remove Hardcoded Secrets in Tests

**Objective:** Fix 14 Snyk LOW findings for hardcoded passwords in test files.

**Phase 1: Create Test Fixtures**

File: `tests/conftest.py`

Add these fixtures (or append if file exists):

```python
import os
import pytest

@pytest.fixture
def test_password():
    """Provide test password from environment or safe default.

    Set TEST_PASSWORD environment variable to use a specific value.
    Default is clearly marked as non-production.
    """
    return os.getenv("TEST_PASSWORD", "test-fixture-not-real-password-12345")

@pytest.fixture
def test_api_key():
    """Provide test API key from environment or safe default.

    Set TEST_API_KEY environment variable to use a specific value.
    Default is clearly marked as non-production.
    """
    return os.getenv("TEST_API_KEY", "test-fixture-not-real-key-67890")

@pytest.fixture
def test_secret_token():
    """Provide test secret token from environment or safe default."""
    return os.getenv("TEST_SECRET_TOKEN", "test-fixture-not-real-token-abcdef")
```

**Phase 2: Update Test Files**

For each test file with hardcoded secrets:

**File 1:** `tests/test_admin_auth.py`

Find lines with hardcoded passwords (search for strings like `"password123"` or `"secret"`).

Before:
```python
def test_admin_login():
    response = client.post("/admin/login", json={
        "username": "admin",
        "password": "password123"  # Hardcoded secret
    })
```

After:
```python
def test_admin_login(test_password):
    response = client.post("/admin/login", json={
        "username": "admin",
        "password": test_password
    })
```

**File 2:** `tests/test_error_middleware.py`

Apply same pattern to any hardcoded API keys or tokens.

**General Pattern:**

1. Add fixture parameter to test function signature
2. Replace hardcoded string with fixture variable
3. If test requires specific format, document in fixture docstring

**Phase 3: Update CI Environment**

File: `.github/workflows/python-app.yml`

In the test step, add environment variables:

```yaml
- name: Test with pytest
  env:
    TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
    TEST_API_KEY: ${{ secrets.TEST_API_KEY }}
    TEST_SECRET_TOKEN: ${{ secrets.TEST_SECRET_TOKEN }}
  run: |
    pytest tests/ -v --tb=short
```

**Note:** You don't need to actually set GitHub secrets for these. The fixtures provide safe defaults. This structure just allows overriding if needed.

**Verification:**
```bash
# Check no hardcoded secrets remain
grep -r "password.*=.*['\"]" tests/ | grep -v fixture
grep -r "api_key.*=.*['\"]" tests/ | grep -v fixture
grep -r "secret.*=.*['\"]" tests/ | grep -v fixture
# All should return empty or only fixture definitions

# Run tests with fixtures
pytest tests/test_admin_auth.py -v
pytest tests/test_error_middleware.py -v

# Run with custom values
TEST_PASSWORD="custom123" pytest tests/test_admin_auth.py -v
```

**Success criteria:**
- No hardcoded passwords/secrets in test files
- All tests pass with fixture defaults
- Snyk shows 14 fewer hardcoded secret findings
- Tests can optionally use environment variables for specific test scenarios

---

### Group F: Pull Request Documentation

**After completing Tasks F1 and F2, generate:** `PR_GROUP_F_Security_Hardening.md`

**Required sections to populate:**

1. **Summary**: "[Option A: Adds defusedxml dependency and migrates all XML parsing] OR [Option B: Drops Python 3.10 support] to resolve 15 XXE vulnerabilities; replaces hardcoded test secrets with environment-based fixtures to resolve 14 credential exposure findings."

2. **Motivation and Context**:
   ```markdown
   ### Problem Statement
   - **XXE Vulnerability (15 findings):** XML parser vulnerable to external entity attacks
   - **Hardcoded Secrets (14 findings):** Test files contain plaintext passwords/API keys
   - **Severity:** HIGH (XXE), LOW (hardcoded secrets)
   - **Attack Surface:** Production XML parsing, test credential leakage

   ### Why This Matters
   - **XXE Risk:** Attackers can read arbitrary files, SSRF, DoS attacks
   - **Credential Leakage:** Hardcoded secrets appear in git history, accessible to anyone with repo access
   - **Compliance:** Many security policies prohibit hardcoded credentials
   - **Best Practices:** Defense-in-depth security posture

   ### Decision Made
   **[For Task F1, document which option was chosen]**
   - [x] Option A: Add defusedxml dependency (supports Python 3.10+)
   - [ ] Option B: Drop Python 3.10 support

   **Rationale:** [Explain why this option was selected]
   ```

3. **Security Considerations** (This is the most critical section):
   ```markdown
   ### Vulnerabilities Addressed

   #### XXE (XML External Entity) Injection - 15 Findings

   **Attack Vector:**
   ```xml
   <?xml version="1.0"?>
   <!DOCTYPE foo [
     <!ENTITY xxe SYSTEM "file:///etc/passwd">
   ]>
   <userdata>&xxe;</userdata>
   ```

   If parsed with Python's default `xml` module, this reads `/etc/passwd` and includes content in parsed output.

   **Affected Files:**
   - `src/lattice_lock_sheriff/formatters.py` (line 15) - JUnit XML output
   - `tests/test_xml_parser.py` (3 locations) - Test XML fixtures
   - `tests/test_sheriff_format.py` (2 locations) - Sheriff output tests
   - [List all 15 locations]

   **Fix Applied:**
   - **Option A:** Migrated to defusedxml library
     - `defusedxml` disables DTD processing by default
     - Prevents external entity expansion
     - Prevents billion laughs attack
     - Drop-in replacement for stdlib xml modules

   **OR**

   - **Option B:** Dropped Python 3.10 support
     - Python 3.11+ has secure XML defaults
     - No external dependency required
     - See migration guide in CHANGELOG.md

   **Verification:**
   ```bash
   # Test XXE prevention
   python << 'EOF'
   from defusedxml.ElementTree import fromstring

   # Attempt XXE attack
   malicious_xml = """<?xml version="1.0"?>
   <!DOCTYPE foo [
     <!ENTITY xxe SYSTEM "file:///etc/passwd">
   ]>
   <data>&xxe;</data>
   """

   try:
       tree = fromstring(malicious_xml)
       assert False, "Should have blocked XXE"
   except Exception as e:
       print(f"✓ XXE blocked: {e}")
   EOF
   ```

   ---

   #### Hardcoded Credentials - 14 Findings

   **Exposure Risk:**
   - Credentials in git history (can't be fully removed)
   - Visible to anyone with repo access
   - Could be accidentally reused in production
   - Security scanners flag these in compliance audits

   **Affected Files:**
   - `tests/test_admin_auth.py` (6 locations) - "password123", "admin_secret"
   - `tests/test_error_middleware.py` (4 locations) - "test_api_key_12345"
   - `tests/test_integration.py` (4 locations) - Various tokens

   **Fix Applied:**
   - Created pytest fixtures in `conftest.py`
   - Fixtures read from environment variables with safe defaults
   - Default values clearly marked as non-production:
     - `test-fixture-not-real-password-12345`
     - `test-fixture-not-real-key-67890`
   - Updated CI to optionally use secrets (but works without)

   **Security Properties:**
   - No production credentials in source code
   - Clear distinction between test and production secrets
   - Secrets can be rotated via environment variables
   - No hardcoded strings matching common password patterns

   **Verification:**
   ```bash
   # Verify no hardcoded secrets remain
   $ grep -rn "password.*=.*['\"]" tests/ | grep -v fixture | grep -v conftest
   # (empty output - no matches)

   # Verify tests work with defaults
   $ unset TEST_PASSWORD TEST_API_KEY TEST_SECRET_TOKEN
   $ pytest tests/test_admin_auth.py -v
   # ===== 12 passed in 1.23s =====

   # Verify tests work with custom values
   $ export TEST_PASSWORD="custom_test_pass"
   $ pytest tests/test_admin_auth.py -v
   # ===== 12 passed in 1.25s =====
   ```

   ### Security Scan Results

   **Before (Snyk):**
   ```
   ✗ High severity vulnerabilities:
     - XML External Entity (XXE) Injection [15 occurrences]
       Impact: Arbitrary file read, SSRF, DoS
       CVSS: 7.5 (HIGH)

   ✗ Low severity vulnerabilities:
     - Hardcoded passwords [14 occurrences]
       Impact: Credential exposure
       CVSS: 3.1 (LOW)

   Total: 29 vulnerabilities
   ```

   **After (Snyk):**
   ```
   ✓ All high severity vulnerabilities resolved
   ✓ All low severity vulnerabilities resolved

   Total: 0 vulnerabilities
   ```

   ### Attack Surface Reduction
   - XML parsing: Attack surface eliminated (defusedxml/Python 3.11+)
   - Test credentials: No longer exploitable (parameterized fixtures)
   - Compliance: Meets OWASP Top 10 requirements for XXE and credential management
   ```

4. **Detailed Changes**:

   ```markdown
   #### Task F1: XXE Mitigation

   **[If Option A chosen]**

   ##### pyproject.toml
   **File:** `pyproject.toml`
   **Lines:** dependencies section
   **Change:** Added defusedxml>=0.7.1

   **Before:**
   ```toml
   dependencies = [
       "click>=8.0",
       "pyyaml>=6.0",
       # …
   ]
   ```

   **After:**
   ```toml
   dependencies = [
       "click>=8.0",
       "defusedxml>=0.7.1",  # Security: Prevents XXE attacks
       "pyyaml>=6.0",
       # …
   ]
   ```

   ##### formatters.py
   **File:** `src/lattice_lock_sheriff/formatters.py`
   **Lines:** 15, 87, 132
   **Snyk Finding:** SNYK-PYTHON-XML-001

   **Before:**
   ```python
   from xml.dom import minidom
   from xml.etree.ElementTree import Element, SubElement, tostring

   class JUnitFormatter:
       def format(self, results):
           root = Element('testsuite')
           # … XML generation …
           return minidom.parseString(tostring(root)).toprettyxml()
   ```

   **After:**
   ```python
   from defusedxml import minidom
   from defusedxml.ElementTree import Element, SubElement, tostring

   class JUnitFormatter:
       def format(self, results):
           root = Element('testsuite')
           # … XML generation …
           return minidom.parseString(tostring(root)).toprettyxml()
   ```

   **Impact:** JUnit XML output generation now uses secure parser

   ##### Test Files (13 locations)
   [Document each test file with before/after for XML imports]

   **[If Option B chosen]**

   ##### pyproject.toml
   **Change:** Updated Python version requirement

   **Before:**
   ```toml
   requires-python = ">=3.10"
   ```

   **After:**
   ```toml
   requires-python = ">=3.11"
   ```

   ##### .github/workflows/*.yml
   **Change:** Removed Python 3.10 from test matrix
   [Show matrix before/after]

   ##### CHANGELOG.md
   **Added migration notice:**
   ```markdown
   ## Breaking Changes in v2.2.0

   ### Python 3.10 Support Dropped
   - **Reason:** Security hardening (XXE vulnerability mitigation)
   - **Migration:** Upgrade to Python 3.11 or later
   - **Timeline:** Python 3.10 reaches EOL in October 2026
   ```

   ---

   #### Task F2: Hardcoded Secrets Remediation

   ##### conftest.py (Created)
   **File:** `tests/conftest.py`
   **Lines:** 1-24 (new file)

   **Content:**
   [Include complete fixture implementation from instructions]

   **Design Decisions:**
   - **Default values:** Clearly non-production (test-fixture-not-real-*)
   - **Environment variables:** Optional override mechanism
   - **Naming:** Prefix "test_" to avoid confusion with production
   - **Documentation:** Docstrings explain usage

   ##### test_admin_auth.py
   **File:** `tests/test_admin_auth.py`
   **Lines:** 23, 45, 67, 89, 112, 134 (6 locations)

   **Example Change (Line 23):**

   **Before:**
   ```python
   def test_admin_login():
       response = client.post("/api/login", json={
           "username": "admin",
           "password": "password123"  # Hardcoded
       })
       assert response.status_code == 200
   ```

   **After:**
   ```python
   def test_admin_login(test_password):
       response = client.post("/api/login", json={
           "username": "admin",
           "password": test_password  # From fixture
       })
       assert response.status_code == 200
   ```

   **Rationale:**
   - Password now sourced from fixture
   - Can be overridden via TEST_PASSWORD env var
   - Default is clearly non-production
   - Test behavior unchanged (mocks still work)

   [Repeat for all 14 locations across all test files]

   ##### CI Workflows
   **File:** `.github/workflows/python-app.yml`
   **Lines:** Test step

   **Before:**
   ```yaml
   - name: Test with pytest
     run: |
       pytest tests/ -v --tb=short
   ```

   **After:**
   ```yaml
   - name: Test with pytest
     env:
       TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
       TEST_API_KEY: ${{ secrets.TEST_API_KEY }}
       TEST_SECRET_TOKEN: ${{ secrets.TEST_SECRET_TOKEN }}
     run: |
       pytest tests/ -v --tb=short
   ```

   **Note:** GitHub secrets are optional. Tests work with fixture defaults if secrets not configured.
   ```

5. **Testing**:
   ```markdown
   ### Test Strategy
   - **XXE Testing:** Attempt malicious XML payloads, verify blocking
   - **Secret Testing:** Verify no hardcoded credentials remain
   - **Regression Testing:** All existing tests pass with new fixtures
   - **Security Scanning:** Snyk, Bandit, Safety scans pass

   ### Tests Added
   - [x] `tests/test_xml_security.py` - New: XXE attack prevention tests
   - [x] `tests/test_fixture_security.py` - New: Validates fixture behavior
   - [x] `tests/test_credential_scan.py` - New: Scans for hardcoded secrets

   ### Verification Steps

   #### XXE Prevention Testing
   ```bash
   # Test 1: Basic XXE attack
   python tests/test_xml_security.py::test_xxe_file_read
   # Expected: defusedxml raises DTDForbidden

   # Test 2: Billion laughs attack
   python tests/test_xml_security.py::test_billion_laughs
   # Expected: defusedxml raises DTDForbidden

   # Test 3: SSRF attempt
   python tests/test_xml_security.py::test_xxe_ssrf
   # Expected: External network request blocked
   ```

   #### Credential Scan
   ```bash
   # Automated scan for secrets
   pytest tests/test_credential_scan.py -v
   # Scans all Python files for patterns like:
   # - password = "…"
   # - api_key = "…"
   # - secret = "…"
   # Excludes: conftest.py fixtures, test-fixture-* patterns

   # Manual verification
   grep -rn 'password.*=.*["'\'']' tests/ | grep -v fixture | grep -v conftest
   # Expected: Empty output
   ```

   #### Fixture Behavior Testing
   ```bash
   # Test default fixture values
   $ unset TEST_PASSWORD TEST_API_KEY
   $ python -c "
   import sys
   sys.path.insert(0, 'tests')
   from conftest import test_password
   passwd = test_password()
   assert 'test-fixture-not-real' in passwd.__name__
   print('✓ Default fixture works')
   "

   # Test environment override
   $ export TEST_PASSWORD="override123"
   $ pytest tests/test_admin_auth.py::test_admin_login -v -s
   # Should use "override123" instead of default
   ```

   ### Test Results

   **Security Scan Comparison:**
   ```bash
   # Before
   $ snyk test
   Testing /path/to/lattice-lock-framework…

   ✗ High severity vulnerabilities: 15
     - XML External Entity (XXE) [CWE-611]
       Introduced through: xml@stdlib
       Fixed in: defusedxml>=0.7.1 OR Python>=3.11

   ✗ Low severity vulnerabilities: 14
     - Hardcoded credentials [CWE-798]
       Found in: tests/test_admin_auth.py +5 others

   Organization test limit: 200/200 tests used

   # After
   $ snyk test
   Testing /path/to/lattice-lock-framework…

   ✓ Tested 47 dependencies for known issues, no vulnerable paths found.
   ```

   **Regression Test Results:**
   ```bash
   # All existing tests pass
   $ pytest tests/ -v
   ==================== test session starts ====================
   collected 947 items

   tests/test_admin_auth.py::test_admin_login PASSED    [  1%]
   tests/test_admin_auth.py::test_invalid_password PASSED [  2%]
   # … 943 more tests …
   tests/test_xml_parser.py::test_parse_junit PASSED    [100%]

   ==================== 947 passed in 45.23s ===================
   ```
   ```

6. **Dependencies**:
   ```markdown
   ### Dependency Changes
   **[If Option A]**
   - **Added:** defusedxml>=0.7.1
     - Size: ~50KB
     - Transitive dependencies: None
     - License: Python Software Foundation License (compatible)
     - Maintenance: Actively maintained, last update 2023-09
     - Security: Specifically designed for security hardening

   **[If Option B]**
   - **Removed Support:** Python 3.10
     - Reason: Python 3.11+ has secure XML by default
     - EOL: Python 3.10 reaches end-of-life October 2026
     - Migration: Users on 3.10 must upgrade to 3.11+

   ### Dependency Justification
   **[If Option A]**
   **Why defusedxml?**
   - Industry-standard solution for XXE prevention
   - Recommended by OWASP, Snyk, Bandit
   - Drop-in replacement (minimal code changes)
   - Zero breaking changes for API users
   - Negligible performance impact (<1% slower XML parsing)
   - Actively maintained with security focus

   **Alternatives Considered:**
   - lxml with DTD disabled: Larger dependency (C extensions), overkill for our use case
   - Custom XML parser: High maintenance burden, security risk
   - Python 3.11+ only: Breaking change for users
   ```

7. **Breaking Changes**:
   ```markdown
   ### Breaking Changes

   **[If Option A]**
   - [ ] No breaking changes
     - defusedxml is drop-in replacement
     - All existing APIs work identically
     - Tests pass without modification

   **[If Option B]**
   - [x] Python 3.10 support dropped
     - **Impact:** Users on Python 3.10 cannot upgrade to v2.2.0+
     - **Mitigation:** Stay on v2.1.x until Python upgrade possible
     - **Timeline:** v2.1.x will receive security patches for 6 months

   ### Migration Path
   **[If Option B]**

   #### For Users on Python 3.10
   ```bash
   # Check current Python version
   python --version

   # If Python 3.10, pin to last compatible version
   pip install "lattice-lock-framework<2.2.0"

   # Or upgrade Python
   # Ubuntu/Debian:
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt install python3.11

   # macOS:
   brew install python@3.11

   # Windows:
   # Download from python.org
   ```

   #### For CI Pipelines
   Update your CI configuration:
   ```yaml
   # Before
   strategy:
     matrix:
       python-version: ["3.10", "3.11", "3.12"]

   # After
   strategy:
     matrix:
       python-version: ["3.11", "3.12", "3.13"]
   ```
   ```

8. **Deployment Notes**:
   ```markdown
   ### Pre-Deployment Checklist
   - [ ] Security scan passes (snyk test)
   - [ ] All tests pass (pytest tests/)
   - [ ] [If Option A] defusedxml installed in production
   - [ ] [If Option B] Production Python version >= 3.11
   - [ ] Monitoring configured for XML parsing errors
   - [ ] Rollback plan documented

   ### Deployment Steps
   1. **[If Option A]**
      ```bash
      # Update dependencies
      pip install -e ".[dev]"

      # Verify defusedxml works
      python -c "from defusedxml import ElementTree; print('OK')"
      ```

   2. **[If Option B]**
      ```bash
      # Verify Python version
      python --version  # Must be >= 3.11

      # Reinstall package
      pip install --upgrade lattice-lock-framework
      ```

   3. Run smoke tests:
      ```bash
      lattice-lock validate --schema-only tests/fixtures/lattice.yaml
      lattice-lock sheriff --format junit tests/
      ```

   ### Rollback Plan
   **[If Option A]**
   ```bash
   # Remove defusedxml, revert to stdlib
   pip install "lattice-lock-framework<2.2.0"
   ```

   **[If Option B]**
   ```bash
   # Downgrade to last compatible version
   pip install "lattice-lock-framework<2.2.0"
   # Or downgrade Python (not recommended)
   ```

   ### Monitoring
   **Metrics to Watch:**
   - XML parsing errors (should remain at baseline)
   - Test execution time (negligible change expected)
   - Security scan results (should show 0 XXE findings)

   **Alerts to Configure:**
   - Alert on any DTDForbidden exceptions (indicates XXE attempt)
   - Alert on any tests using hardcoded credentials (in case new ones added)
   ```

9. **Post-Merge Tasks**:
   ```markdown
   - [ ] Update security documentation with XXE prevention guidelines
   - [ ] Update developer onboarding to mention test fixture usage
   - [ ] [If Option B] Announce Python 3.10 deprecation in community channels
   - [ ] Schedule security audit for Q1 2025
   - [ ] Add pre-commit hook to detect hardcoded secrets
   - [ ] Document security practices in CONTRIBUTING.md
   ```

---

## Execution Order Summary (For LLM Planning)

**Phase 1: Green CI (Must Complete First)**
1. Task A1 (Fix test paths) → Generate PR_GROUP_A
2. Task A2 (Fix failing tests)

**Phase 2: CLI Consolidation**
3. Task B1 (Add gauntlet alias) → Generate PR_GROUP_B
4. Task B2 (Consolidate orchestrator CLI)

**Phase 3: Security Utilities**
5. Task C1 (Jinja2 centralization) → Generate PR_GROUP_C
6. Task C2 (Path validation)

**Phase 4: Documentation**
7. Task D1 (Fix import paths) → Generate PR_GROUP_D
8. Task D2 (Generate missing docs)

**Phase 5: Code Quality**
9. Task E1 (Fix silent errors) → Generate PR_GROUP_E
10. Task E2 (Fix placeholder returns)

**Phase 6: Security (Decision-Gated)**
11. Task F1 (XML security - requires human decision) → Generate PR_GROUP_F
12. Task F2 (Test fixtures)

---

## LLM-Specific Notes

**After each task:**
1. Show exact diffs of what you changed
2. Run the verification command
3. Report success/failure status
4. If blocked, clearly state blocking dependency

**After completing each GROUP (all tasks in A, B, C, D, E, or F):**
1. Generate the Pull Request markdown document
2. Save it to the specified filename
3. Show a summary of what was documented
4. Confirm the PR document is complete and ready for human review

**Error handling:**
- If you can't find a file, ask for confirmation of path
- If you can't parse syntax, show the surrounding context
- If a verification command fails, show the full output
- If documentation generation is unclear, ask for clarification on missing details

**Before starting work:**
Respond with:
```
Ready to begin refactoring with PR documentation.

I will complete tasks in this order:
- Group A (Tasks A1, A2) → PR_GROUP_A_CI_Test_Infrastructure.md
- Group B (Tasks B1, B2) → PR_GROUP_B_CLI_Consolidation.md
- Group C (Tasks C1, C2) → PR_GROUP_C_Security_Utilities.md
- Group D (Tasks D1, D2) → PR_GROUP_D_Documentation_Fixes.md
- Group E (Tasks E1, E2) → PR_GROUP_E_Code_Hygiene.md
- Group F (Tasks F1, F2, pending human decision) → PR_GROUP_F_Security_Hardening.md

After completing each group, I will generate a comprehensive PR document following the template.

Should I proceed with Task A1?
```
