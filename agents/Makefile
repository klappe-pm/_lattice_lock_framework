.PHONY: help install sync watch clean

help:
	@echo "Agent Sync Automation for Claude Code"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make sync       - Run one-time sync to Claude Code format"
	@echo "  make watch      - Start automatic file watcher for continuous sync"
	@echo "  make clean      - Remove generated .claude/agents directory"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt
	@echo "✓ Dependencies installed"

sync:
	@echo "Running one-time sync..."
	python3 sync_agents_to_claude.py

watch:
	@echo "Starting file watcher for automatic sync..."
	python3 watch_and_sync.py

clean:
	@echo "Cleaning generated Claude Code agents..."
	rm -rf ../.claude/agents
	@echo "✓ Cleaned"
