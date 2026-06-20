"""
Learning resources model
"""
import enum
from datetime import datetime

from app.db.database import Base
from sqlalchemy import Column, DateTime, Enum, Integer, String, Text


class ResourceType(str, enum.Enum):
    VIDEO = "video"
    ARTICLE = "article"
    EXERCISE = "exercise"
    FLASHCARD = "flashcard"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    level = Column(Integer, nullable=True)
    duration = Column(String, nullable=True)
    url = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
