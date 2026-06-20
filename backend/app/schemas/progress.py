"""
Progress schemas for API validation
"""
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class ProgressResponse(BaseModel):
    id: int
    student_id: int
    overall_progress: float
    total_assessments: int
    total_tests_completed: int
    subject_progress: Dict
    strengths: List[str]
    weaknesses: List[str]
    recommended_topics: List[str]
    attendance_rate: float
    last_activity: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProgressUpdate(BaseModel):
    overall_progress: Optional[float] = None
    total_assessments: Optional[int] = None
    total_tests_completed: Optional[int] = None
    subject_progress: Optional[Dict] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recommended_topics: Optional[List[str]] = None
    attendance_rate: Optional[float] = None
