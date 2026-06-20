"""
Learning Materials API Routes
Generate and retrieve personalized learning plans
"""
from typing import Optional

from app.api import deps
from app.db.database import get_db
from app.models.learning_material import LearningMaterial
from app.models.user import User
from app.services.Learning_materials import generate_learning_materials
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/generate/{subject}")
def generate_materials(
    subject: str,
    force_regenerate: bool = False,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized learning materials for current user
    
    - **subject**: Subject name (e.g., "Mathematics", "English", "Science")
    - **force_regenerate**: Force regeneration even if recent materials exist
    """
    try:
        learning_material = generate_learning_materials(
            db=db,
            student_id=current_user.id,
            subject=subject,
            force_regenerate=force_regenerate
        )
        
        if not learning_material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No weaknesses found for {subject}. Complete assessments first."
            )
        
        return {
            "id": learning_material.id,
            "subject": learning_material.subject,
            "content": learning_material.content,
            "generated_at": learning_material.generated_at,
            "expires_at": learning_material.expires_at
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate learning materials: {str(e)}"
        )


@router.get("/my-materials")
def get_my_materials(
    subject: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all active learning materials for current user
    
    - **subject**: Optional filter by subject
    """
    from sqlalchemy import func
    
    query = db.query(LearningMaterial).filter(
        LearningMaterial.student_id == current_user.id,
        LearningMaterial.is_active == 1
    )
    
    if subject:
        query = query.filter(func.lower(LearningMaterial.subject) == subject.lower())
    
    materials = query.order_by(LearningMaterial.generated_at.desc()).all()
    
    return [
        {
            "id": m.id,
            "subject": m.subject,
            "content": m.content,
            "generated_at": m.generated_at,
            "expires_at": m.expires_at,
            "schema_version": m.schema_version
        }
        for m in materials
    ]


@router.get("/materials/{material_id}")
def get_material_by_id(
    material_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific learning material by ID"""
    material = db.query(LearningMaterial).filter(
        LearningMaterial.id == material_id,
        LearningMaterial.student_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning material not found"
        )
    
    return {
        "id": material.id,
        "subject": material.subject,
        "content": material.content,
        "generated_at": material.generated_at,
        "expires_at": material.expires_at,
        "schema_version": material.schema_version
    }


@router.delete("/materials/{material_id}")
def archive_material(
    material_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Archive (soft delete) a learning material"""
    material = db.query(LearningMaterial).filter(
        LearningMaterial.id == material_id,
        LearningMaterial.student_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning material not found"
        )
    
    material.is_active = 0
    db.commit()
    
    return {"message": "Learning material archived successfully"}
