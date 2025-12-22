#!/usr/bin/env python3
"""
Verify Agent Definitions Script

This script scans the agent definitions directory for YAML files and validates:
1. Valid YAML syntax
2. Existence of referenced subagent files
"""

import sys
import yaml
from pathlib import Path

def verify_agent_definitions(root_dir: Path):
    print(f"Scanning {root_dir} for agent definitions...")
    
    errors_found = False
    checked_count = 0
    
    # Walk through all directories
    for yaml_file in root_dir.glob("**/*.yaml"):
        if yaml_file.name == "base_agent_v2.1.yaml": 
            continue # Skip base template for now or validate differently
            
        checked_count += 1
        relative_path = yaml_file.relative_to(root_dir)
        
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            if not data or 'agent' not in data:
                # Might be a subagent file or just a fragment
                continue

            # Check subagent references
            agent_def = data.get('agent', {})
            delegation = agent_def.get('delegation', {})
            subagents = delegation.get('allowed_subagents', [])
            
            if subagents:
                for sub in subagents:
                    # Skip if it's an anchor reference (which might appear as dict if resolved, 
                    # but we are looking for 'file' keys)
                    if isinstance(sub, dict) and 'file' in sub:
                        ref_file = sub['file']
                        # Assuming relative path from the agent definition file's directory
                        target_path = yaml_file.parent / ref_file
                        
                        if not target_path.exists():
                            print(f"[FAIL] {relative_path}: Subagent file not found: {ref_file}")
                            print(f"       Resolved to: {target_path}")
                            errors_found = True
                        else:
                            # print(f"[PASS] {relative_path}: Verified subagent {ref_file}")
                            pass
                    elif isinstance(sub, dict) and 'name' in sub:
                         pass # Might be an inline definition or missing file key
                    else:
                        print(f"[WARN] {relative_path}: Unexpected subagent format: {sub}")

        except yaml.YAMLError as exc:
            print(f"[FAIL] {relative_path}: Invalid YAML syntax - {exc}")
            errors_found = True
        except Exception as e:
            print(f"[FAIL] {relative_path}: Error validating - {e}")
            errors_found = True
            
    print(f"\nScanned {checked_count} YAML files.")
    
    if errors_found:
        print("\n❌ Verification FAILED: Errors found in agent definitions.")
        sys.exit(1)
    else:
        print("\n✅ Verification PASSED: All agent definitions valid.")
        sys.exit(0)

if __name__ == "__main__":
    agents_dir = Path("docs/agents/agent_definitions")
    if not agents_dir.exists():
        print(f"Error: Directory {agents_dir} not found. Run from repo root.")
        sys.exit(1)
        
    verify_agent_definitions(agents_dir)
