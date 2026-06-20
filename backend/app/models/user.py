"""
User model for students, teachers, and admins
"""
import enum
from datetime import datetime

from app.db.database import Base
from sqlalchemy import (Boolean, Column, DateTime, Enum, Float, ForeignKey,
                        Integer, String)
from sqlalchemy.orm import relationship


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Foreign Keys
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="users")
    assessments = relationship("Assessment", back_populates="student")
    progress = relationship("Progress", back_populates="student", uselist=False)
    student_responses = relationship("StudentResponse", back_populates="student")
    
    # Student-specific fields
    current_level = Column(Integer, nullable=True)
    math_level = Column(Integer, nullable=True)
    science_level = Column(Integer, nullable=True)
    english_level = Column(Integer, nullable=True)
    fit_to_teach_level = Column(Integer, nullable=True)  # Deprecated — peer matching removed
    speaking_english_level = Column(Integer, nullable=True)
    writing_english_level = Column(Integer, nullable=True)
    location = Column(String, nullable=True)  # Deprecated — peer matching removed
    latitude = Column(Float, nullable=True)  # Deprecated
    longitude = Column(Float, nullable=True)  # Deprecated

    assessment_sessions = relationship("AssessmentSession", back_populates="student")
    topic_performances = relationship("TopicPerformance", back_populates="student")
