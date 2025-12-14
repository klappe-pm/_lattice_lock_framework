#!/bin/bash
set -e

# Compile requirements.in to requirements.lock
# Ensures deterministic builds

if ! command -v pip-compile &> /dev/null
then
    echo "pip-compile could not be found. Installing pip-tools..."
    pip install pip-tools
fi

echo "Updating requirements.lock..."
pip-compile requirements.in --output-file requirements.lock

echo "Done."
