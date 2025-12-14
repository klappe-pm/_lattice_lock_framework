.PHONY: lint test ci deps clean

lint:
	ruff check .
	black --check .
	lattice-lock validate

format:
	black .
	ruff check . --fix

test:
	pytest tests/unit

ci: lint test

deps:
	./scripts/update_deps.sh
	pip install -r requirements.lock

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
