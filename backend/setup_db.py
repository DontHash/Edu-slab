"""
Setup script for new developers
Run this to initialize the database with sample data
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.db.database import Base, SessionLocal
from app.models import *  # Import all models
from sqlalchemy import create_engine


def setup_database():
    """Initialize database and create sample data"""
    print("🚀 Setting up database...")
    print(f"📍 Database location: {settings.DATABASE_URL}")
    
    # Create engine
    engine = create_engine(str(settings.DATABASE_URL))
    
    # Create all tables
    print("📊 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    # Check if we need sample data
    db = SessionLocal()
    try:
        from app.models.user import User
        user_count = db.query(User).count()
        
        if user_count == 0:
            print("📝 Database is empty. You can now:")
            print("   1. Run the backend server: python main.py")
            print("   2. Register users through the frontend")
            print("   3. Or run seed scripts if available")
        else:
            print(f"✅ Database has {user_count} users already")
    finally:
        db.close()
    
    print("\n✨ Setup complete! You can now run: python main.py")

if __name__ == "__main__":
    setup_database()
