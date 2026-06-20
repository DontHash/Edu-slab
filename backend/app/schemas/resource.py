"""
Resource schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResourceBase(BaseModel):
    type: str
    title: str
    description: Optional[str] = None
    subject: str
    difficulty: str
    level: Optional[int] = None
    duration: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None


class ResourceCreate(ResourceBase):
    pass


class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
