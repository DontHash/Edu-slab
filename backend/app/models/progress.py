"""
Progress tracking model for student learning
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Overall progress
    overall_progress = Column(Float, default=0.0)
    total_assessments = Column(Integer, default=0)
    total_tests_completed = Column(Integer, default=0)
    
    # Subject-specific progress (stored as JSON)
    subject_progress = Column(JSON, default={})
    
    # Learning metrics
    strengths = Column(JSON, default=[])
    weaknesses = Column(JSON, default=[])
    recommended_topics = Column(JSON, default=[])
    
    # Attendance and activity
    attendance_rate = Column(Float, default=0.0)
    last_activity = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="progress")
