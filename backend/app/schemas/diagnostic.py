"""Pydantic schemas for diagnostic API (v1 base)."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class BlueprintSection(BaseModel):
    id: str
    format: str
    count: Optional[int] = None
    count_per_topic: Optional[int] = None


class SkillBlueprint(BaseModel):
    label: str
    estimated_minutes: int
    sections: list[BlueprintSection]


class DiagnosticBlueprintResponse(BaseModel):
    version: str = "1.0"
    skill_areas: list[str]
    blueprint: dict[str, SkillBlueprint]


class AssessmentSessionResponse(BaseModel):
    id: int
    student_id: int
    status: str
    current_skill_area: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class TopicPerformanceResponse(BaseModel):
    id: int
    skill_area: str
    topic_name: str
    score: float
    accuracy_percentage: Optional[int] = None
    weakness_level: str
    strengths: list[str] = []
    weaknesses: list[str] = []
    reasoning: Optional[str] = None
    assessed_at: datetime

    class Config:
        from_attributes = True


class PlatformInfoResponse(BaseModel):
    name: str
    version: str
    skill_areas: list[str]
    features: dict[str, Any]
