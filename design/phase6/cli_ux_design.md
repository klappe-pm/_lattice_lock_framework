# Engineering Framework CLI UX Design (6.4.1)

**Status:** Draft
**Owner:** Gemini Antimatter
**Implementation Owner:** Devin AI

## 1. Overview
The Lattice Lock Framework CLI (`lattice-lock`) needs a unified, professional, and consistent user experience. Currently, commands are functional but lack a cohesive visual identity and standardized interaction patterns. This design establishes the UX standards for Phase 6 and beyond.

## 2. Core Principles
1.  **Rich Visuals:** Use the `rich` library for all user-facing output (tables, panels, spinners, syntax highlighting).
2.  **Predictability:** Standardized flags (`--help`, `--examples`, `--json`, `--verbose`) across all commands.
3.  **Actionability:** Error scenarios must suggest fixes (Doctor pattern).
4.  **Speed:** Instant feedback for long-running operations via progress indicators.

## 3. Command Structure

### 3.1 Global Entry Point
Binary: `lattice-lock`
Alias: `ll` (recommended implication)

```bash
lattice-lock [GROUP] [COMMAND] [ARGS...]
```

### 3.2 Command Groups
| Group | Description | Commands |
|-------|-------------|----------|
| `core` (root) | Essential lifecycle commands | `init`, `compile`, `validate` |
| `dev` | Development assistance | `doctor`, `update` |
| `ops` | Operational tasks | `deploy`, `rollback`, `status` |
| `ci` | CI/CD utilities | `sheriff`, `gauntlet`, `audit` |

### 3.3 Standard Flags
- `--verbose, -v`: Enable debug logging (rich tracebacks).
- `--json`: Output raw JSON to stdout (disable rich formatting).
- `--quiet, -q`: Suppress all non-error output.
- `--help, -h`: Show context-aware help.

## 4. Visual Design Specifications

### 4.1 Color Palette (HSL-aligned)
- **Primary:** `#00d4ff` (Cyan - Info/Headers)
- **Success:** `#00ff9d` (Spring Green - Pass/Safe)
- **Warning:** `#ffaa00` (Amber - Deprecations/Risks)
- **Error:** `#ff4444` (Red - Failures/Blockers)
- **Muted:** `#666666` (Grey - Secondary text)

### 4.2 Output Formats

#### Tables
ALL list data must use `rich.table.Table`.
- **Borders:** minimal (box.SIMPLE)
- **Headers:** Bold, primary color.
- **Alternating rows:** generic styling not required, but row styles for status (green for active, etc.) encouraged.

#### Progress
Long operations (>500ms) must use `rich.progress`.
- Spinner: `dots`
- Description: "Compiling lattice.yaml... [3/5]"

#### Errors
Use `rich.panel.Panel` for errors.
Title: "[bold red]Error: <ErrorType>[/]"
Body:
1. Description of what went wrong.
2. **Context:** File/Line if applicable.
3. **Suggestion:** Actionable next step.

Example:
```text
┌─ Error: ValidationError ───────────────────────────────────────────────┐
│                                                                        │
│  The capabilities contract 'bedrock-standard' is missing required      │
│  field 'throughput'.                                                   │
│                                                                        │
│  Location: lattice.yaml:14                                             │
│  Suggestion: Run `lattice-lock doctor` to fix schema issues.           │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## 5. Key Command Specs

### 5.1 `compile`
**Goal:** Transform governance specs into executable code.
**UX:**
1.  Start spinner: "Reading configuration..."
2.  Update spinner: "Validating schema (Sheriff)..."
3.  Update spinner: "Generating artifacts..."
4.  Stop spinner.
5.  Print Summary Panel:
    - Files generated: 4
    - Validation: PASSED
    - Duration: 1.2s

### 5.2 `init`
**Goal:** Scaffold new project.
**UX:** Interactive Questionnaire (using `rich.prompt`).
- "Project Name?" [default: current_dir]
- "Select Cloud Provider:" (Arrow keys selection)
- "Enable CI/CD?" (y/n)

## 6. Implementation Strategy (6.4.2)
- Refactor `src/lattice_lock_cli/utils/output.py` to encapsulate `rich` console.
- Create `BaseCommand` class in `src/lattice_lock_cli/commands/base.py`.
- Update `compile.py` to use new `Output` utilities.
