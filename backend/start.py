#!/usr/bin/env python
"""
Quick start script to run the backend server
"""
import subprocess
import sys
import os

def main():
    print("🚀 Starting EduAssess Backend Server...")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Creating from .env.example...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ Created .env file")
        else:
            print("❌ .env.example not found")
            sys.exit(1)
    
    # Initialize database
    print("\n📊 Initializing database...")
    subprocess.run([sys.executable, "-m", "app.db.init_db"])
    
    # Ask to seed database
    seed = input("\n🌱 Seed database with sample data? (y/n): ").lower()
    if seed == 'y':
        subprocess.run([sys.executable, "-m", "app.db.seed"])
    
    # Start server
    print("\n🌐 Starting server at http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server\n")
    
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    main()
