"""
User management routes
"""
from typing import List

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.email is not None:
        current_user.email = user_data.email
    if user_data.school_id is not None:
        current_user.school_id = user_data.school_id
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/locations")
def get_user_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get anonymized locations of all active users for usage map visualization"""
    users = db.query(User).filter(
        User.latitude.isnot(None),
        User.longitude.isnot(None),
        User.location.isnot(None)
    ).all()
    
    locations = [
        {
            "latitude": user.latitude,
            "longitude": user.longitude,
            "location": user.location
        }
        for user in users
    ]
    
    return {"locations": locations, "count": len(locations)}


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID (admin/teacher only)"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users (admin/teacher only)"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users
