#!/bin/bash
# Run GPU runner using uv

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install dependencies and run
uv run python gpurunner.py "$@"

