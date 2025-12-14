
# IMPLEMENTATION SKELETON (Agent C3)
# Task 5.4: Prompt Tracker Integration

import json
import hashlib
from datetime import datetime
from pathlib import Path

TRACKER_FILE = ".lattice/prompt_state.json"

def get_file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def update_tracker(prompts_dir: str = "prompts"):
    """
    Scans Markdown prompt files and updates state tracking.
    """
    state = {}
    if Path(TRACKER_FILE).exists():
        with open(TRACKER_FILE) as f:
            state = json.load(f)
            
    root = Path(prompts_dir)
    changes = []
    
    for p_file in root.glob("**/*.md"):
        current_hash = get_file_hash(p_file)
        stored = state.get(str(p_file))
        
        if not stored or stored['hash'] != current_hash:
            changes.append(p_file.name)
            state[str(p_file)] = {
                "hash": current_hash,
                "updated_at": datetime.now().isoformat()
            }
            
    # Save State
    Path(TRACKER_FILE).parent.mkdir(exist_ok=True)
    with open(TRACKER_FILE, "w") as f:
        json.dump(state, f, indent=2)
        
    print(f"[C3] Prompt Tracker updated. {len(changes)} files changed.")

if __name__ == "__main__":
    update_tracker()
