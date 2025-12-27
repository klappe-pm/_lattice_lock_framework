#!/usr/bin/env python3
"""
Verify project dependencies and environment setup.
"""
import importlib
import subprocess
import sys

REQUIRED_PACKAGES = [
    "yaml",  # PyYAML
    "jwt",   # PyJWT
    "bcrypt",
    "lattice_lock.config",
    "lattice_lock.exceptions",
]

def check_pip_dependencies():
    """Run pip check to verify installed packages have compatible dependencies."""
    print("Verifying pip dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
        print("✅ pip check passed")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip check failed")
        return False

def check_imports():
    """Verify critical packages can be imported."""
    print("\nVerifying imports...")
    all_passed = True
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
            print(f"✅ Import successful: {package}")
        except ImportError as e:
            print(f"❌ Import failed: {package} - {e}")
            all_passed = False
    return all_passed

def main():
    pip_ok = check_pip_dependencies()
    imports_ok = check_imports()
    
    if pip_ok and imports_ok:
        print("\n✨ All dependency checks passed!")
        sys.exit(0)
    else:
        print("\n🚨 Dependency verification failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
