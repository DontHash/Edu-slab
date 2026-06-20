"""
API routes for RAG-based question generation
"""
import json
from pathlib import Path
from typing import List, Optional

from app.api.routes.auth import get_current_user
from app.core.config import settings
from app.db.database import get_db
from app.models.assessment import Assessment
from app.models.user import User
from app.services.evaluation_service import get_evaluation_service
from app.services.rag_service import RAGService
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()

# Initialize RAG service
RAG_DATA_FOLDER = Path(__file__).parent.parent.parent.parent / "python_RAG" / "data"
MISTRAL_API_KEY = settings.MISTRAL_API_KEY if hasattr(settings, 'MISTRAL_API_KEY') else None

rag_service = None

def get_rag_service():
    """Get or initialize RAG service"""
    global rag_service
    
    if rag_service is None:
        if not MISTRAL_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service not configured. MISTRAL_API_KEY is missing."
            )
        
        try:
            rag_service = RAGService(api_key=MISTRAL_API_KEY, data_folder=str(RAG_DATA_FOLDER))
            print("RAG service initialized successfully")
        except Exception as e:
            print(f"Error initializing RAG service: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to initialize RAG service: {str(e)}"
            )
    
    return rag_service


# Request/Response Models
class QuestionGenerationRequest(BaseModel):
    chapter: Optional[str] = None
    subject: str
    num_questions: int = 5


class GeneratedQuestion(BaseModel):
    id: str
    question: str
    chapter: str
    subject: str
    type: str
    order: int


class QuestionGenerationResponse(BaseModel):
    questions: List[GeneratedQuestion]
    chapter: str
    subject: str
    total_generated: int


class AnswerSubmission(BaseModel):
    question_id: str
    answer: str
    chapter: Optional[str] = None
    question: Optional[str] = None


class AssessmentSubmission(BaseModel):
    chapter: str
    subject: str
    answers: List[AnswerSubmission]


class AssessmentResponse(BaseModel):
    assessment_id: str
    chapter: str
    subject: str
    total_questions: int
    submitted_at: str
    status: str


class EvaluationResponse(BaseModel):
    assessment_id: str
    chapter_analysis: dict
    question_analysis: dict
    overall_analysis: dict
    evaluation_completed_at: str
    submitted_at: str
    status: str


