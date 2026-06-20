"""
Migration: Add learning_materials table
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, MetaData,
                        String, Table, Text, create_engine)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eduassess.db")
engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()

def upgrade():
    """Create learning_materials table"""
    learning_materials = Table(
        'learning_materials',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('student_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('subject', String, nullable=False),
        Column('content', JSON, nullable=False),
        Column('generator_model', String, default='mistral-small-latest'),
        Column('schema_version', String, default='1.0'),
        Column('is_active', Integer, default=1),
        Column('expires_at', DateTime, nullable=True),
        Column('generated_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    
    metadata.create_all(engine, tables=[learning_materials])
    print("✅ learning_materials table created successfully")

def downgrade():
    """Drop learning_materials table"""
    learning_materials = Table('learning_materials', metadata, autoload_with=engine)
    learning_materials.drop(engine)
    print("✅ learning_materials table dropped")

if __name__ == "__main__":
    print("Running migration: Add learning_materials table")
    upgrade()
