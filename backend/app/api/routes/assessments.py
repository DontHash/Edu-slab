"""
Assessment routes for managing tests and questions
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.assessment import Assessment, Question, StudentResponse, AssessmentStatus
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    QuestionCreate,
    QuestionResponse,
    QuestionPublic,
    StudentResponseCreate,
    StudentResponseResponse
)

router = APIRouter()


# Assessment endpoints
@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment_data: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new assessment"""
    assessment = Assessment(
        student_id=assessment_data.student_id,
        title=assessment_data.title,
        subject=assessment_data.subject,
        total_questions=assessment_data.total_questions
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    return assessment


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get assessment by ID"""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Check permissions
    if current_user.role == "student" and assessment.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return assessment


@router.get("/student/{student_id}", response_model=List[AssessmentResponse])
def get_student_assessments(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all assessments for a student"""
    # Check permissions
    if current_user.role == "student" and student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    assessments = db.query(Assessment).filter(Assessment.student_id == student_id).all()
    return assessments


# Question endpoints
@router.post("/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new question (teacher/admin only)"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    question = Question(**question_data.dict())
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return question


@router.get("/questions/{question_id}", response_model=QuestionPublic)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get question by ID (without correct answer for students)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question


@router.get("/questions/", response_model=List[QuestionPublic])
def get_questions(
    subject: str = None,
    grade_level: int = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get questions with filters"""
    query = db.query(Question).filter(Question.is_active == True)
    
    if subject:
        query = query.filter(Question.subject == subject)
    if grade_level:
        query = query.filter(Question.grade_level == grade_level)
    
    questions = query.offset(skip).limit(limit).all()
    return questions


# Student response endpoints
@router.post("/responses", response_model=StudentResponseResponse, status_code=status.HTTP_201_CREATED)
def submit_response(
    response_data: StudentResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit a student's answer to a question"""
    # Get the question to check correct answer
    question = db.query(Question).filter(Question.id == response_data.question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if answer is correct
    is_correct = response_data.student_answer.strip().lower() == question.correct_answer.strip().lower()
    
    # Create response
    response = StudentResponse(
        student_id=current_user.id,
        assessment_id=response_data.assessment_id,
        question_id=response_data.question_id,
        student_answer=response_data.student_answer,
        is_correct=is_correct
    )
    
    db.add(response)
    
    # Update assessment
    assessment = db.query(Assessment).filter(Assessment.id == response_data.assessment_id).first()
    if assessment:
        if is_correct:
            assessment.correct_answers += 1
        
        # Check if assessment is complete
        total_responses = db.query(StudentResponse).filter(
            StudentResponse.assessment_id == response_data.assessment_id
        ).count()
        
        if total_responses >= assessment.total_questions - 1:  # -1 because we're adding one now
            assessment.status = AssessmentStatus.COMPLETED
            assessment.score = (assessment.correct_answers / assessment.total_questions) * 100
    
    db.commit()
    db.refresh(response)
    
    return response
