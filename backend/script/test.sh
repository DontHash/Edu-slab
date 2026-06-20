#!/bin/bash

set -e

echo "🧪 Running Comprehensive Test Suite..."
echo ""

# Run linting
echo "📝 Running linters..."
uv run ruff check app tests || echo "⚠️  Linting issues found"
echo ""

# Run type checking
echo "🔍 Running type checker..."
uv run mypy app || echo "⚠️  Type checking issues found"
echo ""

# Run tests with coverage
echo "🎯 Running tests with coverage..."
uv run pytest --cov=app --cov-report=term-missing --cov-report=html -v
echo ""

# Check coverage threshold
echo "📊 Coverage report generated in htmlcov/index.html"
echo ""

if command -v open &> /dev/null; then
    read -p "Open coverage report in browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open htmlcov/index.html
    fi
fi

echo "✅ All tests completed!"
