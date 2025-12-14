
# IMPLEMENTATION PROTOTYPE (Agent C_4_2)
# Task 4.2: Tutorial Content Generator

from pathlib import Path

TUTORIAL_CONTENT = """
# Getting Started with Lattice Lock

## 1. Installation
`pip install lattice-lock-framework`

## 2. Initialize
`lattice-lock init`

## 3. Configure
Edit `lattice.yaml` to define your rules.

## 4. Run Governance
`lattice-lock validate` ensures your code complies with the rules.
"""

def generate_tutorial():
    print("[DOCS] Generating tutorial content...")
    dest = Path("docs/guides")
    dest.mkdir(parents=True, exist_ok=True)
    
    with open(dest / "quickstart.md", "w") as f:
        f.write(TUTORIAL_CONTENT)
        
    print(f"[DOCS] Created {dest}/quickstart.md")

if __name__ == "__main__":
    generate_tutorial()
