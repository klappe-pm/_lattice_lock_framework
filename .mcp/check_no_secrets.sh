#!/bin/bash
# Pre-commit hook script to check for secrets and hardcoded paths in MCP configs
# This script is called by pre-commit with file paths as arguments

set -e

EXIT_CODE=0

for f in "$@"; do
    # Check for common secret patterns and hardcoded user paths
    if grep -qE "(sk-[a-zA-Z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN|/Users/[a-zA-Z]+/)" "$f"; then
        echo "ERROR: $f may contain secrets or hardcoded paths"
        EXIT_CODE=1
    fi
done

exit $EXIT_CODE
