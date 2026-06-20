#!/bin/bash

LOGS_DIR="logs"

mkdir -p $LOGS_DIR

if [ "$1" = "follow" ] || [ "$1" = "-f" ]; then
    echo "📊 Following logs (Ctrl+C to stop)..."
    tail -f $LOGS_DIR/app.log 2>/dev/null || echo "No logs yet. Start the server first."
else
    echo "📊 Recent logs:"
    echo "════════════════════════════════════════════════════════════"
    tail -n 50 $LOGS_DIR/app.log 2>/dev/null || echo "No logs yet. Start the server first."
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Use: ./scripts/logs.sh follow   to follow logs in real-time"
fi
