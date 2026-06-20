"""Initialize database tables"""
from app.core.config import settings
from app.db.base import Base
from app.models.assessment import Assessment
from app.models.progress import Progress
from app.models.school import School
from app.models.user import User
from sqlalchemy import create_engine


def init_db():
    """Create all database tables"""
    print(f"Connecting to database: {settings.DATABASE_URL}")
    
    # Create engine
    engine = create_engine(str(settings.DATABASE_URL))
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created successfully!")

if __name__ == "__main__":
    init_db()
