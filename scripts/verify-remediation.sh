#!/bin/bash
set -e

echo "=== Lattice Lock Remediation Verification ==="
echo "Date: $(date)"
echo ""

# Phase 1 checks
echo "--- Phase 1: Critical Path ---"
python -c "from lattice_lock.cli.commands.gauntlet import gauntlet_command" && echo "✓ Gauntlet import OK" || echo "✗ Gauntlet import FAILED"
python -c "from lattice_lock.agents.prompt_architect.cli import main" && echo "✓ Prompt Architect CLI OK" || echo "✗ Prompt Architect CLI FAILED"
lattice-lock --help > /dev/null 2>&1 && echo "✓ CLI help OK" || echo "✗ CLI help FAILED"

# Phase 2 checks
echo ""
echo "--- Phase 2: Agent Definitions ---"
LEGACY_AGENTS=$(grep -rl "lattice_lock_agents" docs/agents/ 2>/dev/null | wc -l)
echo "Files with legacy agent paths: $LEGACY_AGENTS"

# Phase 3 checks
echo ""
echo "--- Phase 3: Test Suite ---"
ASSERT_TRUE=$(grep -r "assert True" tests/agents/ 2>/dev/null | wc -l)
echo "Placeholder assertions: $ASSERT_TRUE"

echo ""
echo "=== Verification Complete ==="
