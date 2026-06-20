"""
Database detection and initialization
Automatically detects available database and configures accordingly
"""
import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


def detect_database():
    """Detect which database is available"""
    
    # Try PostgreSQL (Docker)
    postgres_urls = [
        "postgresql://eduassess:eduassess123@localhost:5432/eduassess",
        "postgresql://postgres:postgres@localhost:5432/eduassess",
    ]
    
    for url in postgres_urls:
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✓ PostgreSQL detected: {url.split('@')[1]}")
            return url
        except Exception as e:
            continue
    
    # Fallback to SQLite
    sqlite_url = "sqlite:///./eduassess.db"
    print(f"✓ Using SQLite: {sqlite_url}")
    return sqlite_url


if __name__ == "__main__":
    db_url = detect_database()
    print(f"\nDatabase URL: {db_url}")
    
    # Update config
    config_file = os.path.join(os.path.dirname(__file__), "app", "core", "config.py")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Update DATABASE_URL
        if 'DATABASE_URL: str = "postgresql://' in content:
            content = content.replace(
                'DATABASE_URL: str = "postgresql://eduassess:eduassess123@localhost:5432/eduassess"',
                f'DATABASE_URL: str = "{db_url}"'
            )
            content = content.replace(
                'DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/eduassess"',
                f'DATABASE_URL: str = "{db_url}"'
            )
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        print(f"✓ Config updated: {config_file}")
