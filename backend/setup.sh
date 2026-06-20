#!/bin/bash

echo "========================================"
echo "EduAssess Backend - Setup Script"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "[1/6] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi

echo "[2/6] Activating virtual environment..."
source venv/bin/activate

echo "[3/6] Installing dependencies..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[4/6] Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created successfully"
else
    echo ".env file already exists"
fi

echo "[5/6] Initializing database..."
python -m app.db.init_db
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to initialize database"
    exit 1
fi

echo "[6/6] Seeding database with sample data..."
python -m app.db.seed
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to seed database"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Sample Credentials:"
echo "  Admin:   admin@eduassess.com / admin123"
echo "  Teacher: teacher@eduassess.com / teacher123"
echo "  Student: student@eduassess.com / student123"
echo ""
echo "To start the server, run:"
echo "  python main.py"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""
