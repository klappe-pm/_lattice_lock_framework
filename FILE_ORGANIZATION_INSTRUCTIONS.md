# File Organization Instructions
**Repository**: lattice-lock-framework  
**Purpose**: Guide for organizing root-level files into proper directories  
**For use with**: WARP.md, CLAUDE.md, GEMINI.md, and other AI assistant instruction files

---

## Current Root Directory Issues

### Analysis Summary
The root directory contains 41 items, many of which belong in subdirectories:
- **Documentation files** scattered in root (should be in `docs/`)
- **Test artifacts** in root (should be in `tests/` or be removed)
- **Example scripts** in root (should be in `docs/examples/` or `scripts/`)
- **Project management files** that could be better organized

---

## Directory Structure Overview

```
lattice-lock-framework/
├── docs/                    # All documentation
│   ├── agents/             # Agent-related docs
│   ├── architecture/       # System architecture docs
│   ├── database/           # Database docs
│   ├── design/             # Design documents
│   ├── examples/           # Code examples and demos
│   ├── features/           # Feature documentation
│   ├── guides/             # User guides
│   ├── reference/          # API reference docs
│   ├── testing/            # Testing documentation
│   └── tutorials/          # Tutorial content
│
├── project-management/      # Project planning and tracking
│   ├── refactoring/        # Refactoring plans
│   └── [planning docs]     # Audit reports, deprecations, etc.
│
├── scripts/                 # Utility and build scripts
│   ├── migrations/         # Database migrations
│   ├── setup/              # Setup scripts
│   ├── tests/              # Test runner scripts
│   └── utilities/          # Various utility scripts
│
├── tests/                   # Test suite
│   ├── [test modules]/     # Various test directories
│   ├── fixtures/           # Test fixtures
│   └── data/               # Test data
│
├── src/                     # Source code
├── frontend/                # Frontend code
├── infrastructure/          # Infrastructure as code
├── shared/                  # Shared resources
└── diagrams/                # Architecture diagrams
```

---

## File-by-File Instructions

### Files to MOVE

#### 1. Documentation Files → `docs/`

| Current Location | New Location | Reason |
|-----------------|--------------|--------|
| `Code Gap Inventory.md` | `docs/development/code-gap-inventory.md` | Development documentation |
| `MODELS.md` | `docs/reference/models.md` | Reference documentation |
| `VALIDATION_REPORT.md` | `docs/testing/validation-report.md` | Testing documentation |

**Action**: 
```bash
mkdir -p docs/development docs/reference
mv "Code Gap Inventory.md" docs/development/code-gap-inventory.md
mv MODELS.md docs/reference/models.md
mv VALIDATION_REPORT.md docs/testing/validation-report.md
```

#### 2. Example Scripts → `docs/examples/`

| Current Location | New Location | Reason |
|-----------------|--------------|--------|
| `multi_turn_example.py` | `docs/examples/basic/multi_turn_chat.py` | Basic usage example |
| `test_prompt.py` | `docs/examples/basic/simple_prompt.py` | Basic usage example |

**Action**:
```bash
mv multi_turn_example.py docs/examples/basic/multi_turn_chat.py
mv test_prompt.py docs/examples/basic/simple_prompt.py
```

#### 3. Test Artifacts → `tests/reports/` or DELETE

| Current Location | New Location | Reason |
|-----------------|--------------|--------|
| `e2e_report.xml` | `tests/reports/e2e_report.xml` OR DELETE | Test output artifact |
| `e2e_summary.md` | `tests/reports/e2e_summary.md` OR DELETE | Test output artifact |

**Recommended Action** (DELETE - these are generated artifacts):
```bash
rm e2e_report.xml e2e_summary.md
```

**Alternative Action** (KEEP - if historical value):
```bash
mkdir -p tests/reports
mv e2e_report.xml tests/reports/
mv e2e_summary.md tests/reports/
# Add tests/reports/ to .gitignore
echo "tests/reports/" >> .gitignore
```

#### 4. Project Management → Already in correct location
`pr_comments.json` appears to be a work artifact - recommend deletion:
```bash
rm pr_comments.json
```

### Files to KEEP in Root

These files are correctly placed in the root directory:

| File | Reason |
|------|--------|
| `.coverage` | Generated coverage data (in .gitignore) |
| `.DS_Store` | macOS metadata (should be in .gitignore) |
| `.gitignore` | Version control configuration |
| `.pre-commit-config.yaml` | Development tooling |
| `CONTRIBUTING.md` | Repository documentation |
| `LICENSE.md` | Legal requirement |
| `Makefile` | Build automation |
| `docker-compose.yml` | Container orchestration |
| `Dockerfile` | Container definition |
| `pyproject.toml` | Python project configuration |
| `requirements*.lock` | Dependency specifications |
| `requirements.in` | Dependency specifications |
| `version.txt` | Version tracking |

### Hidden Directories to KEEP

| Directory | Purpose |
|-----------|---------|
| `.git/` | Version control |
| `.githooks/` | Git hooks |
| `.github/` | GitHub actions/workflows |
| `.lattice-lock/` | Application data |
| `.mcp/` | MCP server data |
| `.obsidian/` | Obsidian vault metadata |
| `.pytest_cache/` | Test cache (generated) |
| `.ruff_cache/` | Linter cache (generated) |

---

## Execution Plan

