"""
Progress tracking routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.progress import Progress
from app.schemas.progress import ProgressResponse, ProgressUpdate

router = APIRouter()


@router.get("/student/{student_id}", response_model=ProgressResponse)
def get_student_progress(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get progress for a student"""
    # Check permissions
    if current_user.role == "student" and student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    progress = db.query(Progress).filter(Progress.student_id == student_id).first()
    
    # Create progress record if it doesn't exist
    if not progress:
        progress = Progress(student_id=student_id)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    return progress


@router.put("/student/{student_id}", response_model=ProgressResponse)
def update_student_progress(
    student_id: int,
    progress_data: ProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update student progress (teacher/admin only)"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    progress = db.query(Progress).filter(Progress.student_id == student_id).first()
    
    if not progress:
        # Create if doesn't exist
        progress = Progress(student_id=student_id)
        db.add(progress)
    
    # Update fields
    for field, value in progress_data.dict(exclude_unset=True).items():
        setattr(progress, field, value)
    
    db.commit()
    db.refresh(progress)
    
    return progress
