#!/usr/bin/env python3
import subprocess
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def lock_dependencies():
    """
    Compiles requirements.in to requirements.lock using pip-compile.
    Ensures deterministic builds for CI.
    """
    logger.info("Locking dependencies...")
    
    req_in = Path("requirements.in")
    if not req_in.exists():
        logger.warning("requirements.in not found. Creating default.")
        with open("requirements.in", "w") as f:
            f.write("click>=8.0\npydantic>=2.0\npyyaml\n")
            
    # Check if pip-tools is installed
    try:
        subprocess.run(["pip-compile", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("pip-tools not found. Install with: pip install pip-tools")
        sys.exit(1)

    try:
        subprocess.run(
            ["pip-compile", "requirements.in", "--output-file", "requirements.lock", "--generate-hashes"],
            check=True
        )
        logger.info("Successfully generated requirements.lock")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to lock dependencies: {e}")
        sys.exit(1)

if __name__ == "__main__":
    lock_dependencies()
