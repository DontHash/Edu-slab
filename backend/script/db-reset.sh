#!/bin/bash

set -e

echo "⚠️  DATABASE RESET SCRIPT"
echo "This will DELETE ALL DATA and recreate the database."
echo ""

read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Operation cancelled"
    exit 0
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Extract database name from DATABASE_URL
DB_NAME=$(echo $DATABASE_URL | sed 's/.*\/\([^?]*\).*/\1/')

echo "🗑️  Dropping database: $DB_NAME"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"

echo "📦 Creating database: $DB_NAME"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"

echo "🔄 Running migrations..."
uv run alembic upgrade head

echo "🌱 Seeding database..."
uv run python scripts/seed_data.py

echo "✅ Database reset complete!"
