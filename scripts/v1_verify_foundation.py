
# VERIFICATION SCRIPT (Phase 1)
# Tasks 1.1, 1.2, 1.3: Foundation Verification

import sys
import importlib
from pathlib import Path

def verify_foundation():
    print("[VERIFY] Checking Phase 1 Foundation...")
    failures = []

    # 1.1 Orchestrator Import
    try:
        import lattice_lock_orchestrator
        print("  [PASS] 1.1 Model Orchestrator package is importable.")
    except ImportError as e:
        failures.append(f"1.1 Orchestrator Import Failed: {e}")

    # 1.2 Configuration Validator
    try:
        from lattice_lock_validator.schema import validate_lattice_schema
        print("  [PASS] 1.2 Configuration Validator importable.")
    except ImportError as e:
        failures.append(f"1.2 Validator Import Failed: {e}")

    # 1.3 Structure Enforcement
    try:
        from lattice_lock_validator.structure import validate_repository_structure
        print("  [PASS] 1.3 Structure Enforcement importable.")
    except ImportError as e:
        failures.append(f"1.3 Structure Enforcer Import Failed: {e}")

    if failures:
        print("\n[FAIL] Foundation Verification Failed:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Phase 1 Foundation Verified.")

if __name__ == "__main__":
    # Ensure src is in path
    sys.path.append(str(Path.cwd() / "src"))
    verify_foundation()
