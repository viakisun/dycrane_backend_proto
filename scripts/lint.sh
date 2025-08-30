#!/bin/bash

# Exit on any error
set -e

echo "--- Running ruff linter ---"
ruff check .

echo "--- Running ruff formatter (check mode) ---"
ruff format --check .

echo "--- Running mypy type checker ---"
mypy .

echo "--- All checks passed! ---"
