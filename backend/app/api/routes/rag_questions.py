"""
API routes for RAG-based question generation
"""
import json
from pathlib import Path
from typing import List, Optional

from app.api.routes.auth import get_current_user
from app.core.config import settings
from app.core.curriculum import (
    CURRICULUM_FRAMEWORK,
    ROADMAP_HOURS_BY_WEAKNESS,
    ROADMAP_STEP_MINUTES_BY_WEAKNESS,
    normalize_subject_key,
)
from app.core.paths import ASSESSMENTS_DIR
from app.db.database import get_db
from app.models.assessment import Assessment
from app.models.user import User
from app.services.adaptive_assessment_service import get_adaptive_service
from app.services.evaluation_service import evaluate_assessment_file
from app.services.question_bank_service import get_question_bank
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()

# Nepal CDC curriculum knowledge base (local files — no API key)
CURRICULUM_DATA = Path(__file__).parent.parent.parent.parent.parent / "python_RAG" / "data"


# Request/Response Models
class QuestionGenerationRequest(BaseModel):
    chapter: Optional[str] = None
    subject: str
    num_questions: int = 1
    grade: Optional[int] = None


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
    question_raw: Optional[str] = None
    expected_answer: Optional[str] = None
    answer_type: Optional[str] = None


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


class AdaptiveStartRequest(BaseModel):
    subject: str
    grade: Optional[int] = None


class AdaptiveAnswerRequest(BaseModel):
    question_id: str
    answer: str


class AdaptiveQuestionPublic(BaseModel):
    id: str
    question: str
    chapter: str
    difficulty: str
    type: str
    domain: Optional[str] = None
    section: Optional[str] = None
    context_text: Optional[str] = None
    item_type: Optional[str] = None
    cognitive_level: Optional[str] = None


class AdaptiveStartResponse(BaseModel):
    session_id: str
    question_number: int
    total_questions: int
    difficulty: str
    grade: int
    question: AdaptiveQuestionPublic
    progress_percent: int
    blueprint_mode: Optional[bool] = None


class AdaptiveAnswerResponse(BaseModel):
    session_id: str
    completed: bool
    question_number: int
    total_questions: int
    progress_percent: int
    last_result: Optional[dict] = None
    question: Optional[AdaptiveQuestionPublic] = None
    difficulty: Optional[str] = None
    message: Optional[str] = None


class EvaluationResponse(BaseModel):
    assessment_id: str
    chapter_analysis: dict
    question_analysis: dict
    overall_analysis: dict
    recommended_resources: Optional[list] = None
    evaluation_completed_at: str
    submitted_at: str
    status: str
    answers: Optional[list] = None


def _build_evaluation_response(
    assessment_id: str,
    evaluation_data: dict,
    assessment_data: dict,
) -> EvaluationResponse:
    """Ensure study resources are attached (backfill for older evaluations)."""
    from app.services.learning_resource_service import attach_study_resources

    if not evaluation_data.get("recommended_resources"):
        subject = assessment_data.get("subject", "")
        grade = int(assessment_data.get("grade") or 10)
        attach_study_resources(
            evaluation_data,
            subject=subject,
            grade=grade,
            answers=assessment_data.get("answers"),
        )

    return EvaluationResponse(
        assessment_id=assessment_id,
        chapter_analysis=evaluation_data.get("chapter_analysis", {}),
        question_analysis=evaluation_data.get("question_analysis", {}),
        overall_analysis=evaluation_data.get("overall_analysis", {}),
        recommended_resources=evaluation_data.get("recommended_resources", []),
        evaluation_completed_at=evaluation_data.get("evaluated_at", ""),
        submitted_at=assessment_data.get("submitted_at", ""),
        status=assessment_data.get("status", ""),
        answers=assessment_data.get("answers", []),
    )


