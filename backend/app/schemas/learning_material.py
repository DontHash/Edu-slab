"""
Learning materials schemas
"""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class LearningMaterialBase(BaseModel):
    subject: str
    content: Dict[str, Any]


class LearningMaterialCreate(LearningMaterialBase):
    pass


class LearningMaterialResponse(LearningMaterialBase):
    id: int
    student_id: int
    generated_at: datetime
    expires_at: Optional[datetime]
    schema_version: str
    is_active: int
    
    class Config:
        from_attributes = True
