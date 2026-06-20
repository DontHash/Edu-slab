@echo off
echo ========================================
echo EduAssess Backend - Windows Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Installing dependencies...
pip install -e .
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [4/6] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env file created successfully
) else (
    echo .env file already exists
)

echo [5/6] Initializing database...
python -m app.db.init_db
if errorlevel 1 (
    echo [ERROR] Failed to initialize database
    pause
    exit /b 1
)

echo [6/6] Seeding database with sample data...
python -m app.db.seed
if errorlevel 1 (
    echo [ERROR] Failed to seed database
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete! 
echo ========================================
echo.
echo Sample Credentials:
echo   Admin:   admin@eduassess.com / admin123
echo   Teacher: teacher@eduassess.com / teacher123
echo   Student: student@eduassess.com / student123
echo.
echo To start the server, run:
echo   python main.py
echo.
echo API Documentation will be available at:
echo   http://localhost:8000/docs
echo.
pause
