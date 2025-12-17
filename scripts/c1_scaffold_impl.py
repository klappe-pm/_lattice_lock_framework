from pathlib import Path

import yaml


def init_project(target_dir: str = "."):
    """
    SCAFFOLDING AGENT (Claude C1) OUTPUT
    Task 1.4: Scaffolding CLI
    """
    root = Path(target_dir)
    print(f"Initializing Lattice Lock Project in {root.resolve()}...")

    # 1. Directory Structure
    dirs = ["src", "tests/unit", "tests/integration", ".lattice", "docs"]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)
        print(f"  [+] Created {d}/")

    # 2. Default Config
    config = {"version": "2.1", "project": {"name": root.name}, "governance": {"strict": True}}
    with open(root / "lattice.yaml", "w") as f:
        yaml.dump(config, f)
    print("  [+] Created lattice.yaml")

    # 3. Gitignore
    with open(root / ".gitignore", "w") as f:
        f.write(".lattice/\n__pycache__/\n*.pyc\n.env\n")
    print("  [+] Created .gitignore")

    print("\nProject Initialized Successfully.")


if __name__ == "__main__":
    init_project()
