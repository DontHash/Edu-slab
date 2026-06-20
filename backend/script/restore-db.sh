#!/bin/bash

set -e

BACKUP_DIR="backups"

echo "📦 Available backups:"
echo ""

backups=($(ls -t $BACKUP_DIR/*.sql.gz 2>/dev/null))

if [ ${#backups[@]} -eq 0 ]; then
    echo "❌ No backups found in $BACKUP_DIR"
    exit 1
fi

for i in "${!backups[@]}"; do
    size=$(du -h "${backups[$i]}" | cut -f1)
    echo "$((i+1)). ${backups[$i]} ($size)"
done

echo ""
read -p "Select backup number to restore (or 'q' to quit): " selection

if [ "$selection" = "q" ]; then
    echo "❌ Operation cancelled"
    exit 0
fi

if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#backups[@]} ]; then
    echo "❌ Invalid selection"
    exit 1
fi

BACKUP_FILE="${backups[$((selection-1))]}"

echo ""
echo "⚠️  WARNING: This will replace all current data!"
read -p "Type 'yes' to confirm: " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Operation cancelled"
    exit 0
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "🔄 Restoring from: $BACKUP_FILE"

# Decompress and restore
gunzip -c $BACKUP_FILE | psql $DATABASE_URL

echo "✅ Database restored successfully!"
