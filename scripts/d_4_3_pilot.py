
# IMPLEMENTATION PROTOTYPE (Agent D_4_3)
# Task 4.3: Pilot Projects Setup

import shutil
from pathlib import Path

def setup_pilot():
    """
    Creates a 'managed' pilot project to test the framework in-situ.
    """
    print("[PILOT] Setting up 'Alpha Service' pilot...")
    
    root = Path("pilot_projects/alpha_service")
    root.mkdir(parents=True, exist_ok=True)
    
    # Create lattice.yaml
    with open(root / "lattice.yaml", "w") as f:
        f.write("""
version: "2.1"
project:
  name: "alpha-service"
rules:
  - id: "enforce-types"
    severity: "error"
""")
    
    # Create valid python file
    (root / "src").mkdir(exist_ok=True)
    with open(root / "src/main.py", "w") as f:
        f.write("def handler(event: dict) -> dict:\n    return {'status': 'ok'}\n")

    print(f"[PILOT] Initialized at {root}")

if __name__ == "__main__":
    setup_pilot()
