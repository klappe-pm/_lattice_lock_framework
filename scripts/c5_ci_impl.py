
# IMPLEMENTATION SKELETON (Agent C5)
# Task 2.1: GitHub Actions Implementation based on 6.4.3 Design

from pathlib import Path

WORKFLOW_CONTENT = """name: Lattice Lock CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.11
      uses: actions/setup-python@v3
      with:
        python-version: "3.11"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install .[dev]
    - name: Governance Check (Sheriff)
      run: |
        lattice-lock validate
    - name: Test with pytest
      run: |
        pytest tests/unit
"""

def generate_workflow():
    dest = Path(".github/workflows")
    dest.mkdir(parents=True, exist_ok=True)

    with open(dest / "ci.yml", "w") as f:
        f.write(WORKFLOW_CONTENT)

    print("[C5] Generated .github/workflows/ci.yml")

if __name__ == "__main__":
    generate_workflow()
