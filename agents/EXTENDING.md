# Extending the Agent Sync System

This guide explains how to add new sync targets to the agent synchronization system.

## Architecture Overview

The sync system is built with three main components:

### 1. SyncTarget (Dataclass)
Defines a sync destination with:
- **name**: Unique identifier
- **base_path**: Directory path
- **subfolder**: Optional subdirectory
- **converter**: Function to convert YAML to target format
- **description**: Human-readable description

### 2. AgentConverter (Static Class)
Contains converter methods that transform YAML agent definitions into different markdown formats:
- `to_claude_code_format()`: Creates Claude Code-compatible markdown
- `to_lattice_lock_format()`: Creates documentation-focused markdown
- *Add your own converter methods here*

### 3. AgentSyncer (Class)
Orchestrates the sync process:
- Reads YAML files from `agent_definitions/`
- Applies converter functions
- Writes output to target directories
- Tracks and reports progress

## Adding a New Sync Target

Follow these steps to add a new sync target:

### Step 1: Create a Converter Function

Add a new static method to the `AgentConverter` class in `sync_agents_to_claude.py`:

```python
@staticmethod
def to_your_format(agent_data: Dict[str, Any], is_subagent: bool = False) -> str:
    """
    Convert agent YAML data to your custom format.
    
    Args:
        agent_data: Parsed YAML agent definition
        is_subagent: Whether this is a subagent
        
    Returns:
        Markdown string in your custom format
    """
    # Extract agent information
    agent_info = agent_data.get('agent', {})
    identity = agent_info.get('identity', {})
    directive = agent_info.get('directive', {})
    scope = agent_info.get('scope', {})
    
    # Extract specific fields
    name = identity.get('name', 'unnamed-agent')
    role = identity.get('role', 'AI Assistant')
    description = identity.get('description', '')
    
    # Build your markdown format
    lines = []
    lines.append(f"# {name}")
    lines.append(f"**Role**: {role}")
    
    if description:
        lines.append(f"\\n{description}")
    
    # Add more sections as needed
    
    return '\\n'.join(lines)
```

### Step 2: Define the Sync Target

In the `create_sync_targets()` function, add your target to the `all_targets` dictionary:

```python
def create_sync_targets(agents_root: Path, project_root: Path, 
                        target_choice: str) -> List[SyncTarget]:
    # Define all available sync targets
    all_targets = {
        'claude-project': SyncTarget(...),
        'claude-user': SyncTarget(...),
        'lattice-lock': SyncTarget(...),
        
        # Add your new target here
        'your-target-name': SyncTarget(
            name='your-target-name',
            base_path=project_root / 'your' / 'base' / 'path',
            subfolder='optional_subfolder',  # Or None
            converter=AgentConverter.to_your_format,
            description='Description of what this target is for'
        ),
    }
    # ... rest of function
```

### Step 3: Add to Target Combinations

Update the `target_combinations` dictionary to include your target in sync options:

```python
# Map user choices to target combinations
target_combinations = {
    '1': ['claude-project', 'lattice-lock'],
    '2': ['claude-user', 'lattice-lock'],
    '3': ['claude-project', 'claude-user', 'lattice-lock'],
    '4': ['lattice-lock'],
    # Add a new option for your target
    '5': ['your-target-name'],
    '6': ['claude-project', 'lattice-lock', 'your-target-name'],
}
```

### Step 4: Update User Interface

In the `main()` function, add your option to the menu:

```python
print("\\nSync Targets:")
print("1. Claude Code (project-level) + Lattice Lock archive [RECOMMENDED]")
print("2. Claude Code (user-level) + Lattice Lock archive")
print("3. All targets (project + user + archive)")
print("4. Lattice Lock archive only")
print("5. Your custom target only")  # Add this
print("6. Claude + Lattice + Your target")  # Add this

choice = input("\\nEnter choice (1-6) [default: 1]: ").strip() or "1"
```

### Step 5: Test Your Integration

Run the sync script:

```bash
python3 sync_agents_to_claude.py
```

Select your new option and verify:
1. Files are created in the correct location
2. The format matches your expectations
3. All agents (main and subagents) are converted

## Example: Adding a JSON Export Target

Here's a complete example adding JSON export:

```python
# Step 1: Add converter
@staticmethod
def to_json_format(agent_data: Dict[str, Any], is_subagent: bool = False) -> str:
    """Export agent as JSON for API consumption."""
    import json
    
    agent_info = agent_data.get('agent', {})
    
    # Create a clean JSON structure
    export_data = {
        'identity': agent_info.get('identity', {}),
        'directive': agent_info.get('directive', {}),
        'scope': agent_info.get('scope', {}),
        'is_subagent': is_subagent
    }
    
    # Note: Return as markdown with JSON code block for consistency
    json_str = json.dumps(export_data, indent=2)
    return f"```json\\n{json_str}\\n```\\n"

# Step 2: Add target
'json-export': SyncTarget(
    name='json-export',
    base_path=agents_root / 'exports',
    subfolder='json',
    converter=AgentConverter.to_json_format,
    description='JSON export for API integration'
),

# Step 3: Add to combinations
'5': ['json-export'],
'6': ['claude-project', 'lattice-lock', 'json-export'],
```

## Best Practices

### Converter Functions
- Always handle missing fields gracefully with `.get()` and defaults
- Document the expected output format in docstrings
- Return a string (markdown or other text format)
- Use consistent formatting within your converter

### Target Configuration
- Use descriptive names (lowercase with hyphens)
- Set appropriate base paths (avoid hardcoding user paths)
- Provide clear descriptions for the UI
- Consider whether a subfolder makes sense

### Testing
- Test with agents that have minimal fields
- Test with fully-populated agents
- Verify both main agents and subagents convert correctly
- Check error handling for malformed YAML

### Documentation
- Update SYNC_README.md with information about your target
- Add examples to QUICKSTART.md if relevant
- Document any special requirements or use cases

## Common Patterns

### Conditional Formatting
```python
if is_subagent:
    # Format for subagents
else:
    # Format for main agents
```

### Extracting All Fields Safely
```python
identity = agent_info.get('identity', {})
name = identity.get('name', 'unnamed')
role = identity.get('role', 'Unknown')
description = identity.get('description', '')
version = identity.get('version', '1.0.0')
```

### Building Markdown Sections
```python
lines = []
lines.append("# Header")
lines.append("")  # Blank line

if some_condition:
    lines.append("## Section")
    lines.append(content)
    lines.append("")

return '\\n'.join(lines)
```

### Using YAML Frontmatter
```python
frontmatter = {
    'key': 'value',
    'list': ['item1', 'item2']
}

yaml_str = yaml.dump(frontmatter, default_flow_style=False)
markdown = f"---\\n{yaml_str}---\\n\\nContent here\\n"
```

## Troubleshooting

**Q: My converter isn't being called**
- Check that you spelled the target name correctly in all locations
- Verify the target is added to `target_combinations`
- Make sure the converter function signature matches: `(agent_data, is_subagent) -> str`

**Q: Files are created but empty/corrupted**
- Add print statements in your converter to debug
- Check that your converter returns a non-empty string
- Verify YAML agent data is being parsed correctly

**Q: Some agents are missing**
- Ensure your converter handles both main agents and subagents
- Check file glob patterns match your YAML filenames
- Verify the source directory path is correct

## Need Help?

If you encounter issues:
1. Check the existing converter implementations for reference
2. Add debug print statements to trace execution
3. Test with a single simple agent first
4. Review the AgentSyncer class for how converters are called
