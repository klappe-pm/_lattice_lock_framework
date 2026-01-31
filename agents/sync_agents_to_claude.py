#!/usr/bin/env python3
"""
Sync agent definition files to Claude Code subagent format.

This script converts YAML agent definitions to Claude Code-compatible
Markdown files with YAML frontmatter and syncs them to multiple targets:
- Claude Code format (.claude/agents/)
- Lattice Lock markdown archive (agents/markdown/)
- Extensible for additional sync targets

Architecture:
- SyncTarget: Defines where and how to sync agent files
- AgentConverter: Handles conversion from YAML to Markdown
- AgentSyncer: Orchestrates the sync process across all targets
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class SyncTarget:
    """
    Defines a sync target destination and its conversion requirements.
    
    Attributes:
        name: Human-readable name for this target (e.g., 'claude-code', 'lattice-lock')
        base_path: Base directory path for this target
        subfolder: Optional subfolder within base_path (e.g., 'agents')
        converter: Function to convert agent data to target format
        description: Description of what this target is for
    """
    name: str
    base_path: Path
    subfolder: Optional[str]
    converter: Callable[[Dict[str, Any], bool], str]
    description: str
    
    def get_target_dir(self) -> Path:
        """Get the full target directory path."""
        if self.subfolder:
            return self.base_path / self.subfolder
        return self.base_path


class AgentConverter:
    """
    Handles conversion of agent YAML data to various output formats.
    
    This class contains static methods for different conversion formats.
    Add new conversion methods here for additional output formats.
    """
    
    @staticmethod
    def to_claude_code_format(agent_data: Dict[str, Any], is_subagent: bool = False) -> str:
        """
        Convert agent YAML data to Claude Code Markdown format with YAML frontmatter.
        
        Args:
            agent_data: Parsed YAML agent definition
            is_subagent: Whether this is a subagent (affects delegation section)
            
        Returns:
            Markdown string with YAML frontmatter compatible with Claude Code
        """
        agent_info = agent_data.get('agent', {})
        identity = agent_info.get('identity', {})
        directive = agent_info.get('directive', {})
        scope = agent_info.get('scope', {})
        delegation = agent_info.get('delegation', {})
        
        # Extract basic information
        name = identity.get('name', 'unnamed-agent')
        role = identity.get('role', 'AI Assistant')
        description = identity.get('description', f'A specialized {role}')
        version = identity.get('version', '1.0.0')
        
        # Build YAML frontmatter for Claude Code
        frontmatter = {
            'name': name,
            'description': description,
        }
        
        # Add tools - default to common Claude Code tools
        frontmatter['tools'] = ['Read', 'Write', 'Edit', 'Bash', 'Glob', 'Grep']
        
        # Add model preference (default to sonnet)
        frontmatter['model'] = 'sonnet'
        
        # Build the markdown content (system prompt)
        content_parts = []
        
        # Add role and identity
        content_parts.append(f"You are a {role}.")
        
        # Add primary goal if specified
        if directive.get('primary_goal'):
            content_parts.append(f"\n## Primary Goal\n{directive['primary_goal']}")
        
        # Add scope information if available
        if scope:
            content_parts.append("\n## Scope")
            if scope.get('can_access'):
                access_paths = '\n'.join([f"- {path}" for path in scope['can_access']])
                content_parts.append(f"\n### Can Access\n{access_paths}")
            if scope.get('can_modify'):
                modify_paths = '\n'.join([f"- {path}" for path in scope['can_modify']])
                content_parts.append(f"\n### Can Modify\n{modify_paths}")
        
        # Add delegation information for main agents
        if delegation.get('enabled') and delegation.get('allowed_subagents'):
            subagents = '\n'.join([f"- {sa}" for sa in delegation['allowed_subagents']])
            content_parts.append(f"\n## Delegation\nYou can delegate to the following subagents:\n{subagents}")
        
        # Add general instructions
        content_parts.append("\n## Key Practices")
        content_parts.append("- Follow best practices for your domain")
        content_parts.append("- Communicate clearly and concisely")
        content_parts.append("- Always validate your work before reporting completion")
        
        if not is_subagent:
            content_parts.append("- Use delegation to specialized subagents when appropriate")
        
        # Convert frontmatter to YAML string
        yaml_header = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        
        # Combine into final markdown
        markdown = f"---\n{yaml_header}---\n{''.join(content_parts)}\n"
        
        return markdown
    
    @staticmethod
    def to_lattice_lock_format(agent_data: Dict[str, Any], is_subagent: bool = False) -> str:
        """
        Convert agent YAML data to Lattice Lock documentation markdown format.
        
        This format is more documentation-focused and includes all agent metadata
        in a human-readable format for archival and reference purposes.
        
        Args:
            agent_data: Parsed YAML agent definition
            is_subagent: Whether this is a subagent
            
        Returns:
            Markdown string suitable for Lattice Lock documentation
        """
        agent_info = agent_data.get('agent', {})
        identity = agent_info.get('identity', {})
        directive = agent_info.get('directive', {})
        scope = agent_info.get('scope', {})
        delegation = agent_info.get('delegation', {})
        
        # Extract information
        name = identity.get('name', 'unnamed-agent')
        role = identity.get('role', 'AI Assistant')
        description = identity.get('description', '')
        version = identity.get('version', '1.0.0')
        status = identity.get('status', 'active')
        inherits_from = identity.get('inherits_from', None)
        
        # Build markdown document
        lines = []
        
        # Title and metadata
        lines.append(f"# {name.replace('_', ' ').title()}")
        lines.append("")
        
        # Metadata table
        lines.append("## Metadata")
        lines.append("")
        lines.append(f"- **Name**: `{name}`")
        lines.append(f"- **Role**: {role}")
        lines.append(f"- **Version**: {version}")
        lines.append(f"- **Status**: {status}")
        lines.append(f"- **Type**: {'Subagent' if is_subagent else 'Main Agent'}")
        if inherits_from:
            lines.append(f"- **Inherits From**: `{inherits_from}`")
        lines.append("")
        
        # Description
        if description:
            lines.append("## Description")
            lines.append("")
            lines.append(description)
            lines.append("")
        
        # Directive
        if directive:
            lines.append("## Directive")
            lines.append("")
            if directive.get('primary_goal'):
                lines.append(f"**Primary Goal**: {directive['primary_goal']}")
                lines.append("")
        
        # Scope
        if scope:
            lines.append("## Scope")
            lines.append("")
            
            if scope.get('can_access'):
                lines.append("### Can Access")
                lines.append("")
                for path in scope['can_access']:
                    lines.append(f"- `{path}`")
                lines.append("")
            
            if scope.get('can_modify'):
                lines.append("### Can Modify")
                lines.append("")
                for path in scope['can_modify']:
                    lines.append(f"- `{path}`")
                lines.append("")
        
        # Delegation
        if delegation.get('enabled'):
            lines.append("## Delegation")
            lines.append("")
            lines.append(f"**Enabled**: Yes")
            lines.append("")
            
            if delegation.get('allowed_subagents'):
                lines.append("### Allowed Subagents")
                lines.append("")
                for subagent in delegation['allowed_subagents']:
                    lines.append(f"- `{subagent}`")
                lines.append("")
        
        # Source information
        lines.append("---")
        lines.append("")
        lines.append("*This documentation was auto-generated from YAML agent definitions.*")
        lines.append("")
        
        return '\n'.join(lines)


def load_yaml_agent(file_path: Path) -> Dict[str, Any]:
    """
    Load and parse a YAML agent definition file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Parsed YAML data as a dictionary
        
    Raises:
        yaml.YAMLError: If the file cannot be parsed
        FileNotFoundError: If the file doesn't exist
    """
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


class AgentSyncer:
    """
    Orchestrates the syncing of agent definitions to multiple targets.
    
    This class handles the conversion and syncing process, tracking progress
    and handling errors for each target destination.
    """
    
    def __init__(self, source_dir: Path, targets: List[SyncTarget]):
        """
        Initialize the syncer.
        
        Args:
            source_dir: Directory containing agent_definitions/
            targets: List of SyncTarget objects to sync to
        """
        self.source_dir = source_dir
        self.targets = targets
    
    def sync_all_targets(self) -> Dict[str, int]:
        """
        Sync agents to all configured targets.
        
        Returns:
            Dictionary mapping target names to count of synced agents
        """
        results = {}
        
        for target in self.targets:
            print(f"\nSyncing to {target.name}: {target.description}")
            print("-" * 60)
            
            try:
                count = self._sync_to_target(target)
                results[target.name] = count
                print(f"✓ Synced {count} agents to {target.name}")
            except Exception as e:
                print(f"✗ Error syncing to {target.name}: {e}")
                results[target.name] = 0
        
        return results
    
    def _sync_to_target(self, target: SyncTarget) -> int:
        """
        Sync all agents to a specific target.
        
        Args:
            target: The SyncTarget to sync to
            
        Returns:
            Number of agents successfully synced
        """
        # Create target directory if it doesn't exist
        target_dir = target.get_target_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        
        converted_count = 0
        
        # Iterate through all agent definition folders
        for agent_folder in self.source_dir.iterdir():
            if not agent_folder.is_dir():
                continue
            
            # Process main agent definition files
            main_agent_files = list(agent_folder.glob('*_agent_definition.yaml'))
            
            for main_agent_file in main_agent_files:
                try:
                    agent_data = load_yaml_agent(main_agent_file)
                    
                    # Convert using target's converter function
                    converted_content = target.converter(agent_data, is_subagent=False)
                    
                    # Get agent name for output file
                    agent_name = agent_data.get('agent', {}).get('identity', {}).get('name', 'unnamed')
                    output_file = target_dir / f"{agent_name}.md"
                    
                    # Write to target
                    with open(output_file, 'w') as f:
                        f.write(converted_content)
                    
                    print(f"  ✓ {agent_name} (main agent)")
                    converted_count += 1
                    
                except Exception as e:
                    print(f"  ✗ Error converting {main_agent_file.name}: {e}")
            
            # Process subagent files
            subagents_dir = agent_folder / 'subagents'
            if subagents_dir.exists():
                for subagent_file in subagents_dir.glob('*.yaml'):
                    try:
                        agent_data = load_yaml_agent(subagent_file)
                        
                        # Convert using target's converter function
                        converted_content = target.converter(agent_data, is_subagent=True)
                        
                        # Get agent name for output file
                        agent_name = agent_data.get('agent', {}).get('identity', {}).get('name', 'unnamed')
                        output_file = target_dir / f"{agent_name}.md"
                        
                        # Write to target
                        with open(output_file, 'w') as f:
                            f.write(converted_content)
                        
                        print(f"  ✓ {agent_name} (subagent)")
                        converted_count += 1
                        
                    except Exception as e:
                        print(f"  ✗ Error converting {subagent_file.name}: {e}")
        
        return converted_count


def create_sync_targets(agents_root: Path, project_root: Path, 
                        target_choice: str) -> List[SyncTarget]:
    """
    Create a list of sync targets based on user choice.
    
    This function defines all available sync targets and returns the ones
    selected by the user. To add a new sync target:
    
    1. Create a new SyncTarget with:
       - Unique name
       - Target path
       - Converter function from AgentConverter
       - Description
    
    2. Add it to the all_targets dictionary
    
    3. Update the target selection logic
    
    Args:
        agents_root: Path to the agents/ directory
        project_root: Path to the project root
        target_choice: User's choice ('1', '2', '3', etc.)
        
    Returns:
        List of SyncTarget objects to sync to
    """
    # Define all available sync targets
    all_targets = {
        'claude-project': SyncTarget(
            name='claude-project',
            base_path=project_root / '.claude',
            subfolder='agents',
            converter=AgentConverter.to_claude_code_format,
            description='Claude Code project-level agents'
        ),
        'claude-user': SyncTarget(
            name='claude-user',
            base_path=Path.home() / '.claude',
            subfolder='agents',
            converter=AgentConverter.to_claude_code_format,
            description='Claude Code user-level agents (available globally)'
        ),
        'lattice-lock': SyncTarget(
            name='lattice-lock',
            base_path=agents_root,
            subfolder='markdown',
            converter=AgentConverter.to_lattice_lock_format,
            description='Lattice Lock documentation archive'
        ),
    }
    
    # Map user choices to target combinations
    # Add new options here for different target combinations
    target_combinations = {
        '1': ['claude-project', 'lattice-lock'],  # Project + archive
        '2': ['claude-user', 'lattice-lock'],     # User + archive
        '3': ['claude-project', 'claude-user', 'lattice-lock'],  # All
        '4': ['lattice-lock'],                    # Archive only
    }
    
    # Get selected target names
    selected_names = target_combinations.get(target_choice, ['claude-project', 'lattice-lock'])
    
    # Return the selected SyncTarget objects
    return [all_targets[name] for name in selected_names if name in all_targets]


def sync_agents_to_claude(source_dir: Path, target_dir: Path) -> int:
    """
    Legacy function for backward compatibility with watch_and_sync.py.
    
    Syncs agents to a single target directory using Claude Code format.
    
    Args:
        source_dir: Path to agents/agent_definitions
        target_dir: Path to target directory (will be created if doesn't exist)
        
    Returns:
        Number of agents synced
    """
    target = SyncTarget(
        name='legacy',
        base_path=target_dir,
        subfolder=None,
        converter=AgentConverter.to_claude_code_format,
        description='Legacy sync target'
    )
    
    syncer = AgentSyncer(source_dir, [target])
    results = syncer.sync_all_targets()
    return results.get('legacy', 0)


def main():
    """
    Main entry point for the sync script.
    
    Handles user interaction and orchestrates the sync process across
    all selected targets.
    """
    # Define paths
    script_dir = Path(__file__).parent
    agents_root = script_dir
    source_dir = agents_root / 'agent_definitions'
    project_root = script_dir.parent
    
    print("=" * 60)
    print("Agent Sync Tool - Multi-Target Converter")
    print("=" * 60)
    
    # Validate source directory
    if not source_dir.exists():
        print(f"\n✗ Error: Source directory not found: {source_dir}")
        print("   Make sure you're running this from the agents/ directory")
        return 1
    
    # Display options to user
    print(f"\nSource: {source_dir}")
    print("\nSync Targets:")
    print("1. Claude Code (project-level) + Lattice Lock archive [RECOMMENDED]")
    print("2. Claude Code (user-level) + Lattice Lock archive")
    print("3. All targets (project + user + archive)")
    print("4. Lattice Lock archive only")
    
    choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"
    
    # Create sync targets based on choice
    targets = create_sync_targets(agents_root, project_root, choice)
    
    if not targets:
        print("\n✗ Error: Invalid choice or no targets selected")
        return 1
    
    # Display what will be synced
    print(f"\n{'=' * 60}")
    print("Will sync to the following targets:")
    for target in targets:
        print(f"  • {target.name}: {target.get_target_dir()}")
        print(f"    ({target.description})")
    print(f"{'=' * 60}\n")
    
    # Confirm with user
    confirm = input("Proceed with sync? [Y/n]: ").strip().lower()
    if confirm and confirm not in ['y', 'yes']:
        print("\nSync cancelled.")
        return 0
    
    print(f"\n{'=' * 60}")
    print("Starting sync process...")
    print(f"{'=' * 60}")
    
    # Perform the sync
    syncer = AgentSyncer(source_dir, targets)
    results = syncer.sync_all_targets()
    
    # Display summary
    print(f"\n{'=' * 60}")
    print("Sync Complete - Summary")
    print(f"{'=' * 60}")
    
    total = sum(results.values())
    for target_name, count in results.items():
        status = "✓" if count > 0 else "✗"
        print(f"{status} {target_name}: {count} agents")
    
    print(f"\n{'=' * 60}")
    print(f"✓ Total: {total} agent files synced across {len(results)} targets")
    print(f"{'=' * 60}")
    
    return 0


if __name__ == '__main__':
    exit(main())
