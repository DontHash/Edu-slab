"""
API routes for peer-to-peer matching
"""
from typing import List, Optional

from app.api import deps
from app.models.matching import (HelpOffer, HelpRequest, HelpRequestStatus,
                                 MatchStatus, PeerMatch,
                                 StudentChapterPerformance)
from app.models.user import User, UserRole
from app.schemas import matching as matching_schemas
from app.services.matching_service import get_peer_matching_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/update-my-performance")
def update_my_performance(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update current user's chapter performance from evaluation files.
    """
    matching_service = get_peer_matching_service(db)
    count = matching_service.update_student_chapter_performances(current_user.id)
    
    print(f"[DEBUG] Populated {count} chapter performance records for user {current_user.id}")
    
    return {
        "message": "Performance data updated successfully", 
        "user_id": current_user.id,
        "records_created": count
    }


@router.post("/populate-all-performances")
def populate_all_performances(
    db: Session = Depends(deps.get_db),
):
    """
    Populate all users' performance data from assessment files.
    Open endpoint for testing - no authentication required.
    """
    matching_service = get_peer_matching_service(db)
    
    # Get all users
    all_users = db.query(User).all()
    results = []
    
    for user in all_users:
        try:
            count = matching_service.update_student_chapter_performances(user.id)
            results.append({
                "user_id": user.id,
                "name": user.name,
                "records_created": count
            })
            print(f"[DEBUG] Populated {count} records for user {user.id} ({user.name})")
        except Exception as e:
            import traceback
            print(f"[ERROR] Failed to populate user {user.id}: {e}")
            print(traceback.format_exc())
            results.append({
                "user_id": user.id,
                "name": user.name,
                "error": str(e)
            })
    
    return {
        "message": "Performance data populated for all users",
        "results": results
    }


@router.post("/update-performance/{user_id}")
def update_student_performance(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update student chapter performance from evaluation files.
    Should be called after assessment evaluation is complete.
    """
    # Check authorization
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this student's performance"
        )
    
    matching_service = get_peer_matching_service(db)
    matching_service.update_student_chapter_performances(user_id)
    
    return {"message": "Performance data updated successfully", "user_id": user_id}


@router.post("/create-matches", response_model=matching_schemas.MatchingResponse)
def create_chapter_matches(
    request: matching_schemas.MatchingRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create peer-to-peer matches for a specific chapter using Gale-Shapley algorithm.
    Only teachers and admins can create matches.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can create matches"
        )
    
    matching_service = get_peer_matching_service(db)
    
    # Create matches
    matches = matching_service.create_matches(
        subject=request.subject,
        chapter=request.chapter,
        meeting_type=request.meeting_type,
        location=request.location,
        school_id=request.school_id or current_user.school_id,
    )
    
    # Build detailed response
    matches_with_details = []
    for match in matches:
        tutor = db.query(User).filter(User.id == match.tutor_id).first()
        learner = db.query(User).filter(User.id == match.learner_id).first()
        
        if tutor and learner:
            matches_with_details.append(
                matching_schemas.PeerMatchWithDetails(
                    id=match.id,
                    tutor_id=match.tutor_id,
                    learner_id=match.learner_id,
                    chapter=match.chapter,
                    subject=match.subject,
                    meeting_type=match.meeting_type.value if hasattr(match.meeting_type, 'value') else match.meeting_type,
                    tutor_score=match.tutor_score,
                    learner_score=match.learner_score,
                    compatibility_score=match.compatibility_score,
                    preference_rank_tutor=match.preference_rank_tutor,
                    preference_rank_learner=match.preference_rank_learner,
                    status=match.status.value,
                    matched_at=match.matched_at,
                    accepted_at=match.accepted_at,
                    completed_at=match.completed_at,
                    tutor_name=tutor.name,
                    tutor_email=tutor.email,
                    tutor_grade=tutor.current_level,
                    tutor_fit_to_teach_level=tutor.fit_to_teach_level,
                    tutor_location=tutor.location,
                    learner_name=learner.name,
                    learner_email=learner.email,
                    learner_grade=learner.current_level,
                    learner_location=learner.location,
                    tutor_school=tutor.school.name if tutor.school else None,
                    learner_school=learner.school.name if learner.school else None,
                )
            )
    
    return matching_schemas.MatchingResponse(
        success=True,
        message=f"Created {len(matches)} matches for {request.chapter}",
        matches_created=len(matches),
        matches=matches_with_details,
    )


