#!/usr/bin/env python3
"""Migrates legacy YAML configuration files to the inheritance-based format."""

import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class MigrationConfig:
    base_template: str = "base/base_agent.yaml"
    mixins: List[str] = None
    vars: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.mixins is None:
            self.mixins = []
        if self.vars is None:
            self.vars = {}


def load_yaml(file_path: Path) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def detect_appropriate_mixins(content: Dict[str, Any]) -> List[str]:
    mixins = []
    if content.get('agent', {}).get('capabilities', {}).get('code_execution'):
        mixins.append("mixins/agents/code_capabilities.yaml")
    if content.get('agent', {}).get('delegation', {}).get('enabled'):
        mixins.append("mixins/agents/delegation_enabled.yaml")
    if content.get('agent', {}).get('memory', {}).get('enabled'):
        mixins.append("mixins/agents/memory_enabled.yaml")
    if content.get('agent', {}).get('tools_config'):
        mixins.append("mixins/agents/tool_access.yaml")
    return mixins


def extract_vars(content: Dict[str, Any]) -> Dict[str, Any]:
    vars_dict = {}
    agent = content.get('agent', {})
    identity = agent.get('identity', {})
    if 'version' in identity:
        vars_dict['version'] = identity['version']
    if 'status' in identity:
        vars_dict['status'] = identity['status']
    return vars_dict


def generate_frontmatter(config: MigrationConfig) -> str:
    fm = {}
    if config.base_template:
        fm['extends'] = config.base_template
    if config.mixins:
        fm['mixins'] = config.mixins
    if config.vars:
        fm['vars'] = config.vars
    if not fm:
        return "---\n---\n"
    return "---\n" + yaml.dump(fm, default_flow_style=False) + "---\n"


def remove_inherited_fields(content: Dict[str, Any], mixins: List[str]) -> Dict[str, Any]:
    agent = content.get('agent', {})
    identity = agent.get('identity', {})
    identity.pop('version', None)
    identity.pop('status', None)
    return content


def migrate_file(input_path: Path, output_path: Path, config: Optional[MigrationConfig] = None, dry_run: bool = False) -> str:
    content = load_yaml(input_path)
    
    if config is None:
        config = MigrationConfig()
        config.mixins = detect_appropriate_mixins(content)
        config.vars = extract_vars(content)
    
    content = remove_inherited_fields(content, config.mixins)
    frontmatter = generate_frontmatter(config)
    content_str = yaml.dump(content, default_flow_style=False, sort_keys=False)
    
    result = frontmatter + content_str
    
    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Migrated: {input_path} -> {output_path}")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Migrate YAML configs to inheritance format")
    parser.add_argument("input", type=Path, help="Input file or directory")
    parser.add_argument("--output", type=Path, help="Output file or directory")
    parser.add_argument("--base", type=str, default="base/base_agent.yaml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    if args.input.is_file():
        output = args.output or args.input
        config = MigrationConfig(base_template=args.base)
        result = migrate_file(args.input, output, config, args.dry_run)
        if args.dry_run:
            print(result)
    elif args.input.is_dir():
        output_dir = args.output or args.input
        for yaml_file in args.input.glob("**/*.yaml"):
            relative = yaml_file.relative_to(args.input)
            output_file = output_dir / relative
            migrate_file(yaml_file, output_file, dry_run=args.dry_run)
    else:
        print(f"Error: {args.input} is not a valid file or directory")


if __name__ == "__main__":
    main()
