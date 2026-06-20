"""
Assessment models for questions, tests, and student responses
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"


class AssessmentStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    status = Column(Enum(AssessmentStatus), default=AssessmentStatus.NOT_STARTED)
    score = Column(Float, nullable=True)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, default=0)
    
    # Adaptive learning metrics
    starting_level = Column(Integer, nullable=True)
    final_level = Column(Integer, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="assessments")
    responses = relationship("StudentResponse", back_populates="assessment")


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    grade_level = Column(Integer, nullable=False)
    
    # Question content
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # For multiple choice
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    
    # Metadata
    points = Column(Integer, default=1)
    time_limit = Column(Integer, nullable=True)  # in seconds
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responses = relationship("StudentResponse", back_populates="question")


class StudentResponse(Base):
    __tablename__ = "student_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Response data
    student_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer, nullable=True)  # in seconds
    
    # Timestamps
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("User", back_populates="student_responses")
    assessment = relationship("Assessment", back_populates="responses")
    question = relationship("Question", back_populates="responses")
