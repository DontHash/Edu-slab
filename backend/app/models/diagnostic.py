"""
Diagnostic assessment models (v1 foundation).
"""
import enum
from datetime import datetime

from app.db.database import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship


class SessionStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, default=SessionStatus.NOT_STARTED.value, nullable=False)
    current_skill_area = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("User", back_populates="assessment_sessions")
    topic_performances = relationship("TopicPerformance", back_populates="session")


class TopicPerformance(Base):
    """Per-topic results used for reports, roadmaps, and learning guides."""

    __tablename__ = "topic_performances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("assessment_sessions.id"), nullable=True)
    skill_area = Column(String, nullable=False, index=True)
    topic_name = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    accuracy_percentage = Column(Integer, nullable=True)
    weakness_level = Column(String, nullable=False)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    reasoning = Column(Text, nullable=True)
    assessed_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", back_populates="topic_performances")
    session = relationship("AssessmentSession", back_populates="topic_performances")
