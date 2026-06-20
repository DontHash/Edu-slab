#!/bin/bash

echo "🏥 System Health Diagnostic"
echo "==========================="
echo ""

check_ok=0
check_warn=0
check_fail=0

check_command() {
    if command -v $1 &> /dev/null; then
        version=$($1 --version 2>&1 | head -n1)
        echo "✅ $1: $version"
        ((check_ok++))
    else
        echo "❌ $1: Not installed"
        ((check_fail++))
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo "✅ File exists: $1"
        ((check_ok++))
    else
        echo "❌ File missing: $1"
        ((check_fail++))
    fi
}

echo "📋 Required Commands:"
check_command python3
check_command uv
check_command psql
check_command git

echo ""
echo "📋 Optional Commands:"
check_command docker
check_command make

echo ""
echo "📋 Required Files:"
check_file ".env"
check_file "pyproject.toml"
check_file "alembic.ini"

echo ""
echo "📋 Python Environment:"
if [ -d ".venv" ]; then
    echo "✅ Virtual environment: .venv"
    ((check_ok++))
else
    echo "⚠️  Virtual environment not found"
    ((check_warn++))
fi

echo ""
echo "📋 Database Connection:"
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    if psql "$DATABASE_URL" -c "SELECT 1;" &> /dev/null; then
        echo "✅ Database connection: OK"
        ((check_ok++))
    else
        echo "❌ Database connection: FAILED"
        ((check_fail++))
    fi
else
    echo "⚠️  Cannot test database (no .env file)"
    ((check_warn++))
fi

echo ""
echo "📋 PostgreSQL Service:"
if pg_isready -q 2>/dev/null; then
    echo "✅ PostgreSQL: Running"
    ((check_ok++))
else
    echo "❌ PostgreSQL: Not running"
    ((check_fail++))
fi

echo ""
echo "═══════════════════════════════════"
echo "Summary:"
echo "  ✅ Passed: $check_ok"
if [ $check_warn -gt 0 ]; then
    echo "  ⚠️  Warnings: $check_warn"
fi
if [ $check_fail -gt 0 ]; then
    echo "  ❌ Failed: $check_fail"
fi
echo "═══════════════════════════════════"

if [ $check_fail -eq 0 ]; then
    echo "✅ System is healthy!"
    exit 0
else
    echo "❌ System has issues that need attention"
    exit 1
fi
