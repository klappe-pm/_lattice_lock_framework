# IMPLEMENTATION SKELETON (Agent C8)
# Task 2.5: Gauntlet Test Runner Implementation

import sys

import pytest


def run_gauntlet(target_dir: str = "tests/gauntlet"):
    """
    Runs semantic tests using pytest.
    """
    print(f"GAUNTLET: Running semantic tests in {target_dir}...")

    # Check if directory exists
    from pathlib import Path

    if not Path(target_dir).exists():
        print(f"[WARN] No gauntlet tests found in {target_dir}. Skipping.")
        return

    # Run pytest programmatically
    retcode = pytest.main(["-v", target_dir])

    if retcode == 0:
        print("[PASS] All semantic tests passed.")
    else:
        print(f"[FAIL] Semantic tests failed (Exit Code: {retcode}).")
        sys.exit(retcode)


if __name__ == "__main__":
    run_gauntlet()
