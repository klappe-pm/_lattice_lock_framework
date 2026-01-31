# Quick Start Guide

## 1. Install Dependencies

```bash
cd /Users/kevinlappe/Documents/lattice-lock-framework/agents
pip3 install -r requirements.txt
```

Or use the Makefile:

```bash
make install
```

## 2. Run Your First Sync

### Option A: Interactive One-Time Sync

```bash
python3 sync_agents_to_claude.py
```

When prompted:
- Choose option **1** (recommended): Syncs to both Claude Code and Lattice Lock archive
- This creates:
  - `.claude/agents/` for Claude Code
  - `agents/markdown/` for documentation archive

### Option B: Start Auto-Watch Mode

```bash
python3 watch_and_sync.py
```

Or:

```bash
make watch
```

This will:
1. Do an initial sync
2. Keep watching for changes
3. Auto-sync whenever you edit YAML files
4. Press Ctrl+C to stop

## 3. Verify the Sync

Check that agents were created:

```bash
# Check Claude Code agents
ls -la /Users/kevinlappe/Documents/lattice-lock-framework/.claude/agents/

# Check Lattice Lock archive
ls -la /Users/kevinlappe/Documents/lattice-lock-framework/agents/markdown/
```

You should see `.md` files for each of your agents in both locations.

## 4. Use in Claude Code

Open Claude Code and your agents will be automatically available!

Try asking:
- "Show me all available agents" (or use `/agents` command)
- "Have the backend_developer agent review this code"
- Let Claude automatically delegate based on task context

## Next Steps

- Read [SYNC_README.md](SYNC_README.md) for detailed documentation
- Customize the conversion in `sync_agents_to_claude.py`
- Add `.claude/agents/` to your `.gitignore` if desired

## Common Commands

```bash
make help       # Show all available commands
make install    # Install dependencies
make sync       # One-time sync
make watch      # Start auto-watcher
make clean      # Remove generated files
```