@router.get("/my-matches", response_model=matching_schemas.StudentMatchesResponse)
def get_my_matches(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get all matches for the current student.
    Returns separate lists for tutoring and learning matches.
    """
    matching_service = get_peer_matching_service(db)
    
    # Get matches where student is tutor
    tutoring_matches = matching_service.get_student_matches(current_user.id, role='tutor')
    
    # Get matches where student is learner
    learning_matches = matching_service.get_student_matches(current_user.id, role='learner')
    
    # Build detailed responses
    def build_match_details(match: PeerMatch) -> matching_schemas.PeerMatchWithDetails:
        tutor = db.query(User).filter(User.id == match.tutor_id).first()
        learner = db.query(User).filter(User.id == match.learner_id).first()
        
        return matching_schemas.PeerMatchWithDetails(
            id=match.id,
            tutor_id=match.tutor_id,
            learner_id=match.learner_id,
            chapter=match.chapter,
            subject=match.subject,
            meeting_type=match.meeting_type.value if hasattr(match.meeting_type, 'value') else match.meeting_type,
            tutor_score=match.tutor_score,
            learner_score=match.learner_score,
            compatibility_score=match.compatibility_score,
            preference_rank_tutor=match.preference_rank_tutor,
            preference_rank_learner=match.preference_rank_learner,
            status=match.status.value,
            matched_at=match.matched_at,
            accepted_at=match.accepted_at,
            completed_at=match.completed_at,
            tutor_name=tutor.name if tutor else "Unknown",
            tutor_email=tutor.email if tutor else "unknown@example.com",
            tutor_grade=tutor.current_level if tutor else None,
            tutor_fit_to_teach_level=tutor.fit_to_teach_level if tutor else None,
            tutor_location=tutor.location if tutor else None,
            learner_name=learner.name if learner else "Unknown",
            learner_email=learner.email if learner else "unknown@example.com",
            learner_grade=learner.current_level if learner else None,
            learner_location=learner.location if learner else None,
            tutor_school=tutor.school.name if tutor and tutor.school else None,
            learner_school=learner.school.name if learner and learner.school else None,
        )
    
    tutoring_details = [build_match_details(m) for m in tutoring_matches]
    learning_details = [build_match_details(m) for m in learning_matches]
    
    return matching_schemas.StudentMatchesResponse(
        tutoring_matches=tutoring_details,
        learning_matches=learning_details,
        total_matches=len(tutoring_matches) + len(learning_matches),
    )


@router.patch("/match/{match_id}/status")
def update_match_status(
    match_id: int,
    status_update: matching_schemas.MatchStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update the status of a match (accept, reject, complete).
    Students can only update their own matches.
    """
    match = db.query(PeerMatch).filter(PeerMatch.id == match_id).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Verify user is part of this match
    if current_user.id not in [match.tutor_id, match.learner_id]:
        if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this match"
            )
    
    # Update status
    try:
        new_status = MatchStatus(status_update.status)
        match.status = new_status
        
        # Update timestamps
        from datetime import datetime
        if new_status == MatchStatus.ACCEPTED and not match.accepted_at:
            match.accepted_at = datetime.utcnow()
        elif new_status == MatchStatus.COMPLETED and not match.completed_at:
            match.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Match status updated", "match_id": match_id, "status": new_status.value}
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status_update.status}"
        )


