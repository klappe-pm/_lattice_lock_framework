#!/usr/bin/env python3
"""
Verify project dependencies and environment setup.
"""
import importlib
import subprocess
import sys

REQUIRED_PACKAGES = [
    "yaml",  # PyYAML
    "jwt",  # PyJWT
    "bcrypt",
    "lattice_lock.config",
    "lattice_lock.exceptions",
]


def check_pip_dependencies():
    """
    Verify that installed packages have compatible dependencies by running `pip check`.

    Runs `pip check` with the current Python interpreter and prints status messages.

    Returns:
        bool: `True` if `pip check` reports no dependency conflicts, `False` otherwise.
    """
    print("Verifying pip dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
        print("✅ pip check passed")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip check failed")
        return False


def check_imports():
    """
    Check that each package listed in REQUIRED_PACKAGES can be imported.

    Attempts to import every package named in REQUIRED_PACKAGES and reports failures.

    Returns:
        bool: `True` if all packages imported successfully, `False` otherwise.
    """
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
    """
    Run dependency verification and exit the process with a success or failure code.

    Executes pip dependency checks and import checks, prints a success message and exits with status code 0 if both pass, otherwise prints a failure message and exits with status code 1.
    """
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
