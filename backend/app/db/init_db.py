"""
Database initialization script
"""
from app.db.database import engine, Base
from app.models import User, School, Assessment, Question, StudentResponse, Progress

def init_db():
    """Initialize database with tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