### Phase 1: Create Missing Directories (if needed)
```bash
mkdir -p docs/development
mkdir -p docs/reference
# mkdir -p docs/testing  # Already exists
# mkdir -p docs/examples/basic  # Already exists
# mkdir -p tests/reports  # Only if keeping test artifacts
```

### Phase 2: Move Documentation Files
```bash
mv "Code Gap Inventory.md" docs/development/code-gap-inventory.md
mv MODELS.md docs/reference/models.md
mv VALIDATION_REPORT.md docs/testing/validation-report.md
```

### Phase 3: Move Example Scripts
```bash
mv multi_turn_example.py docs/examples/basic/multi_turn_chat.py
mv test_prompt.py docs/examples/basic/simple_prompt.py
```

### Phase 4: Handle Test Artifacts
**Option A - Delete** (recommended):
```bash
rm e2e_report.xml e2e_summary.md
```

**Option B - Archive** (if historical value):
```bash
mkdir -p tests/reports
mv e2e_report.xml tests/reports/
mv e2e_summary.md tests/reports/
echo "" >> .gitignore
echo "# Test reports" >> .gitignore
echo "tests/reports/" >> .gitignore
```

### Phase 5: Remove Work Artifacts
```bash
rm pr_comments.json
```

### Phase 6: Update Documentation References
After moving files, update any references in:
- Documentation files that link to moved content
- `docs/USER_FACING_FILE_MAP.md` (if it exists)
- Any README files that reference the moved files
- CI/CD scripts that may reference file paths

### Phase 7: Verify and Commit
```bash
# Verify structure
ls -la
git status

# Test that imports still work (for Python files)
python -c "import sys; sys.path.append('src'); from lattice_lock import ModelOrchestrator; print('✓ Imports OK')"

# Commit changes
git add -A
git commit -m "chore: reorganize root directory files into proper subdirectories

- Move documentation to docs/ subdirectories
- Move example scripts to docs/examples/basic/
- Remove generated test artifacts
- Remove work artifacts (pr_comments.json)

Improves repository organization and maintainability."
```

---

## Files Summary

### TO MOVE (6 files):
1. `Code Gap Inventory.md` → `docs/development/code-gap-inventory.md`
2. `MODELS.md` → `docs/reference/models.md`
3. `VALIDATION_REPORT.md` → `docs/testing/validation-report.md`
4. `multi_turn_example.py` → `docs/examples/basic/multi_turn_chat.py`
5. `test_prompt.py` → `docs/examples/basic/simple_prompt.py`

### TO DELETE (3 files):
1. `e2e_report.xml` (generated artifact)
2. `e2e_summary.md` (generated artifact)
3. `pr_comments.json` (work artifact)

### TO KEEP (15+ files):
- All configuration files (`.gitignore`, `pyproject.toml`, etc.)
- All build files (`Makefile`, `Dockerfile`, etc.)
- All dependency files (`requirements*.lock`, etc.)
- All repository docs (`CONTRIBUTING.md`, `LICENSE.md`)
- All hidden directories (`.git/`, `.github/`, etc.)

---

## Post-Organization Root Directory

After cleanup, the root should contain:
```
lattice-lock-framework/
├── .coverage                      [generated, ignored]
├── .DS_Store                      [OS metadata, should be ignored]
├── .git/                          [version control]
├── .githooks/                     [git hooks]
├── .github/                       [GitHub config]
├── .gitignore                     [VCS config]
├── .lattice-lock/                 [app data]
├── .mcp/                          [MCP data]
├── .obsidian/                     [Obsidian config]
├── .pre-commit-config.yaml        [dev tooling]
├── .pytest_cache/                 [test cache]
├── .ruff_cache/                   [linter cache]
├── CONTRIBUTING.md                [repo docs]
├── diagrams/                      [architecture diagrams]
├── docker-compose.yml             [container config]
├── Dockerfile                     [container definition]
├── docs/                          [all documentation]
├── frontend/                      [frontend code]
├── infrastructure/                [IaC]
├── LICENSE.md                     [legal]
├── Makefile                       [build automation]
├── project-management/            [project planning]
├── pyproject.toml                 [Python config]
├── requirements-dev.lock          [dev dependencies]
├── requirements.in                [dependencies]
├── requirements.lock              [locked dependencies]
├── scripts/                       [utility scripts]
├── shared/                        [shared resources]
├── src/                           [source code]
├── tests/                         [test suite]
└── version.txt                    [version info]
```

---

## Notes for AI Assistants

1. **Before executing**: Review this plan with the user and get confirmation
2. **Git status**: Always check `git status` before and after operations
3. **Breaking changes**: Moving Python files may require import path updates - test after moving
4. **Documentation links**: Search for internal references to moved files and update them
5. **Backup**: User should ensure work is committed or can create a backup branch before major reorganization
6. **Incremental**: Can be done in phases if user prefers (docs first, then examples, then cleanup)

---

## Validation Checklist

After executing the reorganization:
- [ ] Root directory only contains expected files
- [ ] All moved files are in their new locations
- [ ] Python imports still work (test with `python -c "from lattice_lock import ModelOrchestrator"`)
- [ ] Documentation links are updated
- [ ] `.gitignore` is updated if test reports directory was created
- [ ] Git status shows only intended changes
- [ ] Tests still pass (`pytest` or `make test`)
- [ ] No broken references in documentation