def _find_latest_subject_evaluation(user_id: int, subject: str) -> tuple[dict | None, dict | None, str | None]:
    """Return (assessment_data, evaluation_data, assessment_id) for latest evaluated subject."""
    assessments_dir = ASSESSMENTS_DIR
    user_dir = assessments_dir / str(user_id)
    if not user_dir.exists():
        return None, None, None

    subject_key = normalize_subject_key(subject)
    latest_assessment = None
    latest_evaluation = None
    latest_id = None
    latest_timestamp = ""

    for assessment_file in user_dir.glob("*.json"):
        if assessment_file.name.endswith("_evaluation.json"):
            continue
        try:
            with open(assessment_file, encoding="utf-8") as f:
                assessment_data = json.load(f)
            if normalize_subject_key(assessment_data.get("subject", "")) != subject_key:
                continue
            submitted_at = assessment_data.get("submitted_at", "")
            if submitted_at <= latest_timestamp:
                continue
            evaluation_file = user_dir / f"{assessment_file.stem}_evaluation.json"
            if not evaluation_file.exists():
                continue
            with open(evaluation_file, encoding="utf-8") as ef:
                evaluation_data = json.load(ef)
            latest_timestamp = submitted_at
            latest_assessment = assessment_data
            latest_evaluation = evaluation_data
            latest_id = assessment_file.stem
        except Exception as exc:
            print(f"Error loading assessment {assessment_file}: {exc}")

    return latest_assessment, latest_evaluation, latest_id


def _apply_evaluation_to_user(user: User, subject: str, evaluation_result: dict) -> None:
    """Persist proficiency score and estimated grade after evaluation."""
    overall = evaluation_result.get("overall_analysis", {})
    final_score = int(round(overall.get("final_score_out_of_100", 0)))
    estimated_grade = int(overall.get("estimated_student_grade_level") or user.current_level or 10)
    subject_key = (subject or "").lower()

    if subject_key in ("maths", "math"):
        user.math_level = final_score
    elif subject_key == "science":
        user.science_level = final_score
    elif subject_key == "english":
        user.english_level = final_score
        user.writing_english_level = final_score

    user.current_level = estimated_grade


def _roadmap_from_evaluation(
    subject: str,
    assessment_data: dict,
    evaluation_data: dict,
    assessment_id: str,
) -> dict:
    """Shape evaluation study plan for the Roadmap UI."""
    from app.services.learning_resource_service import attach_study_resources

    if not evaluation_data.get("recommended_resources"):
        grade = int(assessment_data.get("grade") or 10)
        attach_study_resources(evaluation_data, subject=subject, grade=grade)

    overall = evaluation_data.get("overall_analysis", {})
    study_plan = overall.get("study_plan", {})
    weak_topics = study_plan.get("weak_topics", [])

    chapters = []
    for topic in weak_topics:
        weakness = topic.get("weakness_level", "moderate")
        step_mins = ROADMAP_STEP_MINUTES_BY_WEAKNESS.get(weakness, 20)
        hours = topic.get("estimated_time_hours") or ROADMAP_HOURS_BY_WEAKNESS.get(weakness, 2.0)
        chapters.append({
            "chapter_name": topic.get("chapter", "Topic"),
            "weakness_level": weakness,
            "accuracy_percentage": topic.get("accuracy_percentage", 0),
            "priority": {1: 5, 2: 4, 3: 3}.get(topic.get("priority", 3), 3),
            "estimated_time_hours": hours,
            "roadmap_steps": [
                {
                    "step_number": i + 1,
                    "objective": step,
                    "estimated_time_minutes": step_mins,
                }
                for i, step in enumerate(topic.get("study_steps") or [])
            ],
            "resources": [
                {
                    "title": r.get("title", "Tutorial"),
                    "url": r.get("url", ""),
                    "type": r.get("type", "tutorial"),
                    "description": r.get("description", ""),
                    "level": r.get("provider_label", r.get("provider", "")),
                    "estimated_time_minutes": r.get("estimated_time_minutes", 15),
                }
                for r in (topic.get("recommended_resources") or [])
            ],
        })

    all_resources = study_plan.get("all_resources") or evaluation_data.get("recommended_resources", [])

    return {
        "has_data": True,
        "subject": subject,
        "assessment_id": assessment_id,
        "assessed_at": assessment_data.get("submitted_at", ""),
        "overall_score": overall.get("final_score_out_of_100", 0),
        "estimated_grade_level": overall.get("estimated_student_grade_level"),
        "proficiency_band": overall.get("proficiency_band"),
        "proficiency_label": overall.get("proficiency_label"),
        "domain_analysis": overall.get("domain_analysis", {}),
        "evaluation_method": overall.get("evaluation_method"),
        "learning_gaps": overall.get("learning_gap_summary", []),
        "study_plan_message": study_plan.get("message", ""),
        "all_resources": all_resources,
        "content": {
            "chapters": chapters,
            "global_recommendations": {
                "weekly_study_hours": max(4, int(sum(c["estimated_time_hours"] for c in chapters) * 0.75)),
                "minimum_duration_weeks": max(3, len(chapters)),
                "notes": study_plan.get("message") or (
                    f"Based on your latest {subject} diagnostic — "
                    "use the free tutorials below for each weak topic."
                ),
            },
        },
    }


