#!/bin/bash

set -e

echo "⚡ Quick Setup (Minimal)"
echo "======================="
echo ""

# Install UV if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Setup environment
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s/your-super-secret-key-change-this-in-production-please-use-openssl-rand-hex-32/$SECRET_KEY/" .env
    rm .env.bak 2>/dev/null || true
fi

echo ""
echo "✅ Quick setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your database credentials"
echo "  2. Create database: createdb adaptive_learning"
echo "  3. Run migrations: make migrate"
echo "  4. Start server: make run"
