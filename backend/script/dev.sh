#!/bin/bash

set -e

echo "🚀 Starting Development Environment..."

# Check if PostgreSQL is running
if ! pg_isready -q 2>/dev/null; then
    echo "📦 Starting PostgreSQL..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql
    elif command -v brew &> /dev/null; then
        brew services start postgresql@16
    fi
    sleep 2
fi

# Apply any pending migrations
echo "🔄 Checking for pending migrations..."
uv run alembic upgrade head

# Start the development server
echo "✓ Starting FastAPI server..."
echo "📍 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo ""
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
