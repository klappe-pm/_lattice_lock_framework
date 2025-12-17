.PHONY: lint test ci deps clean git-cleanup

lint:
	ruff check .
	black --check .
	lattice-lock validate

format:
	black .
	ruff check . --fix

test:
	pytest tests/ -m "not integration" --tb=short

ci: lint test

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
