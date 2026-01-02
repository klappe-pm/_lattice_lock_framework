.PHONY: lint test ci deps clean git-cleanup check-untracked clean-untracked pre-commit

lint:
	ruff check .
	black --check .
	lattice-lock validate

format:
	black .
	ruff check . --fix

test:
	pytest tests/ -m "not integration" --tb=short

test-quick:
	pytest tests/ -m "critical" --tb=short

type-check:
	mypy src/lattice_lock

check-untracked:
	@echo "🔍 Checking for untracked files..."
	@UNTRACKED=$$(git ls-files --others --exclude-standard | \
		grep -v "^node_modules/" | \
		grep -v "^\.env" | \
		grep -v "^\.venv/" | \
		grep -v "^venv/" | \
		grep -v "^\.lattice-lock/compiled/" | \
		grep -v "^\.ruff_cache/" | \
		grep -v "^\.pytest_cache/" | \
		grep -v "^\.mypy_cache/" | \
		grep -v "^\.DS_Store" | \
		grep -v "^__pycache__/" | \
		grep -v "\.pyc$$"); \
	if [ -n "$$UNTRACKED" ]; then \
		echo "❌ Untracked files detected:"; \
		echo "$$UNTRACKED" | sed 's/^/  - /'; \
		exit 1; \
	else \
		echo "✅ No untracked files"; \
	fi

clean-untracked:
	@echo "🧹 Cleaning untracked files (excluding protected patterns)..."
	@git clean -fd -e node_modules -e .env -e .venv -e venv -e .DS_Store
	@echo "✅ Done"

pre-commit: check-untracked lint type-check
	@echo "✅ Pre-commit checks passed"

help:
	@echo "Available commands:"
	@echo "  make lint            - Run linters (ruff, black)"
	@echo "  make format          - Format code (black, ruff fix)"
	@echo "  make test            - Run unit tests"
	@echo "  make type-check      - Run static type checking"
	@echo "  make ci              - Run CI checks (lint, test)"
	@echo "  make deps            - Update dependencies"
	@echo "  make clean           - Clean build artifacts"
	@echo "  make git-cleanup     - Clean up merged branches"
	@echo "  make check-untracked - Check for untracked files"
	@echo "  make clean-untracked - Remove untracked files"
	@echo "  make pre-commit      - Run all pre-commit checks"

ci: lint type-check test

deps:
	./scripts/update_deps.sh
	pip install -r requirements.lock

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

git-cleanup:
	@echo "Pruning remote tracking branches..."
	git fetch --prune
	@echo "Deleting local merged branches..."
	git branch --merged main | grep -v '^\*\|main' | xargs -r git branch -d || true
	@echo "Done. Remaining branches:"
	@git branch