@router.post("/generate-questions", response_model=QuestionGenerationResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate questions by subject (5 questions from each chapter)
    """
    try:
        service = get_rag_service()
        
        # If chapter is provided, generate for that chapter only (backward compatibility)
        if request.chapter:
            questions = service.generate_questions_from_chapter(
                chapter_name=request.chapter,
                subject=request.subject,
                num_questions=request.num_questions
            )
            chapter_name = request.chapter
        else:
            # Generate questions from all chapters in the subject
            questions = service.generate_questions_by_subject(
                subject=request.subject,
                questions_per_chapter=1
            )
            chapter_name = "All Chapters"
        
        return QuestionGenerationResponse(
            questions=[GeneratedQuestion(**q) for q in questions],
            chapter=chapter_name,
            subject=request.subject or questions[0].get("subject", "general") if questions else "general",
            total_generated=len(questions)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions: {str(e)}"
        )


@router.get("/available-chapters")
async def get_available_chapters(
    subject: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available subjects and example chapters
    Since we're using AI to generate questions, we return common educational chapters
    """
    
    # Common chapters by subject for Class 10
    all_chapters = {
        "maths": [
            "Real Numbers",
            "Polynomials",
            "Linear Equations",
            "Quadratic Equations",
            "Arithmetic Progressions",
            "Triangles",
            "Coordinate Geometry",
            "Trigonometry",
            "Circles",
            "Statistics",
            "Probability"
        ],
        "science": [
            "Chemical Reactions",
            "Acids Bases and Salts",
            "Metals and Non-metals",
            "Carbon Compounds",
            "Periodic Classification",
            "Life Processes",
            "Control and Coordination",
            "Reproduction",
            "Heredity and Evolution",
            "Light Reflection and Refraction",
            "Human Eye",
            "Electricity",
            "Magnetic Effects of Current"
        ],
        "english": [
            "Reading Comprehension",
            "Grammar",
            "Writing Skills",
            "Literature",
            "Poetry Analysis",
            "Essay Writing",
            "Letter Writing"
        ]
    }
    
    if subject:
        subject_lower = subject.lower()
        if subject_lower in all_chapters:
            return {
                "subject": subject_lower,
                "chapters": [{"name": ch, "available": True} for ch in all_chapters[subject_lower]]
            }
        else:
            return {"subject": subject_lower, "chapters": []}
    
    # Return all subjects and their chapters
    return {
        "subjects": {
            subj: [{"name": ch, "available": True} for ch in chapters]
            for subj, chapters in all_chapters.items()
        }
    }


@router.post("/submit-assessment", response_model=AssessmentResponse)
async def submit_assessment(
    submission: AssessmentSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit answers for an assessment and automatically trigger evaluation
    Stores the answers in JSON format and immediately evaluates them
    """
    import uuid
    from datetime import datetime
    
    try:
        # Create assessment record
        assessment_data = {
            "assessment_id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "user_name": current_user.name,
            "user_email": current_user.email,
            "chapter": submission.chapter,
            "subject": submission.subject,
            "answers": [
                {
                    "question_id": ans.question_id,
                    "answer": ans.answer,
                    "chapter": ans.chapter,
                    "question": ans.question
                }
                for ans in submission.answers
            ],
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "evaluating"
        }
        
        # Create file-based storage
        assessments_dir = Path(__file__).parent.parent.parent.parent / "assessments"
        assessments_dir.mkdir(exist_ok=True)
        
        assessment_id = assessment_data["assessment_id"]
        user_dir = assessments_dir / str(current_user.id)
        user_dir.mkdir(exist_ok=True)
        
        assessment_file = user_dir / f"{assessment_id}.json"
        
        # Save assessment
        with open(assessment_file, "w", encoding="utf-8") as f:
            json.dump(assessment_data, f, indent=2)
        
        # Automatically trigger evaluation
        try:
            evaluation_service = get_evaluation_service()
            evaluation_result = evaluation_service.evaluate_assessment(assessment_file)
            
            # Add timestamp
            evaluation_result["evaluated_at"] = datetime.utcnow().isoformat()
            
            # Save evaluation
            evaluation_file = user_dir / f"{assessment_id}_evaluation.json"
            with open(evaluation_file, "w", encoding="utf-8") as f:
                json.dump(evaluation_result, f, indent=2)
            
            # Update user's subject levels and fit_to_teach_level in database
            overall_analysis = evaluation_result.get("overall_analysis", {})
            final_score = overall_analysis.get("final_score_out_of_100", 0)
            # Convert to integer to match schema
            final_score = int(round(final_score))
            
            subject = assessment_data.get("subject", "").lower()
            
            # Update subject-specific level
            if subject == "maths" or subject == "math":
                current_user.math_level = int(final_score)
            elif subject == "science":
                current_user.science_level = int(final_score)
            elif subject == "english":
                current_user.english_level = int(final_score)
            
            # Calculate fit_to_teach_level based on BEST score across all subjects
            best_score = max(
                current_user.math_level or 0,
                current_user.science_level or 0,
                current_user.english_level or 0
            )
            
            if best_score >= 85:
                fit_to_teach = max(1, (current_user.current_level or 10) - 2)
            elif best_score >= 70:
                fit_to_teach = max(1, (current_user.current_level or 10) - 3)
            elif best_score >= 50:
                fit_to_teach = max(1, (current_user.current_level or 10) - 4)
            else:
                fit_to_teach = None
            
            current_user.fit_to_teach_level = fit_to_teach
            
            # Commit changes to database
            db.commit()
            db.refresh(current_user)
            
            # Sync topic performance for reports and learning guides
            try:
                from app.services.topic_performance_service import sync_topic_performances
                count = sync_topic_performances(db, current_user.id)
                print(f"[DEBUG] Synced {count} topic performance records for user {current_user.id}")
            except Exception as e:
                import traceback
                print(f"[ERROR] Failed to sync topic performance: {e}")
                print(traceback.format_exc())
            
            # Update assessment status
            assessment_data["status"] = "evaluated"
            with open(assessment_file, "w", encoding="utf-8") as f:
                json.dump(assessment_data, f, indent=2)
            
        except Exception as eval_error:
            print(f"Evaluation error (non-blocking): {eval_error}")
            # Don't fail the submission if evaluation fails
            assessment_data["status"] = "evaluation_failed"
            with open(assessment_file, "w", encoding="utf-8") as f:
                json.dump(assessment_data, f, indent=2)
        
        return AssessmentResponse(
            assessment_id=assessment_id,
            chapter=submission.chapter,
            subject=submission.subject,
            total_questions=len(submission.answers),
            submitted_at=assessment_data["submitted_at"],
            status=assessment_data["status"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit assessment: {str(e)}"
        )


@router.get("/user-assessments")
async def get_user_assessments(
    current_user: User = Depends(get_current_user)
):
    """
    Get all assessments submitted by the current user
    """
    try:
        assessments_dir = Path(__file__).parent.parent.parent.parent / "assessments"
        user_dir = assessments_dir / str(current_user.id)
        
        if not user_dir.exists():
            return {"assessments": []}
        
        assessments = []
        for assessment_file in user_dir.glob("*.json"):
            try:
                with open(assessment_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["assessment_id"] = assessment_file.stem
                    assessments.append(data)
            except Exception as e:
                print(f"Error loading assessment {assessment_file}: {e}")
        
        # Sort by submitted_at (most recent first)
        assessments.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        
        return {"assessments": assessments}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load assessments: {str(e)}"
        )


@router.get("/assessment/{assessment_id}")
async def get_assessment_details(
    assessment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific assessment
    """
    try:
        assessments_dir = Path(__file__).parent.parent.parent.parent / "assessments"
        user_dir = assessments_dir / str(current_user.id)
        assessment_file = user_dir / f"{assessment_id}.json"
        
        if not assessment_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        with open(assessment_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["assessment_id"] = assessment_id
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load assessment: {str(e)}"
        )


@router.get("/evaluate-assessment/{assessment_id}", response_model=EvaluationResponse)
async def get_evaluation(
    assessment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get evaluation results for a specific assessment
    """
    try:
        assessments_dir = Path(__file__).parent.parent.parent.parent / "assessments"
        user_dir = assessments_dir / str(current_user.id)
        evaluation_file = user_dir / f"{assessment_id}_evaluation.json"
        assessment_file = user_dir / f"{assessment_id}.json"
        
        if not evaluation_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        # Load evaluation data
        with open(evaluation_file, "r", encoding="utf-8") as f:
            evaluation_data = json.load(f)
        
        # Load assessment data for submitted_at and status
        with open(assessment_file, "r", encoding="utf-8") as f:
            assessment_data = json.load(f)
        
        return EvaluationResponse(
            assessment_id=assessment_id,
            chapter_analysis=evaluation_data.get("chapter_analysis", {}),
            question_analysis=evaluation_data.get("question_analysis", {}),
            overall_analysis=evaluation_data.get("overall_analysis", {}),
            evaluation_completed_at=evaluation_data.get("evaluated_at", ""),
            submitted_at=assessment_data.get("submitted_at", ""),
            status=assessment_data.get("status", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load evaluation: {str(e)}"
        )


@router.post("/evaluate-assessment/{assessment_id}", response_model=EvaluationResponse)
async def evaluate_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluate a submitted assessment using AI and update user levels
    """
    try:
        assessments_dir = Path(__file__).parent.parent.parent.parent / "assessments"
        user_dir = assessments_dir / str(current_user.id)
        assessment_file = user_dir / f"{assessment_id}.json"
        
        if not assessment_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        # Check if evaluation already exists
        evaluation_file = user_dir / f"{assessment_id}_evaluation.json"
        if evaluation_file.exists():
            # Return existing evaluation
            with open(evaluation_file, "r", encoding="utf-8") as f:
                evaluation_data = json.load(f)
            
            return EvaluationResponse(
                assessment_id=assessment_id,
                chapter_analysis=evaluation_data.get("chapter_analysis", {}),
                question_analysis=evaluation_data.get("question_analysis", {}),
                overall_analysis=evaluation_data.get("overall_analysis", {}),
                evaluation_completed_at=evaluation_data.get("evaluated_at", "")
            )
        
        # Perform evaluation
        evaluation_service = get_evaluation_service()
        evaluation_result = evaluation_service.evaluate_assessment(assessment_file)
        
        # Add timestamp
        from datetime import datetime
        evaluation_result["evaluated_at"] = datetime.utcnow().isoformat()
        
        # Save evaluation
        with open(evaluation_file, "w", encoding="utf-8") as f:
            json.dump(evaluation_result, f, indent=2)
        
        # Update user's subject levels and fit_to_teach_level in database
        overall_analysis = evaluation_result.get("overall_analysis", {})
        final_score = overall_analysis.get("final_score_out_of_100", 0)
        estimated_grade = overall_analysis.get("estimated_student_grade_level", current_user.current_level or 10)
        
        # Load assessment to get subject
        with open(assessment_file, "r", encoding="utf-8") as f:
            assessment_data = json.load(f)
        
        subject = assessment_data.get("subject", "").lower()
        
        # Convert to integer to match schema
        final_score = int(round(final_score))
        
        # Update subject-specific level
        if subject == "maths" or subject == "math":
            current_user.math_level = final_score
        elif subject == "science":
            current_user.science_level = final_score
        elif subject == "english":
            current_user.english_level = final_score
        
        # Calculate fit_to_teach_level based on BEST score across all subjects
        # If student scores 85%+, they can teach 2 grades below current
        # If 70-84%, they can teach 3 grades below
        # If 50-69%, they can teach 4 grades below
        # Below 50%, no teaching recommendation
        best_score = max(
            current_user.math_level or 0,
            current_user.science_level or 0,
            current_user.english_level or 0
        )
        
        if best_score >= 85:
            fit_to_teach = max(1, (current_user.current_level or 10) - 2)
        elif best_score >= 70:
            fit_to_teach = max(1, (current_user.current_level or 10) - 3)
        elif best_score >= 50:
            fit_to_teach = max(1, (current_user.current_level or 10) - 4)
        else:
            fit_to_teach = None
        
        current_user.fit_to_teach_level = fit_to_teach
        
        # Commit changes to database
        db.commit()
        db.refresh(current_user)

        
        
        # Sync topic performance for reports and learning guides
        try:
            from app.services.topic_performance_service import sync_topic_performances
            count = sync_topic_performances(db, current_user.id)
            print(f"[DEBUG] Synced {count} topic performance records for user {current_user.id}")
        except Exception as e:
            import traceback
            print(f"[ERROR] Failed to sync topic performance: {e}")
            print(traceback.format_exc())
        
        return EvaluationResponse(
            assessment_id=assessment_id,
            chapter_analysis=evaluation_result.get("chapter_analysis", {}),
            question_analysis=evaluation_result.get("question_analysis", {}),
            overall_analysis=evaluation_result.get("overall_analysis", {}),
            evaluation_completed_at=evaluation_result.get("evaluated_at", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Evaluation error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate assessment: {str(e)}"
        )


@router.get("/recent-activities")
async def get_recent_activities(
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """
    Get recent assessment activities for the current user
    """
    try:
        assessments_dir = Path(__file__).parent.parent.parent.parent / "assessments"
        user_dir = assessments_dir / str(current_user.id)
        
        if not user_dir.exists():
            return {"activities": []}
        
        activities = []
        
        # Get all assessment files (excluding evaluation files)
        assessment_files = [f for f in user_dir.glob("*.json") if not f.name.endswith("_evaluation.json")]
        
        for assessment_file in assessment_files:
            try:
                with open(assessment_file, "r", encoding="utf-8") as f:
                    assessment_data = json.load(f)
                
                assessment_id = assessment_file.stem
                evaluation_file = user_dir / f"{assessment_id}_evaluation.json"
                
                # Load evaluation if exists
                evaluation_data = None
                if evaluation_file.exists():
                    with open(evaluation_file, "r", encoding="utf-8") as ef:
                        evaluation_data = json.load(ef)
                
                activity = {
                    "id": assessment_id,
                    "type": "assessment",
                    "subject": assessment_data.get("subject", "Unknown"),
                    "chapter": assessment_data.get("chapter", "All Chapters"),
                    "status": assessment_data.get("status", "pending"),
                    "submitted_at": assessment_data.get("submitted_at", ""),
                    "total_questions": len(assessment_data.get("answers", [])),
                }
                
                # Add score if evaluation exists
                if evaluation_data and "overall_analysis" in evaluation_data:
                    activity["score"] = evaluation_data["overall_analysis"].get("final_score_out_of_100", None)
                
                activities.append(activity)
                
            except Exception as e:
                print(f"Error loading activity from {assessment_file}: {e}")
        
        # Sort by submitted_at (most recent first)
        activities.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        
        # Return limited results
        return {"activities": activities[:limit]}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load activities: {str(e)}"
        )


@router.get("/subject-progress/{subject}")
async def get_subject_progress(
    subject: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed progress analysis for a specific subject including strengths and weaknesses
    """
    try:
        assessments_dir = Path(__file__).parent.parent.parent.parent / "assessments"
        user_dir = assessments_dir / str(current_user.id)
        
        if not user_dir.exists():
            return {
                "subject": subject,
                "has_data": False,
                "message": "No assessments found for this subject"
            }
        
        # Find the most recent assessment for this subject
        latest_assessment = None
        latest_evaluation = None
        latest_timestamp = ""
        
        assessment_files = [f for f in user_dir.glob("*.json") if not f.name.endswith("_evaluation.json")]
        
        for assessment_file in assessment_files:
            try:
                with open(assessment_file, "r", encoding="utf-8") as f:
                    assessment_data = json.load(f)
                
                # SECURITY: Verify this assessment belongs to current user
                assessment_user_email = assessment_data.get("user_email") or assessment_data.get("email")
                if assessment_user_email and assessment_user_email != current_user.email:
                    print(f"Warning: Assessment {assessment_file} belongs to {assessment_user_email}, not {current_user.email}")
                    continue  # Skip assessments from other users
                
                if assessment_data.get("subject", "").lower() == subject.lower():
                    submitted_at = assessment_data.get("submitted_at", "")
                    if submitted_at > latest_timestamp:
                        latest_timestamp = submitted_at
                        latest_assessment = assessment_data
                        
                        # Load corresponding evaluation
                        assessment_id = assessment_file.stem
                        evaluation_file = user_dir / f"{assessment_id}_evaluation.json"
                        if evaluation_file.exists():
                            with open(evaluation_file, "r", encoding="utf-8") as ef:
                                latest_evaluation = json.load(ef)
            except Exception as e:
                print(f"Error processing assessment file {assessment_file}: {e}")
        
        if not latest_assessment or not latest_evaluation:
            return {
                "subject": subject,
                "has_data": False,
                "message": "No evaluated assessments found for this subject"
            }
        
        # Extract chapter analysis
        chapter_analysis = latest_evaluation.get("chapter_analysis", {})
        overall_analysis = latest_evaluation.get("overall_analysis", {})
        
        # Categorize chapters by strength
        strengths = []  # none weakness (>=85%)
        areas_to_improve = []  # mild (70-84%) and moderate (50-69%)
        critical_weaknesses = []  # severe (<50%)
        
        for chapter_name, chapter_data in chapter_analysis.items():
            weakness_level = chapter_data.get("weakness_level", "moderate")
            accuracy = chapter_data.get("accuracy_percentage", 0)
            
            chapter_info = {
                "chapter": chapter_name,
                "accuracy": accuracy,
                "weakness_level": weakness_level,
                "score": chapter_data.get("chapter_score_out_of_10", 0)
            }
            
            if weakness_level == "none":
                strengths.append(chapter_info)
            elif weakness_level in ["mild", "moderate"]:
                areas_to_improve.append(chapter_info)
            elif weakness_level == "severe":
                critical_weaknesses.append(chapter_info)
        
        # Sort each category by accuracy (descending for strengths, ascending for weaknesses)
        strengths.sort(key=lambda x: x["accuracy"], reverse=True)
        areas_to_improve.sort(key=lambda x: x["accuracy"])
        critical_weaknesses.sort(key=lambda x: x["accuracy"])
        
        return {
            "subject": subject,
            "has_data": True,
            "overall_score": overall_analysis.get("final_score_out_of_100", 0),
            "estimated_grade_level": overall_analysis.get("estimated_student_grade_level", None),
            "assessed_at": latest_timestamp,
            "strengths": strengths,
            "areas_to_improve": areas_to_improve,
            "critical_weaknesses": critical_weaknesses,
            "learning_gaps": overall_analysis.get("learning_gap_summary", []),
            "strongest_chapters": overall_analysis.get("strongest_chapters", []),
            "weakest_chapters": overall_analysis.get("weakest_chapters", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load subject progress: {str(e)}"
        )


@router.get("/all-subjects-progress")
async def get_all_subjects_progress(
    current_user: User = Depends(get_current_user)
):
    """
    Get progress summary for all subjects
    """
    try:
        subjects = ["maths", "science", "english"]
        progress_data = {}
        
        for subject in subjects:
            # Reuse the subject progress endpoint logic
            result = await get_subject_progress(subject, current_user)
            progress_data[subject] = result
        
        return {"subjects_progress": progress_data}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load all subjects progress: {str(e)}"
        )
