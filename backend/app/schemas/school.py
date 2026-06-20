"""
School schemas for API validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class SchoolBase(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    principal_name: Optional[str] = None


class SchoolCreate(SchoolBase):
    pass


class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    principal_name: Optional[str] = None
    is_active: Optional[bool] = None


class SchoolResponse(SchoolBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
