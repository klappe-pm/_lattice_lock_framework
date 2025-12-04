#!/bin/bash
set -e

echo "Setting up pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "pre-commit not found. Installing..."
    pip install pre-commit
fi

# Install hooks
pre-commit install

# Run initial validation
echo "Running initial validation..."
pre-commit run --all-files

echo "Pre-commit setup complete!"
