# Agent Definition Sync for Claude Code

This folder contains scripts to automatically sync your YAML agent definitions to Claude Code-compatible format.

## Overview

<cite index="1-2,1-32">Claude Code subagents are defined in Markdown files with YAML frontmatter</cite>, while your current agent definitions use YAML format. These scripts automatically convert your YAML definitions to multiple target formats:

- **Claude Code Format**: For use with Claude Code (project-level or user-level)
- **Lattice Lock Archive**: Documentation-focused markdown for archival and reference

The system is extensible - you can easily add new sync targets in the future.

## How Claude Code Subagents Work

<cite index="2-5">Place subagent files in .claude/agents/ within your project</cite>. Claude Code will:
- <cite index="2-5">Automatically detect and load the subagents</cite>
- <cite index="1-15">Delegate to subagents when it encounters a task that matches a subagent's description</cite>
- <cite index="2-4">Use project-specific subagents to override global ones when naming conflicts occur</cite>

## Setup

### 1. Install Dependencies

```bash
pip install pyyaml watchdog
```

### 2. Choose Your Sync Method

#### Option A: One-Time Sync

Run the sync script manually whenever you want to update:

```bash
python3 sync_agents_to_claude.py
```

This will prompt you to choose:
1. **Claude Code (project) + Lattice Lock** [RECOMMENDED]: Syncs to both `.claude/agents/` and `agents/markdown/`
2. **Claude Code (user) + Lattice Lock**: Syncs to `~/.claude/agents/` and `agents/markdown/`
3. **All targets**: Syncs to project, user, and archive locations
4. **Lattice Lock only**: Syncs only to `agents/markdown/` for documentation

#### Option B: Automatic Watching (Recommended)

Run the watcher to automatically sync whenever you modify agent definitions:

```bash
python3 watch_and_sync.py
```

This will:
1. Perform an initial sync
2. Watch for any changes to YAML files in `agent_definitions/`
3. Automatically re-sync when changes are detected
4. Keep running until you press Ctrl+C

## File Structure

Your existing structure is preserved:
```
agents/
├── agent_definitions/          # Your YAML definitions (source)
│   ├── agents_engineering/
│   │   ├── engineering_agent_definition.yaml
│   │   └── subagents/
│   │       ├── engineering_agent_backend_developer_definition.yaml
│   │       └── ...
│   └── ...
├── sync_agents_to_claude.py   # One-time sync script
├── watch_and_sync.py           # Auto-watch script
└── SYNC_README.md              # This file
```

After syncing, files appear in multiple locations:

**Claude Code Format**:
```
.claude/
└── agents/                     # Claude Code format (generated)
    ├── engineering_agent.md
    ├── backend_developer.md
    └── ...
```

**Lattice Lock Archive**:
```
agents/
└── markdown/                   # Documentation format (generated)
    ├── engineering_agent.md
    ├── backend_developer.md
    └── ...
```

## Agent Format Conversion

The scripts convert your YAML format:

```yaml
agent:
  identity:
    name: backend_developer
    role: Backend Engineer
    description: Responsible for server-side logic...
  directive:
    primary_goal: Implement performant and secure server-side components.
  scope:
    can_access:
      - /src/backend
```

To Claude Code Markdown format:

```markdown
---
name: backend_developer
description: Responsible for server-side logic...
tools: [Read, Write, Edit, Bash, Glob, Grep]
model: sonnet
---

You are a Backend Engineer.

## Primary Goal
Implement performant and secure server-side components.

## Scope
### Can Access
- /src/backend
...
```

## Using Your Agents in Claude Code

Once synced, your agents are automatically available. You can:

1. **Let Claude decide**: <cite index="1-15">When Claude encounters a task that matches a subagent's description, it delegates to that subagent</cite>

2. **Explicitly invoke**: <cite index="2-3,2-30">You can explicitly request its help</cite>:
   ```
   Have the backend_developer subagent review this API code
   ```

3. **Use the `/agents` command**: <cite index="7-2,7-27">Run the `/agents` command in Claude Code</cite> to see all available agents

## Important Notes

- **Your YAML files remain unchanged**: The sync only reads your YAML files and generates Markdown files
- **No reverse sync**: Changes made to generated `.md` files will be overwritten on next sync
- **Main source of truth**: Keep editing your YAML files in `agent_definitions/`
- **Version control**: Consider adding generated directories to `.gitignore`:
  - `.claude/agents/` (Claude Code agents)
  - `agents/markdown/` (Lattice Lock archive) - or commit this if you want versioned docs

## Customization

### Adding New Conversion Formats

To add a new output format, edit `sync_agents_to_claude.py`:

1. Add a new static method to the `AgentConverter` class:
   ```python
   @staticmethod
   def to_my_custom_format(agent_data: Dict[str, Any], is_subagent: bool = False) -> str:
       # Your conversion logic here
       return markdown_content
   ```

2. Add a new target in `create_sync_targets()` function:
   ```python
   'my-target': SyncTarget(
       name='my-target',
       base_path=some_path,
       subfolder='optional_subfolder',
       converter=AgentConverter.to_my_custom_format,
       description='Description of this target'
   )
   ```

3. Update the `target_combinations` dictionary to include your new target

### Modifying Existing Formats

- **Claude Code format**: Edit `AgentConverter.to_claude_code_format()`
- **Lattice Lock format**: Edit `AgentConverter.to_lattice_lock_format()`
- Adjust tools, model preferences, or prompt sections as needed

## Troubleshooting

**Q: My agents aren't showing up in Claude Code**
- Ensure you synced to the correct location (project-level vs user-level)
- Check that `.claude/agents/` directory exists and contains `.md` files
- Restart Claude Code if it was already running

**Q: Changes to my YAML aren't reflected**
- If using manual sync: Run `sync_agents_to_claude.py` again
- If using watcher: Check that the watcher is still running

**Q: I get import errors**
- Make sure you installed dependencies: `pip install pyyaml watchdog`
