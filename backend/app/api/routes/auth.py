"""
Authentication routes for login and registration
"""
from datetime import timedelta
from typing import Optional

from app.core.config import settings
from app.core.security import (create_access_token, decode_token,
                               get_password_hash, verify_password)
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (LoginRequest, Token, UserCreate, UserResponse,
                              UserUpdate)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    print(f"[DEBUG AUTH] Validating token: {token[:20]}..." if token else "[DEBUG AUTH] No token provided")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        print("[DEBUG AUTH] Token decode failed")
        raise credentials_exception
    
    email: str = payload.get("sub")
    print(f"[DEBUG AUTH] Token decoded, email: {email}")
    
    if email is None:
        print("[DEBUG AUTH] No email in token")
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        print(f"[DEBUG AUTH] User not found for email: {email}")
        raise credentials_exception
    
    print(f"[DEBUG AUTH] Authenticated user ID: {user.id}, name: {user.name}, email: {user.email}")
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user without default subject levels
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        school_id=user_data.school_id,
        current_level=user_data.current_level if user_data.current_level else (10 if user_data.role == "student" else None),
        math_level=None,
        science_level=None,
        english_level=None,
        fit_to_teach_level=user_data.fit_to_teach_level,
        location=user_data.location,
        latitude=user_data.latitude,
        longitude=user_data.longitude
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login")
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login and get access token with user data"""
    print(f"[DEBUG LOGIN] Login attempt for email: {credentials.email}")
    
    # Authenticate user
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        print(f"[DEBUG LOGIN] Login failed for: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        print(f"[DEBUG LOGIN] Inactive user: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    print(f"[DEBUG LOGIN] Login successful - User ID: {user.id}, Name: {user.name}, Email: {user.email}")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "school_id": user.school_id,
            "current_level": user.current_level,
            "math_level": user.math_level,
            "science_level": user.science_level,
            "english_level": user.english_level,
            "fit_to_teach_level": user.fit_to_teach_level,
            "location": user.location,
            "latitude": user.latitude,
            "longitude": user.longitude
        }
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.patch("/profile", response_model=UserResponse)
def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile (location)"""
    print(f"[DEBUG UPDATE PROFILE] User ID: {current_user.id}")
    
    if profile_data.location is not None:
        current_user.location = profile_data.location
        print(f"[DEBUG UPDATE PROFILE] Updated location: {profile_data.location}")
    if profile_data.latitude is not None:
        current_user.latitude = profile_data.latitude
        print(f"[DEBUG UPDATE PROFILE] Updated latitude: {profile_data.latitude}")
    if profile_data.longitude is not None:
        current_user.longitude = profile_data.longitude
        print(f"[DEBUG UPDATE PROFILE] Updated longitude: {profile_data.longitude}")
    
    db.commit()
    db.refresh(current_user)
    
    print(f"[DEBUG UPDATE PROFILE] Profile updated successfully")
    return current_user