@router.get("/available-chapters", response_model=List[matching_schemas.ChapterListResponse])
def get_available_chapters(
    subject: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get list of chapters available for matching, grouped by subject.
    """
    query = db.query(
        StudentChapterPerformance.subject,
        StudentChapterPerformance.chapter,
    ).distinct()
    
    if subject:
        query = query.filter(StudentChapterPerformance.subject == subject)
    
    if current_user.school_id:
        from app.models.user import User as UserModel
        query = query.join(UserModel).filter(UserModel.school_id == current_user.school_id)
    
    results = query.all()
    
    # Group by subject
    subject_chapters = {}
    for subj, chapter in results:
        if subj not in subject_chapters:
            subject_chapters[subj] = []
        subject_chapters[subj].append(chapter)
    
    # Build response
    response = []
    for subj, chapters in subject_chapters.items():
        # Count students with performance in this subject
        student_count = db.query(StudentChapterPerformance.student_id).filter(
            StudentChapterPerformance.subject == subj
        ).distinct().count()
        
        response.append(
            matching_schemas.ChapterListResponse(
                subject=subj,
                chapters=sorted(chapters),
                total_students=student_count,
            )
        )
    
    return response


@router.get("/stats", response_model=matching_schemas.MatchingStatsResponse)
def get_matching_stats(
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get statistics about potential tutors and learners.
    """
    from app.services.matching_service import AsymmetricGaleShapleyMatcher
    
    matcher = AsymmetricGaleShapleyMatcher()
    
    # Base query
    query = db.query(StudentChapterPerformance)
    
    if subject:
        query = query.filter(StudentChapterPerformance.subject == subject)
    if chapter:
        query = query.filter(StudentChapterPerformance.chapter == chapter)
    
    if current_user.school_id:
        from app.models.user import User as UserModel
        query = query.join(UserModel).filter(UserModel.school_id == current_user.school_id)
    
    all_performances = query.all()
    
    # Count potential tutors and learners
    tutors = set()
    learners = set()
    chapters_set = set()
    subjects_set = set()
    
    for perf in all_performances:
        subjects_set.add(perf.subject)
        chapters_set.add(perf.chapter)
        
        if perf.score >= matcher.tutor_threshold:
            tutors.add(perf.student_id)
        if perf.score <= matcher.learner_threshold:
            learners.add(perf.student_id)
    
    return matching_schemas.MatchingStatsResponse(
        total_potential_tutors=len(tutors),
        total_potential_learners=len(learners),
        chapters_available=sorted(list(chapters_set)),
        subjects_available=sorted(list(subjects_set)),
    )


@router.get("/student/{student_id}/performance", response_model=List[matching_schemas.StudentChapterPerformance])
def get_student_performance(
    student_id: int,
    subject: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get chapter performance for a specific student.
    """
    # Authorization check
    if current_user.id != student_id and current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this student's performance"
        )
    
    query = db.query(StudentChapterPerformance).filter(
        StudentChapterPerformance.student_id == student_id
    )
    
    if subject:
        query = query.filter(StudentChapterPerformance.subject == subject)
    
    performances = query.all()
    
    return [
        matching_schemas.StudentChapterPerformance(
            id=p.id,
            student_id=p.student_id,
            subject=p.subject,
            chapter=p.chapter,
            score=p.score,
            accuracy_percentage=p.accuracy_percentage,
            weakness_level=p.weakness_level,
            total_questions_attempted=p.total_questions_attempted,
            correct_answers=p.correct_answers,
            is_strong_chapter=p.is_strong_chapter,
            is_weak_chapter=p.is_weak_chapter,
            last_assessed_at=p.last_assessed_at,
            updated_at=p.updated_at,
        )
        for p in performances
    ]


@router.get("/potential-matches")
async def get_potential_matches(
    meeting_type: str = "online",
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Get all potential matches for the current student across all subjects.
    Uses SUBJECT-LEVEL matching to support cross-grade peer learning
    (e.g., Grade 10 student tutoring Grade 7 student in Science).
    
    Returns subjects where they can tutor others and subjects where they need help.
    
    Query params:
    - meeting_type: "online" (default) or "physical" (location-based)
    """
    matching_service = get_peer_matching_service(db)
    
    # For physical meetups, use user's location
    location = current_user.location if meeting_type == "physical" else None
    
    print(f"[DEBUG MATCHING] Getting matches for user {current_user.id} ({current_user.name})")
    print(f"  Meeting type: {meeting_type}")
    print(f"  Location: {location}")
    print(f"  GPS: lat={current_user.latitude}, lng={current_user.longitude}")
    
    # Get subject-level matches (works across different grade levels)
    subject_matches = matching_service.get_subject_level_matches(
        current_user.id,
        meeting_type=meeting_type,
        location=location,
        limit=10
    )
    
    print(f"[DEBUG MATCHING] User {current_user.id} ({current_user.name}):")
    print(f"  Can tutor: {len(subject_matches['can_tutor'])} subjects")
    print(f"  Needs help: {len(subject_matches['needs_help'])} subjects")
    for subj in subject_matches['can_tutor']:
        print(f"    - Can tutor {subj['subject']}: {len(subj['potential_learners'])} learners")
    for subj in subject_matches['needs_help']:
        print(f"    - Needs help in {subj['subject']}: {len(subj['potential_tutors'])} tutors")
    
    # Transform to frontend-friendly format
    potential_matches = []
    
    # Add tutoring opportunities
    for tutor_subject in subject_matches['can_tutor']:
        for learner in tutor_subject['potential_learners']:
            potential_matches.append({
                'as_tutor': True,
                'as_learner': False,
                'subject': tutor_subject['subject'],
                'chapter': None,  # Subject-level match, no specific chapter
                'tutor_id': current_user.id,
                'tutor_name': current_user.name,
                'tutor_email': current_user.email,
                'tutor_score': tutor_subject['my_average_score'],
                'tutor_grade': current_user.current_level,
                'tutor_location': current_user.location,
                'learner_id': learner['user_id'],
                'learner_name': learner['name'],
                'learner_email': learner['email'],
                'learner_score': learner['average_score'],
                'learner_grade': learner['grade'],
                'learner_location': learner['location'],
                'compatibility_score': learner['compatibility_score'],
            })
    
    # Add learning opportunities
    for help_subject in subject_matches['needs_help']:
        for tutor in help_subject['potential_tutors']:
            potential_matches.append({
                'as_tutor': False,
                'as_learner': True,
                'subject': help_subject['subject'],
                'chapter': None,  # Subject-level match, no specific chapter
                'tutor_id': tutor['user_id'],
                'tutor_name': tutor['name'],
                'tutor_email': tutor['email'],
                'tutor_score': tutor['average_score'],
                'tutor_grade': tutor['grade'],
                'tutor_location': tutor['location'],
                'learner_id': current_user.id,
                'learner_name': current_user.name,
                'learner_email': current_user.email,
                'learner_score': help_subject['my_average_score'],
                'learner_grade': current_user.current_level,
                'learner_location': current_user.location,
                'compatibility_score': tutor['compatibility_score'],
            })
    
    return {
        'potential_matches': potential_matches,
        'total_count': len(potential_matches)
    }


@router.post("/request-help", response_model=matching_schemas.HelpRequest)
def request_help(
    request: matching_schemas.HelpRequestCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Student requests help in a specific chapter.
    This creates a help request that tutors can see and accept.
    """
    # Get student's score in this chapter
    student_perf = db.query(StudentChapterPerformance).filter(
        StudentChapterPerformance.student_id == current_user.id,
        StudentChapterPerformance.subject == request.subject,
        StudentChapterPerformance.chapter == request.chapter,
    ).first()
    
    student_score = student_perf.score if student_perf else None
    
    # Create help request
    help_request = HelpRequest(
        student_id=current_user.id,
        subject=request.subject,
        chapter=request.chapter,
        description=request.description,
        urgency=request.urgency,
        student_score=student_score,
        status=HelpRequestStatus.OPEN,
    )
    
    db.add(help_request)
    db.commit()
    db.refresh(help_request)
    
    return help_request


@router.get("/help-requests", response_model=List[matching_schemas.HelpRequestWithDetails])
def get_help_requests(
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get help requests. Students see their own, tutors see open requests they can help with.
    """
    query = db.query(HelpRequest)
    
    if current_user.role == UserRole.STUDENT:
        # Students see only their own requests
        query = query.filter(HelpRequest.student_id == current_user.id)
    else:
        # Teachers/admins see all
        pass
    
    if subject:
        query = query.filter(HelpRequest.subject == subject)
    if chapter:
        query = query.filter(HelpRequest.chapter == chapter)
    if status:
        query = query.filter(HelpRequest.status == status)
    
    requests = query.order_by(HelpRequest.created_at.desc()).all()
    
    # Build detailed response
    result = []
    for req in requests:
        student = db.query(User).filter(User.id == req.student_id).first()
        tutor = db.query(User).filter(User.id == req.matched_with).first() if req.matched_with else None
        
        if student:
            result.append(
                matching_schemas.HelpRequestWithDetails(
                    id=req.id,
                    student_id=req.student_id,
                    subject=req.subject,
                    chapter=req.chapter,
                    description=req.description,
                    urgency=req.urgency,
                    student_score=req.student_score,
                    status=req.status.value,
                    matched_with=req.matched_with,
                    created_at=req.created_at,
                    updated_at=req.updated_at,
                    fulfilled_at=req.fulfilled_at,
                    student_name=student.name,
                    student_email=student.email,
                    student_school=student.school.name if student.school else None,
                    tutor_name=tutor.name if tutor else None,
                )
            )
    
    return result


@router.post("/offer-help", response_model=matching_schemas.HelpOffer)
def offer_help(
    offer: matching_schemas.HelpOfferCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Student offers to help others in a specific chapter.
    This creates a help offer that learners can see.
    """
    # Get student's score in this chapter
    student_perf = db.query(StudentChapterPerformance).filter(
        StudentChapterPerformance.student_id == current_user.id,
        StudentChapterPerformance.subject == offer.subject,
        StudentChapterPerformance.chapter == offer.chapter,
    ).first()
    
    tutor_score = student_perf.score if student_perf else None
    
    # Check if student qualifies to tutor
    matching_service = get_peer_matching_service(db)
    if tutor_score and tutor_score < matching_service.matcher.tutor_threshold:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Your score ({tutor_score}/10) is below the tutoring threshold ({matching_service.matcher.tutor_threshold}/10)"
        )
    
    # Create help offer
    help_offer = HelpOffer(
        tutor_id=current_user.id,
        subject=offer.subject,
        chapter=offer.chapter,
        description=offer.description,
        availability=offer.availability,
        tutor_score=tutor_score,
        max_students=offer.max_students,
        is_active=True,
        current_students=0,
    )
    
    db.add(help_offer)
    db.commit()
    db.refresh(help_offer)
    
    return help_offer


@router.get("/help-offers", response_model=List[matching_schemas.HelpOfferWithDetails])
def get_help_offers(
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get available help offers from tutors.
    """
    query = db.query(HelpOffer)
    
    if active_only:
        query = query.filter(HelpOffer.is_active == True)
    
    if subject:
        query = query.filter(HelpOffer.subject == subject)
    if chapter:
        query = query.filter(HelpOffer.chapter == chapter)
    
    offers = query.order_by(HelpOffer.tutor_score.desc()).all()
    
    # Build detailed response
    result = []
    for offer in offers:
        tutor = db.query(User).filter(User.id == offer.tutor_id).first()
        
        if tutor:
            result.append(
                matching_schemas.HelpOfferWithDetails(
                    id=offer.id,
                    tutor_id=offer.tutor_id,
                    subject=offer.subject,
                    chapter=offer.chapter,
                    description=offer.description,
                    availability=offer.availability,
                    tutor_score=offer.tutor_score,
                    max_students=offer.max_students,
                    is_active=offer.is_active,
                    current_students=offer.current_students,
                    created_at=offer.created_at,
                    updated_at=offer.updated_at,
                    tutor_name=tutor.name,
                    tutor_email=tutor.email,
                    tutor_school=tutor.school.name if tutor.school else None,
                )
            )
    
    return result


@router.post("/accept-help-request/{request_id}")
def accept_help_request(
    request_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Tutor accepts a help request and creates a match.
    """
    help_request = db.query(HelpRequest).filter(HelpRequest.id == request_id).first()
    
    if not help_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Help request not found")
    
    if help_request.status != HelpRequestStatus.OPEN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Help request is no longer open")
    
    # Verify tutor qualification
    tutor_perf = db.query(StudentChapterPerformance).filter(
        StudentChapterPerformance.student_id == current_user.id,
        StudentChapterPerformance.subject == help_request.subject,
        StudentChapterPerformance.chapter == help_request.chapter,
    ).first()
    
    matching_service = get_peer_matching_service(db)
    if not tutor_perf or tutor_perf.score < matching_service.matcher.tutor_threshold:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't meet the tutoring requirements for this chapter"
        )
    
    # Get learner performance
    learner_perf = db.query(StudentChapterPerformance).filter(
        StudentChapterPerformance.student_id == help_request.student_id,
        StudentChapterPerformance.subject == help_request.subject,
        StudentChapterPerformance.chapter == help_request.chapter,
    ).first()
    
    # Calculate compatibility
    compatibility = matching_service.matcher.calculate_compatibility_score(
        tutor_perf.score,
        learner_perf.score if learner_perf else 0,
    )
    
    # Create match
    match = PeerMatch(
        tutor_id=current_user.id,
        learner_id=help_request.student_id,
        chapter=help_request.chapter,
        subject=help_request.subject,
        tutor_score=tutor_perf.score,
        learner_score=learner_perf.score if learner_perf else 0,
        compatibility_score=compatibility,
        status=MatchStatus.PENDING,
    )
    
    db.add(match)
    
    # Update help request
    help_request.status = HelpRequestStatus.IN_PROGRESS
    help_request.matched_with = current_user.id
    from datetime import datetime
    help_request.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Help request accepted", "match_id": match.id, "request_id": request_id}


@router.post("/connect-with-peer")
def connect_with_peer(
    request: matching_schemas.DirectMatchRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a direct match request between two students.
    Either a tutor reaching out to a learner or vice versa.
    """
    matching_service = get_peer_matching_service(db)
    
    # Get both students' performances
    my_perf = db.query(StudentChapterPerformance).filter(
        StudentChapterPerformance.student_id == current_user.id,
        StudentChapterPerformance.subject == request.subject,
        StudentChapterPerformance.chapter == request.chapter,
    ).first()
    
    peer_perf = db.query(StudentChapterPerformance).filter(
        StudentChapterPerformance.student_id == request.peer_student_id,
        StudentChapterPerformance.subject == request.subject,
        StudentChapterPerformance.chapter == request.chapter,
    ).first()
    
    if not my_perf or not peer_perf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both students must have performance data for this chapter"
        )
    
    # Determine who is tutor and who is learner
    if my_perf.score > peer_perf.score:
        tutor_id, learner_id = current_user.id, request.peer_student_id
        tutor_score, learner_score = my_perf.score, peer_perf.score
    else:
        tutor_id, learner_id = request.peer_student_id, current_user.id
        tutor_score, learner_score = peer_perf.score, my_perf.score
    
    # Calculate compatibility
    compatibility = matching_service.matcher.calculate_compatibility_score(
        tutor_score, learner_score
    )
    
    # Create match
    match = PeerMatch(
        tutor_id=tutor_id,
        learner_id=learner_id,
        chapter=request.chapter,
        subject=request.subject,
        tutor_score=tutor_score,
        learner_score=learner_score,
        compatibility_score=compatibility,
        status=MatchStatus.PENDING,
    )
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    return {
        "message": "Connection request sent",
        "match_id": match.id,
        "compatibility_score": compatibility,
        "you_are": "tutor" if tutor_id == current_user.id else "learner"
    }


# ===========================
# CHAT & COMMUNICATION ROUTES
# ===========================

@router.post("/chat/send", response_model=matching_schemas.ChatMessage)
def send_chat_message(
    message_data: matching_schemas.ChatMessageCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Send a chat message to matched peer"""
    from app.models.matching import ChatMessage
    
    # Verify match exists and user is part of it
    match = db.query(PeerMatch).filter(PeerMatch.id == message_data.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if current_user.id not in [match.tutor_id, match.learner_id]:
        raise HTTPException(status_code=403, detail="Not part of this match")
    
    # Verify receiver is the other person in the match
    if message_data.receiver_id not in [match.tutor_id, match.learner_id]:
        raise HTTPException(status_code=400, detail="Invalid receiver")
    
    if message_data.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    
    # Create message
    message = ChatMessage(
        match_id=message_data.match_id,
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        message=message_data.message,
        message_type=message_data.message_type,
        file_url=message_data.file_url,
        file_name=message_data.file_name,
        file_size=message_data.file_size,
        file_type=message_data.file_type,
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Add sender/receiver names
    sender = db.query(User).filter(User.id == current_user.id).first()
    receiver = db.query(User).filter(User.id == message_data.receiver_id).first()
    
    message.sender_name = sender.name if sender else None
    message.receiver_name = receiver.name if receiver else None
    
    return message


@router.get("/chat/{match_id}", response_model=List[matching_schemas.ChatMessage])
def get_chat_history(
    match_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get chat history for a match"""
    from app.models.matching import ChatMessage
    
    # Verify match exists and user is part of it
    match = db.query(PeerMatch).filter(PeerMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if current_user.id not in [match.tutor_id, match.learner_id]:
        raise HTTPException(status_code=403, detail="Not part of this match")
    
    # Get messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.match_id == match_id
    ).order_by(ChatMessage.created_at).all()
    
    # Add sender/receiver names
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        receiver = db.query(User).filter(User.id == msg.receiver_id).first()
        msg.sender_name = sender.name if sender else None
        msg.receiver_name = receiver.name if receiver else None
    
    return messages


@router.patch("/chat/{message_id}/read")
def mark_message_read(
    message_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Mark a message as read"""
    from app.models.matching import ChatMessage
    from datetime import datetime
    
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the receiver of this message")
    
    message.is_read = True
    message.read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Marked as read"}


# ===========================
# SESSION & VIDEO CALL ROUTES
# ===========================

@router.post("/session/create", response_model=matching_schemas.Session)
def create_session(
    session_data: matching_schemas.SessionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Create a tutoring session (text, video call, or in-person)"""
    from app.models.matching import TutoringSession
    import secrets
    import string
    
    # Verify match exists and user is part of it
    match = db.query(PeerMatch).filter(PeerMatch.id == session_data.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if current_user.id not in [match.tutor_id, match.learner_id]:
        raise HTTPException(status_code=403, detail="Not part of this match")
    
    # Generate Google Meet link for video calls
    meeting_link = None
    if session_data.communication_method == "video_call":
        # Generate a unique meeting code
        meeting_code = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        meeting_link = f"https://meet.google.com/{meeting_code}"
    
    # Create session
    session = TutoringSession(
        match_id=session_data.match_id,
        communication_method=session_data.communication_method,
        scheduled_at=session_data.scheduled_at,
        meeting_link=meeting_link,
        meeting_location=session_data.meeting_location,
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.patch("/session/{session_id}", response_model=matching_schemas.Session)
def update_session(
    session_id: int,
    update_data: matching_schemas.SessionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update session details (start/end time, notes, topics)"""
    from app.models.matching import TutoringSession
    
    session = db.query(TutoringSession).filter(TutoringSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify user is part of the match
    match = db.query(PeerMatch).filter(PeerMatch.id == session.match_id).first()
    if current_user.id not in [match.tutor_id, match.learner_id]:
        raise HTTPException(status_code=403, detail="Not part of this session")
    
    # Update fields
    if update_data.meeting_link is not None:
        session.meeting_link = update_data.meeting_link
    if update_data.topics_covered is not None:
        session.topics_covered = update_data.topics_covered
    if update_data.notes is not None:
        session.notes = update_data.notes
    if update_data.started_at is not None:
        session.started_at = update_data.started_at
    if update_data.ended_at is not None:
        session.ended_at = update_data.ended_at
        # Calculate duration
        if session.started_at:
            duration = (update_data.ended_at - session.started_at).total_seconds() / 60
            session.duration_minutes = int(duration)
    
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/session/{match_id}/list", response_model=List[matching_schemas.Session])
def get_sessions(
    match_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get all sessions for a match"""
    from app.models.matching import TutoringSession
    
    # Verify match exists and user is part of it
    match = db.query(PeerMatch).filter(PeerMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if current_user.id not in [match.tutor_id, match.learner_id]:
        raise HTTPException(status_code=403, detail="Not part of this match")
    
    sessions = db.query(TutoringSession).filter(
        TutoringSession.match_id == match_id
    ).order_by(TutoringSession.scheduled_at.desc()).all()
    
    return sessions


# ===========================
# FILE & RESOURCE SHARING ROUTES
# ===========================

@router.post("/resource/share", response_model=matching_schemas.SharedResource)
def share_resource(
    resource_data: matching_schemas.SharedResourceCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Share a file or resource with matched peer"""
    from app.models.matching import SharedResource
    
    # Verify match exists and user is part of it
    match = db.query(PeerMatch).filter(PeerMatch.id == resource_data.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if current_user.id not in [match.tutor_id, match.learner_id]:
        raise HTTPException(status_code=403, detail="Not part of this match")
    
    # Create resource
    resource = SharedResource(
        match_id=resource_data.match_id,
        uploader_id=current_user.id,
        title=resource_data.title,
        description=resource_data.description,
        resource_type=resource_data.resource_type,
        file_url=resource_data.file_url,
        file_name=resource_data.file_name,
        file_size=resource_data.file_size,
        external_link=resource_data.external_link,
        subject=resource_data.subject,
        chapter=resource_data.chapter,
        tags=resource_data.tags,
    )
    
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    # Add uploader name
    uploader = db.query(User).filter(User.id == current_user.id).first()
    resource.uploader_name = uploader.name if uploader else None
    
    return resource


@router.get("/resource/{match_id}/list", response_model=List[matching_schemas.SharedResource])
def get_shared_resources(
    match_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get all shared resources for a match"""
    from app.models.matching import SharedResource
    
    # Verify match exists and user is part of it
    match = db.query(PeerMatch).filter(PeerMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if current_user.id not in [match.tutor_id, match.learner_id]:
        raise HTTPException(status_code=403, detail="Not part of this match")
    
    resources = db.query(SharedResource).filter(
        SharedResource.match_id == match_id
    ).order_by(SharedResource.created_at.desc()).all()
    
    # Add uploader names
    for res in resources:
        uploader = db.query(User).filter(User.id == res.uploader_id).first()
        res.uploader_name = uploader.name if uploader else None
    
    return resources
