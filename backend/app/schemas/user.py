"""
User schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional

from app.models.user import UserRole
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole


class UserCreate(UserBase):
    password: str
    school_id: Optional[int] = None
    current_level: Optional[int] = None
    fit_to_teach_level: Optional[int] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    school_id: Optional[int] = None
    is_active: Optional[bool] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    school_id: Optional[int] = None
    current_level: Optional[int] = None
    math_level: Optional[int] = None
    science_level: Optional[int] = None
    english_level: Optional[int] = None
    fit_to_teach_level: Optional[int] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
