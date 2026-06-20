#!/bin/bash

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Extract database details
DB_NAME=$(echo $DATABASE_URL | sed 's/.*\/\([^?]*\).*/\1/')
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "💾 Creating database backup..."
echo "📁 File: $BACKUP_FILE"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE
BACKUP_FILE="${BACKUP_FILE}.gz"

echo "✅ Backup created: $BACKUP_FILE"
echo "📊 Size: $(du -h $BACKUP_FILE | cut -f1)"

# Keep only last 10 backups
echo "🧹 Cleaning old backups (keeping last 10)..."
ls -t $BACKUP_DIR/*.sql.gz | tail -n +11 | xargs rm -f 2>/dev/null || true

echo "✅ Backup complete!"
