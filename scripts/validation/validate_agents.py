#!/usr/bin/env python3
import os
import yaml
import sys

def validate_agent_file(filepath):
    """Validates a single agent YAML file against v2.1 spec requirements."""
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            
        if not data:
            return False, "Empty file"
            
        # Check root keys
        required_sections = [
            "agent", "directive", "responsibilities", "scope", "context",
            "planning", "estimation", "model_selection", "delegation",
            "workflow", "output", "error_handling", "interaction",
            "metrics", "guardrails", "examples", "tests", "metadata", "versioning"
        ]
        
        missing = [sec for sec in required_sections if sec not in data]
        if missing:
            return False, f"Missing sections: {', '.join(missing)}"
            
        # Check identity
        if "identity" not in data.get("agent", {}):
            return False, "Missing agent.identity"
            
        # Check model selection
        if "strategies" not in data.get("model_selection", {}):
            return False, "Missing model_selection.strategies"
            
        return True, "Valid"
        
    except Exception as e:
        return False, f"YAML Error: {str(e)}"

def main():
    root_dir = "Agents-v3"
    if not os.path.exists(root_dir):
        print(f"Error: {root_dir} does not exist.")
        sys.exit(1)
        
    total_files = 0
    valid_files = 0
    errors = []
    
    print(f"Scanning {root_dir}...")
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                total_files += 1
                filepath = os.path.join(dirpath, filename)
                is_valid, message = validate_agent_file(filepath)
                
                if is_valid:
                    valid_files += 1
                else:
                    errors.append(f"{filepath}: {message}")
                    
    print(f"\nValidation Complete.")
    print(f"Total Agent Files: {total_files}")
    print(f"Valid Files: {valid_files}")
    print(f"Invalid Files: {len(errors)}")
    
    if errors:
        print("\nErrors found:")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("\nAll files passed validation! ✅")
        sys.exit(0)

if __name__ == "__main__":
    main()
