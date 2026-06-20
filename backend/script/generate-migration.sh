#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/generate-migration.sh \"migration message\""
    echo "Example: ./scripts/generate-migration.sh \"add user preferences table\""
    exit 1
fi

MESSAGE="$1"

echo "🔄 Generating migration: $MESSAGE"

uv run alembic revision --autogenerate -m "$MESSAGE"

echo ""
echo "✅ Migration created!"
echo "📝 Review the generated file in alembic/versions/"
echo "🚀 Apply with: make migrate"
