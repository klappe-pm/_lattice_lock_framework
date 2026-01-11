# Agent Sync Automation System - Overview

## What This System Does

Automatically converts your YAML agent definitions into multiple markdown formats and syncs them to different destinations:

1. **Claude Code Format** → `.claude/agents/` (for Claude Code to use)
2. **Lattice Lock Archive** → `agents/markdown/` (documentation)
3. **Extensible** → Easy to add new targets in the future

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run one-time sync
python3 sync_agents_to_claude.py

# OR start auto-watcher
python3 watch_and_sync.py
```

## File Structure

```
agents/
├── agent_definitions/              # Source YAML files (EDIT THESE)
│   ├── agents_engineering/
│   │   ├── engineering_agent_definition.yaml
│   │   └── subagents/
│   │       └── *.yaml
│   └── .../
│
├── markdown/                       # Generated Lattice Lock docs
│   ├── engineering_agent.md
│   └── .../
│
├── sync_agents_to_claude.py       # Main sync script
├── watch_and_sync.py               # Auto-watch script
│
├── requirements.txt
├── Makefile
│
├── QUICKSTART.md                   # Start here!
├── SYNC_README.md                  # Full documentation
├── EXTENDING.md                    # How to add new targets
└── SYSTEM_OVERVIEW.md              # This file
```

## Scripts

### `sync_agents_to_claude.py`
**Purpose**: One-time conversion and sync

**Usage**:
```bash
python3 sync_agents_to_claude.py
```

**Options**:
1. Claude Code (project) + Lattice Lock [RECOMMENDED]
2. Claude Code (user) + Lattice Lock
3. All targets
4. Lattice Lock only

**When to use**: Manual syncs, CI/CD, first-time setup

### `watch_and_sync.py`
**Purpose**: Automatic syncing on file changes

**Usage**:
```bash
python3 watch_and_sync.py
```

**Features**:
- Initial sync on startup
- Watches for YAML file changes
- Debouncing (batches rapid changes)
- Runs until Ctrl+C

**When to use**: Active development, continuous syncing

### Makefile Commands

```bash
make help       # Show all commands
make install    # Install dependencies
make sync       # Run one-time sync
make watch      # Start auto-watcher
make clean      # Remove generated files
```

## Formats

### Claude Code Format
**Location**: `.claude/agents/*.md`

**Purpose**: Claude Code subagent definitions

**Format**:
```markdown
---
name: agent_name
description: Agent description
tools: [Read, Write, Edit, Bash, Glob, Grep]
model: sonnet
---

You are a [Role].

## Primary Goal
...

## Scope
...
```

**Used by**: Claude Code (automatically loaded)

### Lattice Lock Format
**Location**: `agents/markdown/*.md`

**Purpose**: Human-readable documentation and archival

**Format**:
```markdown
# Agent Name

## Metadata
- **Name**: `agent_name`
- **Role**: Engineer
- **Version**: 1.0.0
...

## Description
...

## Directive
...

## Scope
...
```

**Used by**: Documentation, reference, versioning

## Architecture

### Components

```
┌─────────────────────────────────────────┐
│         User Interface (CLI)            │
│  - Prompts for target selection         │
│  - Displays progress and results        │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│      create_sync_targets()              │
│  - Builds list of SyncTarget objects    │
│  - Maps user choice to targets          │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         AgentSyncer                     │
│  - Reads YAML files                     │
│  - Loops through targets                │
│  - Writes converted files               │
└───────────────┬─────────────────────────┘
                │
                ▼
        ┌───────┴───────┐
        │               │
        ▼               ▼
┌───────────────┐ ┌──────────────────┐
│  SyncTarget   │ │ AgentConverter   │
│  - name       │ │ - to_claude_*    │
│  - path       │ │ - to_lattice_*   │
│  - converter  │ │ - to_custom_*    │
└───────────────┘ └──────────────────┘
```

### Data Flow

```
YAML Files → load_yaml_agent() → agent_data (dict)
                                       │
                                       ▼
                            AgentConverter.to_*()
                                       │
                                       ▼
                            markdown string
                                       │
                                       ▼
                            Write to target directory
```

## Key Design Decisions

### 1. Extensibility
The system uses the **Strategy Pattern** with:
- `SyncTarget` dataclass to define destinations
- Converter functions as strategies
- Easy addition of new targets without modifying core logic

### 2. Separation of Concerns
- **AgentConverter**: Pure functions for conversion
- **AgentSyncer**: I/O and orchestration
- **SyncTarget**: Configuration
- **Main/CLI**: User interaction

### 3. Backward Compatibility
- Legacy `sync_agents_to_claude()` function preserved
- Existing scripts continue to work
- Watch script updated to use new architecture

### 4. Error Handling
- Continues on individual file errors
- Reports errors without stopping entire process
- Returns counts for verification

## Adding New Sync Targets

See [EXTENDING.md](EXTENDING.md) for detailed guide.

**Quick summary**:
1. Add converter method to `AgentConverter`
2. Define `SyncTarget` in `create_sync_targets()`
3. Add to `target_combinations`
4. Update UI menu
5. Test

**Example** (in code):
```python
# 1. Converter
@staticmethod
def to_my_format(agent_data, is_subagent=False):
    # Your conversion logic
    return markdown_string

# 2. Target
'my-target': SyncTarget(
    name='my-target',
    base_path=path,
    subfolder='sub',
    converter=AgentConverter.to_my_format,
    description='My target description'
)

# 3. Combination
'5': ['my-target'],
```

## Best Practices

### Development Workflow
1. Edit YAML files in `agent_definitions/`
2. Run watcher: `python3 watch_and_sync.py`
3. Changes auto-sync to all targets
4. Use generated files (don't edit them)

### Version Control
- **Commit**: YAML files in `agent_definitions/`
- **Optional**: `agents/markdown/` for versioned docs
- **Ignore**: `.claude/agents/` (can be regenerated)

### Production/CI
```bash
# In CI pipeline
pip install -r agents/requirements.txt
python3 agents/sync_agents_to_claude.py << EOF
1
y
EOF
```

## Troubleshooting

### Import Errors
```bash
pip3 install -r requirements.txt
```

### Agents Not Showing in Claude Code
- Check `.claude/agents/` exists and has `.md` files
- Restart Claude Code
- Verify you synced to project-level (option 1)

### Changes Not Syncing
- If using watcher: Check it's still running
- If manual: Run sync script again
- Check YAML syntax is valid

### File Permission Errors
```bash
chmod +x sync_agents_to_claude.py watch_and_sync.py
```

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[SYNC_README.md](SYNC_README.md)** - Complete documentation
- **[EXTENDING.md](EXTENDING.md)** - Add new sync targets
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - This file

## Dependencies

- **pyyaml** (≥6.0): YAML parsing
- **watchdog** (≥3.0): File system monitoring

## Future Enhancements

Potential additions:
- Config file for target preferences
- Validation of YAML before conversion
- Diff reporting (what changed)
- Dry-run mode
- Selective sync (specific agents only)
- Template-based conversion
- Multi-language support

## License & Credits

This sync automation system is part of the Lattice Lock Framework.
Created to bridge YAML agent definitions with Claude Code integration.
