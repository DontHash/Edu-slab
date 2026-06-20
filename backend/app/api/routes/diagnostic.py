"""
Diagnostic assessment API — v1 foundation endpoints.
"""
from typing import List, Optional

from app.api.deps import get_current_active_user
from app.core.assessment_blueprint import DIAGNOSTIC_BLUEPRINT
from app.core.config import settings
from app.core.skills import SKILL_AREAS
from app.db.database import get_db
from app.models.diagnostic import AssessmentSession, SessionStatus, TopicPerformance
from app.models.user import User
from app.schemas.diagnostic import (
    AssessmentSessionResponse,
    DiagnosticBlueprintResponse,
    PlatformInfoResponse,
    TopicPerformanceResponse,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/info", response_model=PlatformInfoResponse)
def platform_info():
    return PlatformInfoResponse(
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        skill_areas=SKILL_AREAS,
        features={
            "peer_matching": False,
            "legacy_rag_assessment": True,
            "diagnostic_battery": "foundation",
        },
    )


@router.get("/blueprint", response_model=DiagnosticBlueprintResponse)
def get_blueprint():
    return DiagnosticBlueprintResponse(skill_areas=SKILL_AREAS, blueprint=DIAGNOSTIC_BLUEPRINT)


@router.post("/session/start", response_model=AssessmentSessionResponse)
def start_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    active = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.student_id == current_user.id,
            AssessmentSession.status != SessionStatus.COMPLETED.value,
        )
        .first()
    )
    if active:
        return active

    session = AssessmentSession(
        student_id=current_user.id,
        status=SessionStatus.IN_PROGRESS.value,
        current_skill_area=SKILL_AREAS[0],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/session/current", response_model=Optional[AssessmentSessionResponse])
def get_current_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    session = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.student_id == current_user.id,
            AssessmentSession.status != SessionStatus.COMPLETED.value,
        )
        .first()
    )
    return session


@router.get("/topics", response_model=List[TopicPerformanceResponse])
def list_topic_performances(
    skill_area: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(TopicPerformance).filter(TopicPerformance.student_id == current_user.id)
    if skill_area:
        query = query.filter(TopicPerformance.skill_area == skill_area)
    return query.order_by(TopicPerformance.assessed_at.desc()).all()


@router.get("/topics/{skill_area}", response_model=List[TopicPerformanceResponse])
def list_topics_for_skill(
    skill_area: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if skill_area not in SKILL_AREAS:
        raise HTTPException(status_code=404, detail="Unknown skill area")
    return (
        db.query(TopicPerformance)
        .filter(
            TopicPerformance.student_id == current_user.id,
            TopicPerformance.skill_area == skill_area,
        )
        .order_by(TopicPerformance.score.asc())
        .all()
    )
