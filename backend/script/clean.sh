#!/bin/bash

echo "🧹 Cleaning project..."

# Remove Python cache
echo "🗑️  Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Remove test cache
echo "🗑️  Removing test cache..."
rm -rf .pytest_cache 2>/dev/null || true
rm -rf .coverage 2>/dev/null || true
rm -rf htmlcov 2>/dev/null || true

# Remove build artifacts
echo "🗑️  Removing build artifacts..."
rm -rf build dist 2>/dev/null || true

# Remove linter cache
echo "🗑️  Removing linter cache..."
rm -rf .ruff_cache .mypy_cache 2>/dev/null || true

# Remove logs
echo "🗑️  Cleaning logs..."
rm -rf logs/*.log 2>/dev/null || true

echo "✅ Cleanup complete!"
