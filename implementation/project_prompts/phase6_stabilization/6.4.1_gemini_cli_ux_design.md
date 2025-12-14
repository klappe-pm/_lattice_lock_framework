# Task 6.4.1: Engineering Framework CLI UX Design

**Status:** Approved
**Owner:** Gemini Antimatter
**Implementation Task:** 6.4.2 (Devin AI)

---

## 1. UX Philosophy

The `lattice-lock` CLI should be:
*   **Unified:** Single entry point (`lattice-lock <command>`), replacing loose scripts.
*   **Helpful:** Rich error messages, suggestions, and auto-completion.
*   **Predictable:** Standard flags (`--verbose`, `--json`, `--project-dir`) across all commands.

## 2. Command Structure

```bash
lattice-lock [GLOBAL OPTIONS] <COMMAND> [SUBCOMMAND] [ARGS]
```

### Global Options
*   `--verbose, -v`: Enable debug logging.
*   `--json`: Output results as JSON (for CI/machine parsing).
*   `--project-dir, -p`: Target directory (default: current).

### Core Commands

| Command | Subcommand | Description |
|---------|------------|-------------|
| `init` | | Scaffold a new project (interactive wizard). |
| `validate` | | Run Sheriff static analysis. |
| `compile` | | Compile `lattice.yaml` policies. |
| `test` | | Run Gauntlet semantic tests. |
| `orchestrator` | `list` | List available models. |
| | `analyze` | Analyze a prompt. |
| `deploy` | | Trigger a deployment (via CD hooks). |
| `cost` | | Show cost tracking reports. |
| `admin` | `dashboard` | Launch the local admin dashboard. |

## 3. Interactive Features

*   **Spinners:** Use `rich` library spinners for long-running tasks (e.g., "Analyzing AST...").
*   **Progress Bars:** Deterministic progress for test execution.
*   **Tables:** Pretty-print tables for `list` and `cost` commands.
*   **Colors:** Red for errors, Green for success, Yellow for warnings.

## 4. Implementation Specifications

### Libraries
*   **Click:** For argument parsing (robust, standard).
*   **Rich:** For terminal UI (tables, colors, spinners).

### Structure
```
src/lattice_lock_cli/
├── __main__.py          # Entry point
├── groups/
│   ├── orchestrator.py  # Orchestrator subcommand group
│   └── admin.py         # Admin subcommand group
├── commands/
│   ├── init.py
│   ├── validate.py
│   └── ...
└── utils/
    ├── console.py       # Rich console singleton
    └── formatting.py    # Output formatters
```

## 5. Migration Guide
Users currently running `python scripts/orchestrator_cli.py` should get a deprecation warning guiding them to `lattice-lock orchestrator`.