@router.post("/generate-questions", response_model=QuestionGenerationResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Load standardized questions from the Nepal CDC curriculum knowledge base (local JSON).
    No cloud API required.
    """
    try:
        bank = get_question_bank()
        grade = request.grade or current_user.current_level or 10
        grade = max(6, min(10, int(grade)))

        questions = bank.pick_questions(
            subject=request.subject,
            grade=grade,
            chapter=request.chapter,
            questions_per_chapter=request.num_questions or 1,
        )

        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"No curriculum questions found for subject '{request.subject}' "
                    f"grade {grade}. Check python_RAG/data files."
                ),
            )

        chapter_name = request.chapter or "All Chapters (Nepal CDC)"

        return QuestionGenerationResponse(
            questions=[GeneratedQuestion(**q) for q in questions],
            chapter=chapter_name,
            subject=request.subject,
            total_generated=len(questions),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions: {str(e)}"
        )


@router.get("/evaluation-status")
async def evaluation_status(current_user: User = Depends(get_current_user)):
    """Check which evaluation engine is active (Ollama AI vs fallbacks)."""
    from app.services.ollama_client import OllamaClient

    client = OllamaClient()
    ollama_up = client.is_available()
    models = client.list_models() if ollama_up else []

    return {
        "primary_provider": settings.EVALUATION_PROVIDER,
        "ollama": {
            "available": ollama_up,
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL,
            "models_installed": models,
            "model_ready": client.is_model_ready(),
            "readiness": client.readiness_message(),
        },
        "mistral_enabled": settings.USE_MISTRAL_EVALUATION,
        "framework": CURRICULUM_FRAMEWORK,
        "message": (
            "Professional AI evaluation ready (Ollama)."
            if client.is_model_ready()
            else client.readiness_message()
        ),
    }


@router.get("/curriculum")
async def get_curriculum(
    grade: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """Nepal CDC curriculum metadata and available chapters for a grade."""
    bank = get_question_bank()
    g = grade or current_user.current_level or 10
    g = max(6, min(10, int(g)))
    return bank.get_curriculum_info(g)


@router.get("/curriculum-metadata/{grade}")
async def get_curriculum_metadata_route(
    grade: int,
    current_user: User = Depends(get_current_user),
):
    """CDC-aligned domains, learning outcomes, and spec grids for a grade."""
    from app.services.curriculum_metadata_service import get_curriculum_metadata

    g = max(6, min(10, int(grade)))
    meta = get_curriculum_metadata()
    return {
        "framework": CURRICULUM_FRAMEWORK,
        **meta.curriculum_summary(g),
    }


@router.get("/question-templates/{subject}")
async def list_question_templates(
    subject: str,
    grade: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """List generative question templates for English/Math (parameter-slot blueprints)."""
    from app.services.dynamic_question_service import get_dynamic_question_service

    g = grade or current_user.current_level or 10
    g = max(6, min(10, int(g)))
    svc = get_dynamic_question_service()
    return {
        "subject": subject,
        "grade": g,
        "templates": svc.list_templates(subject, g),
        "dynamic_enabled": True,
    }


@router.get("/question-templates/{subject}/preview")
async def preview_generated_questions(
    subject: str,
    grade: Optional[int] = None,
    count: int = 5,
    current_user: User = Depends(get_current_user),
):
    """Preview dynamically generated questions from templates (for authoring / QA)."""
    from app.services.dynamic_question_service import get_dynamic_question_service

    g = grade or current_user.current_level or 10
    g = max(6, min(10, int(g)))
    count = max(1, min(20, count))
    svc = get_dynamic_question_service()
    samples = svc.generate_pool(subject, g, variants_per_template=1)[:count]
    return {
        "subject": subject,
        "grade": g,
        "count": len(samples),
        "samples": [
            {
                "stem": s.get("stem"),
                "expected_answer": s.get("expected_answer"),
                "template_id": s.get("template_id"),
                "template_kind": s.get("template_kind"),
                "generated_params": s.get("generated_params"),
                "domain": s.get("domain"),
            }
            for s in samples
        ],
    }


@router.get("/available-chapters")
async def get_available_chapters(
    subject: Optional[str] = None,
    grade: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """Chapters from the local Nepal CDC knowledge base."""
    bank = get_question_bank()
    g = grade or current_user.current_level or 10
    g = max(6, min(10, int(g)))

    if subject:
        subject_key = subject.lower()
        chapters = bank.load_chapters(subject_key, g)
        return {
            "framework": "Nepal CDC National Curriculum",
            "grade": g,
            "subject": subject_key,
            "chapters": [{"name": c["chapter"], "available": True} for c in chapters],
        }

    return bank.get_curriculum_info(g)


@router.post("/adaptive/start", response_model=AdaptiveStartResponse)
async def start_adaptive_assessment(
    request: AdaptiveStartRequest,
    current_user: User = Depends(get_current_user),
):
    """Start a 10-question adaptive session — one contextual question at a time."""
    try:
        svc = get_adaptive_service()
        grade = request.grade or current_user.current_level or 10
        grade = max(6, min(10, int(grade)))
        result = svc.start_session(current_user.id, request.subject, grade)
        return AdaptiveStartResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start adaptive assessment: {str(e)}",
        )


@router.post("/adaptive/{session_id}/answer", response_model=AdaptiveAnswerResponse)
async def submit_adaptive_answer(
    session_id: str,
    body: AdaptiveAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """Submit one answer; difficulty adjusts before the next question."""
    try:
        svc = get_adaptive_service()
        result = svc.submit_answer(
            current_user.id, session_id, body.question_id, body.answer
        )
        return AdaptiveAnswerResponse(**result)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}",
        )


@router.post("/adaptive/{session_id}/finish", response_model=AssessmentResponse)
async def finish_adaptive_assessment(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Finalize adaptive session and run full AI evaluation."""
    import uuid
    from datetime import datetime

    try:
        svc = get_adaptive_service()
        finalized = svc.finalize_session(current_user.id, session_id)
        assessment_file = Path(finalized["assessment_file"])

        assessment_data = json.loads(assessment_file.read_text(encoding="utf-8"))
        assessment_id = finalized["assessment_id"]
        user_dir = assessment_file.parent

        try:
            evaluation_result = evaluate_assessment_file(assessment_file)
            evaluation_result["evaluated_at"] = datetime.utcnow().isoformat()

            evaluation_file = user_dir / f"{assessment_id}_evaluation.json"
            with open(evaluation_file, "w", encoding="utf-8") as f:
                json.dump(evaluation_result, f, indent=2)

            _apply_evaluation_to_user(
                current_user,
                assessment_data.get("subject", ""),
                evaluation_result,
            )

            db.commit()
            db.refresh(current_user)

            try:
                from app.services.topic_performance_service import sync_topic_performances
                sync_topic_performances(db, current_user.id)
            except Exception as sync_err:
                print(f"[ERROR] Failed to sync topic performance: {sync_err}")

            assessment_data["status"] = "evaluated"
            with open(assessment_file, "w", encoding="utf-8") as f:
                json.dump(assessment_data, f, indent=2)

        except Exception as eval_error:
            print(f"Adaptive evaluation error: {eval_error}")
            assessment_data["status"] = "evaluation_failed"
            assessment_data["evaluation_error"] = str(eval_error)
            with open(assessment_file, "w", encoding="utf-8") as f:
                json.dump(assessment_data, f, indent=2)

        return AssessmentResponse(
            assessment_id=assessment_id,
            chapter=assessment_data.get("chapter", "Adaptive Diagnostic"),
            subject=assessment_data.get("subject", ""),
            total_questions=finalized["total_questions"],
            submitted_at=assessment_data.get("submitted_at", ""),
            status=assessment_data.get("status", "evaluating"),
        )

    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to finalize adaptive assessment: {str(e)}",
        )


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
            "grade": current_user.current_level or 10,
            "curriculum": CURRICULUM_FRAMEWORK,
            "answers": [
                {
                    "question_id": ans.question_id,
                    "answer": ans.answer,
                    "chapter": ans.chapter,
                    "question": ans.question,
                    "question_raw": ans.question_raw,
                    "expected_answer": ans.expected_answer,
                    "answer_type": ans.answer_type,
                }
                for ans in submission.answers
            ],
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "evaluating"
        }
        
        # Create file-based storage
        assessments_dir = ASSESSMENTS_DIR
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
            evaluation_result = evaluate_assessment_file(assessment_file)
            
            # Add timestamp
            evaluation_result["evaluated_at"] = datetime.utcnow().isoformat()
            
            # Save evaluation
            evaluation_file = user_dir / f"{assessment_id}_evaluation.json"
            with open(evaluation_file, "w", encoding="utf-8") as f:
                json.dump(evaluation_result, f, indent=2)
            
            _apply_evaluation_to_user(
                current_user,
                assessment_data.get("subject", ""),
                evaluation_result,
            )

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
            assessment_data["status"] = "evaluation_failed"
            assessment_data["evaluation_error"] = str(eval_error)
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
        assessments_dir = ASSESSMENTS_DIR
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
        assessments_dir = ASSESSMENTS_DIR
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
        assessments_dir = ASSESSMENTS_DIR
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
        
        return _build_evaluation_response(assessment_id, evaluation_data, assessment_data)
        
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
        assessments_dir = ASSESSMENTS_DIR
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
            with open(evaluation_file, "r", encoding="utf-8") as f:
                evaluation_data = json.load(f)
            with open(assessment_file, "r", encoding="utf-8") as f:
                assessment_data = json.load(f)

            return _build_evaluation_response(assessment_id, evaluation_data, assessment_data)

        evaluation_result = evaluate_assessment_file(assessment_file)

        with open(assessment_file, "r", encoding="utf-8") as f:
            assessment_data = json.load(f)
        
        # Add timestamp
        from datetime import datetime
        evaluation_result["evaluated_at"] = datetime.utcnow().isoformat()
        
        # Save evaluation
        with open(evaluation_file, "w", encoding="utf-8") as f:
            json.dump(evaluation_result, f, indent=2)
        
        _apply_evaluation_to_user(
            current_user,
            assessment_data.get("subject", ""),
            evaluation_result,
        )

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
        
        return _build_evaluation_response(assessment_id, evaluation_result, assessment_data)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Evaluation error: {traceback.format_exc()}")
        detail = str(e)
        if "Ollama" in detail or "ollama" in detail.lower():
            detail += (
                " Install: https://ollama.com — then run "
                f"`ollama pull {settings.OLLAMA_MODEL}` and `ollama serve`."
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to evaluate assessment: {detail}"
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
        assessments_dir = ASSESSMENTS_DIR
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
        assessments_dir = ASSESSMENTS_DIR
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
        latest_assessment_id = None
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
                
                if normalize_subject_key(assessment_data.get("subject", "")) == normalize_subject_key(subject):
                    submitted_at = assessment_data.get("submitted_at", "")
                    if submitted_at > latest_timestamp:
                        latest_timestamp = submitted_at
                        latest_assessment = assessment_data
                        latest_assessment_id = assessment_file.stem
                        
                        # Load corresponding evaluation
                        evaluation_file = user_dir / f"{latest_assessment_id}_evaluation.json"
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
        
        # Attach study resources for progress / roadmap consumers
        from app.services.learning_resource_service import attach_study_resources
        if not latest_evaluation.get("recommended_resources"):
            grade = int(latest_assessment.get("grade") or 10)
            attach_study_resources(
                latest_evaluation,
                subject=latest_assessment.get("subject", subject),
                grade=grade,
            )

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
            "weakest_chapters": overall_analysis.get("weakest_chapters", []),
            "study_plan": overall_analysis.get("study_plan", {}),
            "recommended_resources": latest_evaluation.get("recommended_resources", []),
            "assessment_id": latest_assessment_id,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load subject progress: {str(e)}"
        )


@router.get("/learning-roadmap/{subject}")
async def get_learning_roadmap(
    subject: str,
    current_user: User = Depends(get_current_user),
):
    """
    Personalized learning roadmap from the latest evaluated assessment.
    Includes study steps and curated Khan Academy / YouTube links per weak topic.
    """
    try:
        assessment_data, evaluation_data, assessment_id = _find_latest_subject_evaluation(
            current_user.id, subject
        )
        if not assessment_data or not evaluation_data or not assessment_id:
            return {
                "has_data": False,
                "subject": subject,
                "message": (
                    f"No evaluated {subject} assessment found. "
                    "Complete an adaptive diagnostic first."
                ),
            }

        return _roadmap_from_evaluation(
            subject, assessment_data, evaluation_data, assessment_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load learning roadmap: {str(e)}",
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
