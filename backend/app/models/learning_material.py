"""
Learning materials model - stores AI-generated personalized learning plans
"""
from datetime import datetime

from app.db.database import Base
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship


class LearningMaterial(Base):
    """Store personalized learning plans for students"""
    __tablename__ = "learning_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    
    # Generated content (JSON)
    content = Column(JSON, nullable=False)  # Full JSON with chapters, resources, roadmap
    
    # Metadata
    generator_model = Column(String, default="mistral-small-latest")
    schema_version = Column(String, default="1.0")
    
    # Status tracking
    is_active = Column(Integer, default=1)  # 1=active, 0=archived
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("User", backref="learning_materials")
