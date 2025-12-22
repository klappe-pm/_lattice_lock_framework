# Agent Scripts for Multi-Agent Orchestration

This directory contains Python scripts for coordinating work across multiple AI tools (Devin AI, Claude Code, Gemini in Antimatter, and Gemini CLI).

## Quick Start

### For Devin AI Tasks

```bash
# Get the next available Devin task
python scripts/devin_agent.py next

# Show a specific task
python scripts/devin_agent.py show 2.2.1

# List all Devin tasks
python scripts/devin_agent.py list

# Check status summary
python scripts/devin_agent.py status
```

### For Claude Code (IDE Assistant)

```bash
# Get prompt for a specific task
python scripts/claude_code_agent.py 2.2.1

# List all available tasks
python scripts/claude_code_agent.py list
```

**Workflow:**
1. Run the script with a task ID
2. Copy the generated prompt
3. Open Claude Code in your IDE with the repo open
4. Paste the prompt and review the output
5. Apply the generated code

### For Gemini in Antimatter (Design Docs)

```bash
# Get prompt for a specific task
python scripts/gemini_antimatter_agent.py 2.2.1

# List all available tasks
python scripts/gemini_antimatter_agent.py list
```

**Workflow:**
1. Run the script with a task ID
2. Copy the generated prompt
3. Open Gemini in your Antimatter workspace
4. Paste the prompt and review the design document
5. Save the output to the appropriate location

### For Gemini CLI (Terminal Commands)

```bash
# Get prompt for a specific task
python scripts/gemini_cli_agent.py 2.2.1

# List all available tasks
python scripts/gemini_cli_agent.py list
```

**Workflow:**
1. Run the script with a task ID
2. Copy the generated prompt
3. Open Gemini CLI in your terminal
4. Paste the prompt and review the commands
5. **IMPORTANT:** Replace placeholders (ACCOUNT_ID, REGION, etc.) with actual values
6. Execute commands selectively - review before running

## Available Tasks

| Task ID | Description | Tools |
|---------|-------------|-------|
| 2.2.1 | AWS CodePipeline template | All |
| 2.3.1 | GCP Cloud Build template | All |
| 3.1.1 | Error classification system | All |
| 3.1.2 | Error handling middleware | All |
| 4.3.1 | Pilot Project 1 (API Service) | All |
| 4.3.2 | Pilot Project 2 (CLI Tool) | All |
| 5.1.1 | Prompt Architect Agent core | All |
| 5.1.2 | Prompt Architect integration | All |

## Recommended Execution Order

### Parallel Track A (Devin AI)
1. 2.2.1 AWS CodePipeline
2. 2.3.1 GCP Cloud Build
3. 3.1.1 Error Classification
4. 3.1.2 Error Middleware
5. 5.1.1 Prompt Architect Core
6. 5.1.2 Prompt Architect Integration
7. 4.3.1 Pilot Project 1
8. 4.3.2 Pilot Project 2

### Parallel Track B (Claude/Gemini)
For each task, run in this order:
1. **Gemini Antimatter** - Generate design document
2. **Claude Code** - Generate code draft based on design
3. **Gemini CLI** - Generate bootstrap/test commands
4. **Devin AI** - Integrate, test, and create PR

## File Structure

```
scripts/
├── agent_prompts.py           # Shared prompt library
├── devin_agent.py             # Devin AI task management
├── claude_code_agent.py       # Claude Code prompt generator
├── gemini_antimatter_agent.py # Gemini Antimatter prompt generator
├── gemini_cli_agent.py        # Gemini CLI prompt generator
├── prompt_tracker.py          # Existing prompt tracker
└── AGENT_SCRIPTS_README.md    # This file
```

## Integration with Prompt Tracker

The Devin agent script integrates with `prompt_tracker.py` to:
- Pick up the next available task
- Track task progress (picked up, done, merged)
- Record PR URLs and completion times

Update task status after completion:
```bash
# Mark task as done
python scripts/prompt_tracker.py update --id 2.2.1 --done

# Mark task as merged with PR URL
python scripts/prompt_tracker.py update --id 2.2.1 --merged --pr "https://github.com/..."
```

## Adding New Prompts

To add prompts for new tasks, edit `scripts/agent_prompts.py`:

1. Add the prompt to the appropriate dictionary:
   - `CLAUDE_CODE_PROMPTS` for Claude Code
   - `GEMINI_ANTIMATTER_PROMPTS` for Gemini Antimatter
   - `GEMINI_CLI_PROMPTS` for Gemini CLI

2. Use the task ID as the key (e.g., "2.2.1")

3. The prompt will automatically be available in the corresponding agent script
