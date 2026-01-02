#!/bin/bash
set -euo pipefail

# Scripts to sync version from pyproject.toml to __init__.py

VERSION=$(grep '^version = ' pyproject.toml | cut -d '"' -f 2)
INIT_FILE="src/lattice_lock/__init__.py"

echo "Syncing version $VERSION to $INIT_FILE"

# Detect OS for sed usage
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/^__version__ = .*/__version__ = \"$VERSION\"/" "$INIT_FILE"
else
  sed -i "s/^__version__ = .*/__version__ = \"$VERSION\"/" "$INIT_FILE"
fi

if grep -q "__version__ = \"$VERSION\"" "$INIT_FILE"; then
  echo "✅ Version synced successfully."
else
  echo "❌ Failed to sync version."
  # If __version__ line doesn't exist, append it
  echo "__version__ = \"$VERSION\"" >> "$INIT_FILE"
  echo "✅ Version appended."
fi
