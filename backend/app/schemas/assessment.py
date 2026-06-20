"""
Assessment schemas for API validation
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.assessment import DifficultyLevel, QuestionType, AssessmentStatus


class QuestionBase(BaseModel):
    subject: str
    topic: str
    difficulty: DifficultyLevel
    question_type: QuestionType
    grade_level: int
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionResponse(QuestionBase):
    id: int
    points: int
    time_limit: Optional[int] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionPublic(BaseModel):
    """Question without correct answer for students"""
    id: int
    subject: str
    topic: str
    difficulty: DifficultyLevel
    question_type: QuestionType
    grade_level: int
    question_text: str
    options: Optional[List[str]] = None
    points: int
    time_limit: Optional[int] = None
    
    class Config:
        from_attributes = True


class AssessmentBase(BaseModel):
    title: str
    subject: str


class AssessmentCreate(AssessmentBase):
    student_id: int
    total_questions: int


class AssessmentResponse(AssessmentBase):
    id: int
    student_id: int
    status: AssessmentStatus
    score: Optional[float] = None
    total_questions: int
    correct_answers: int
    starting_level: Optional[int] = None
    final_level: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentResponseCreate(BaseModel):
    assessment_id: int
    question_id: int
    student_answer: str


class StudentResponseResponse(BaseModel):
    id: int
    student_id: int
    assessment_id: int
    question_id: int
    student_answer: str
    is_correct: bool
    time_taken: Optional[int] = None
    answered_at: datetime
    
    class Config:
        from_attributes = True
