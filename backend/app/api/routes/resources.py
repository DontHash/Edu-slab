"""
Learning resources routes
"""
from typing import List

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.models.resource import Resource
from app.models.user import User
from app.schemas.resource import ResourceCreate, ResourceResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[ResourceResponse])
def get_resources(
    subject: str = None,
    difficulty: str = None,
    resource_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get learning resources with optional filters"""
    query = db.query(Resource)
    
    if subject:
        query = query.filter(Resource.subject == subject)
    if difficulty:
        query = query.filter(Resource.difficulty == difficulty)
    if resource_type:
        query = query.filter(Resource.type == resource_type)
    
    resources = query.all()
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific resource"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    return resource


@router.post("/", response_model=ResourceResponse)
def create_resource(
    resource_data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new resource (teacher/admin only)"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    resource = Resource(**resource_data.dict())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    return resource


@router.get("/recommended/{student_id}", response_model=List[ResourceResponse])
def get_recommended_resources(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recommended resources for a student based on their progress"""
    # Check permissions
    if current_user.role == "student" and student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get student's weaknesses from progress
    from app.models.progress import Progress
    progress = db.query(Progress).filter(Progress.student_id == student_id).first()
    
    if not progress or not progress.weaknesses:
        # Return general resources if no progress data
        resources = db.query(Resource).limit(10).all()
        return resources
    
    # Get resources matching student's weak areas
    # This is a simplified version - you can make it more sophisticated
    resources = db.query(Resource).filter(
        Resource.difficulty.in_(["Beginner", "Intermediate"])
    ).limit(10).all()
    
    return resources
