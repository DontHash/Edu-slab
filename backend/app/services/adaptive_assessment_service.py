"""
Adaptive assessment — 10 questions, one at a time, dynamic difficulty.
"""
import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.adaptive_config import (
    ADAPTIVE_TOTAL_QUESTIONS,
    DIFFICULTY_LABELS,
    DIFFICULTY_MAX,
    DIFFICULTY_MIN,
    starting_difficulty_for_grade,
)
from app.core.curriculum import CURRICULUM_FRAMEWORK
from app.services.ollama_client import OllamaClient
from app.services.question_bank_service import get_question_bank

from app.core.paths import ADAPTIVE_SESSIONS_DIR, ASSESSMENTS_DIR
from app.services.answer_format import flatten_student_answer
from app.services.answer_checker import try_check_answer


class AdaptiveAssessmentService:
    def __init__(self):
        self.bank = get_question_bank()
        self.ollama = OllamaClient()

    def _session_path(self, user_id: int, session_id: str) -> Path:
        return ADAPTIVE_SESSIONS_DIR / str(user_id) / f"{session_id}.json"

    def _load_session(self, user_id: int, session_id: str) -> Dict[str, Any]:
        path = self._session_path(user_id, session_id)
        if not path.exists():
            raise FileNotFoundError("Adaptive session not found")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("user_id") != user_id:
            raise PermissionError("Session does not belong to this user")
        return data

    def _save_session(self, session: Dict[str, Any]) -> None:
        path = self._session_path(session["user_id"], session["session_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

    def _quick_check(
        self,
        question: str,
        answer: str,
        subject: str,
        question_raw: str = "",
        expected_answer: str | None = None,
        answer_type: str | None = None,
    ) -> Dict[str, Any]:
        """Fast correctness check to adjust difficulty before next question."""
        text = flatten_student_answer(answer or "").strip()
        if not text:
            return {"correct": False, "partial": False, "score": 0.0, "method": "empty"}

        raw = question_raw or question
        checked = try_check_answer(
            raw, text, subject,
            expected_answer=expected_answer,
            answer_type=answer_type,
        )
        if checked:
            score = float(checked.get("score", 0))
            return {
                "correct": checked.get("correctness") == "correct",
                "partial": checked.get("correctness") == "partial",
                "score": score,
                "reason": checked.get("medium_reason", ""),
                "method": checked.get("grading_method", "deterministic"),
            }

        if self.ollama.is_available():
            try:
                result = self.ollama.chat_json(
                    system=(
                        "You are a strict Nepal CDC examiner. Judge ONE student answer only. "
                        'Return JSON: {"correct": boolean, "partial": boolean, "score": 0|0.5|1, '
                        '"reason": "10 words max"}'
                    ),
                    user=json.dumps({
                        "subject": subject,
                        "question": question[:800],
                        "student_answer": text[:600],
                    }),
                    temperature=0.1,
                )
                score = float(result.get("score", 0))
                if result.get("correct"):
                    score = max(score, 1.0)
                elif result.get("partial"):
                    score = max(score, 0.5)
                return {
                    "correct": bool(result.get("correct")),
                    "partial": bool(result.get("partial")),
                    "score": min(1.0, max(0.0, score)),
                    "reason": result.get("reason", ""),
                    "method": "ai_ollama",
                }
            except Exception as exc:
                print(f"Adaptive quick check AI failed: {exc}")

        return {
            "correct": False,
            "partial": False,
            "score": 0.0,
            "reason": "AI grader unavailable — difficulty held until full evaluation.",
            "method": "unresolved",
        }

    def _adjust_difficulty(self, current: int, score: float) -> int:
        if score >= 0.75:
            return min(DIFFICULTY_MAX, current + 1)
        if score < 0.5:
            return max(DIFFICULTY_MIN, current - 1)
        return current

    def _pick_by_difficulty(
        self,
        pool: list[Dict[str, Any]],
        difficulty: int,
        exclude_ids: set | None = None,
    ) -> Dict[str, Any] | None:
        """Pick a question matching difficulty; fall back to adjacent levels."""
        exclude_ids = exclude_ids or set()
        available = [q for q in pool if q.get("id") not in exclude_ids]

        def at_level(level: int):
            return [q for q in available if q.get("difficulty") == level]

        for level in [difficulty, difficulty - 1, difficulty + 1, 2, 1, 3]:
            if level < DIFFICULTY_MIN or level > DIFFICULTY_MAX:
                continue
            opts = at_level(level)
            if opts:
                return random.choice(opts)
        return random.choice(available) if available else None

    def start_session(self, user_id: int, subject: str, grade: int) -> Dict[str, Any]:
        from app.services.curriculum_metadata_service import get_curriculum_metadata

        grade = max(6, min(10, int(grade)))
        difficulty = starting_difficulty_for_grade(grade)

        meta = get_curriculum_metadata()
        grid = meta.get_spec_grid(subject, grade)
        use_blueprint = grid is not None

        if use_blueprint:
            planned = self.bank.assemble_blueprint_pool(
                subject, grade, ADAPTIVE_TOTAL_QUESTIONS, difficulty=difficulty
            )
        else:
            planned = self.bank.build_classified_pool(
                subject, grade, difficulty=difficulty
            )
            if len(planned) >= ADAPTIVE_TOTAL_QUESTIONS:
                random.shuffle(planned)
                planned = planned[:ADAPTIVE_TOTAL_QUESTIONS]

        if len(planned) < ADAPTIVE_TOTAL_QUESTIONS:
            raise ValueError(
                f"Not enough validated questions for {subject} grade {grade}. "
                f"Found {len(planned)}, need {ADAPTIVE_TOTAL_QUESTIONS}."
            )

        session_id = str(uuid.uuid4())
        first = self._pick_by_difficulty(planned, difficulty) or planned[0]
        remaining = [q for q in planned if q["id"] != first["id"]]

        session = {
            "session_id": session_id,
            "user_id": user_id,
            "subject": subject,
            "grade": grade,
            "curriculum": CURRICULUM_FRAMEWORK,
            "total_questions": ADAPTIVE_TOTAL_QUESTIONS,
            "answered_count": 0,
            "difficulty_level": difficulty,
            "starting_difficulty": difficulty,
            "blueprint_mode": use_blueprint,
            "planned_question_ids": [q["id"] for q in planned],
            "remaining_questions": remaining,
            "used_question_ids": [first["id"]],
            "used_chapters": [first["chapter"]],
            "answers": [],
            "status": "in_progress",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "current_question": first,
        }
        self._save_session(session)

        return {
            "session_id": session_id,
            "question_number": 1,
            "total_questions": ADAPTIVE_TOTAL_QUESTIONS,
            "difficulty": DIFFICULTY_LABELS[difficulty],
            "grade": grade,
            "blueprint_mode": use_blueprint,
            "dynamic_questions": True,
            "question": self._public_question(first),
            "progress_percent": 0,
        }

    def submit_answer(
        self, user_id: int, session_id: str, question_id: str, answer: str
    ) -> Dict[str, Any]:
        session = self._load_session(user_id, session_id)
        if session.get("status") != "in_progress":
            raise ValueError("Session already completed")

        current = session.get("current_question")
        if not current or current["id"] != question_id:
            raise ValueError("Question mismatch — refresh and use the current question")

        check = self._quick_check(
            current["question"],
            answer,
            session["subject"],
            current.get("question_raw", ""),
            current.get("expected_answer"),
            current.get("answer_type"),
        )
        new_difficulty = self._adjust_difficulty(session["difficulty_level"], check["score"])

        session["answers"].append({
            "question_id": question_id,
            "question": current["question"],
            "question_raw": current.get("question_raw", ""),
            "expected_answer": current.get("expected_answer"),
            "answer_type": current.get("answer_type"),
            "chapter": current["chapter"],
            "domain": current.get("domain"),
            "section": current.get("section"),
            "cognitive_level": current.get("cognitive_level"),
            "learning_outcome_id": current.get("learning_outcome_id"),
            "item_type": current.get("item_type"),
            "context_text": current.get("context_text"),
            "rubric": current.get("rubric"),
            "marks": current.get("marks", 1),
            "answer": answer,
            "difficulty": session["difficulty_level"],
            "difficulty_label": DIFFICULTY_LABELS[session["difficulty_level"]],
            "quick_check": check,
        })
        session["answered_count"] = len(session["answers"])
        session["difficulty_level"] = new_difficulty

        if session["answered_count"] >= ADAPTIVE_TOTAL_QUESTIONS:
            session["status"] = "completed"
            session["current_question"] = None
            session["completed_at"] = datetime.now(timezone.utc).isoformat()
            self._save_session(session)
            return {
                "session_id": session_id,
                "completed": True,
                "question_number": ADAPTIVE_TOTAL_QUESTIONS,
                "total_questions": ADAPTIVE_TOTAL_QUESTIONS,
                "progress_percent": 100,
                "last_result": {
                    "correct": check["correct"],
                    "partial": check.get("partial", False),
                    "score": check["score"],
                    "reason": check.get("reason", ""),
                    "method": check.get("method", ""),
                    "next_difficulty": DIFFICULTY_LABELS[new_difficulty],
                },
                "message": "All 10 questions answered. Submit to finish and get your report.",
            }

        if session.get("blueprint_mode") and session.get("remaining_questions"):
            remaining = session["remaining_questions"]
            used_ids = set(session["used_question_ids"])
            nxt = self._pick_by_difficulty(remaining, new_difficulty, used_ids)
            if nxt:
                session["remaining_questions"] = [
                    q for q in remaining if q["id"] != nxt["id"]
                ]
            else:
                nxt = remaining.pop(0) if remaining else None
                session["remaining_questions"] = remaining
        else:
            pool = self.bank.build_classified_pool(
                session["subject"], session["grade"], difficulty=new_difficulty
            )
            used_ids = set(session["used_question_ids"])
            used_chapters = set(session["used_chapters"])
            nxt = self.bank.pick_adaptive_question(pool, new_difficulty, used_ids, used_chapters)

        if not nxt:
            session["status"] = "completed"
            session["current_question"] = None
            self._save_session(session)
            return {
                "session_id": session_id,
                "completed": True,
                "progress_percent": 100,
                "message": "No more questions available at this difficulty.",
            }

        session["used_question_ids"].append(nxt["id"])
        session["used_chapters"].append(nxt["chapter"])
        session["current_question"] = nxt
        self._save_session(session)

        progress = int((session["answered_count"] / ADAPTIVE_TOTAL_QUESTIONS) * 100)
        return {
            "session_id": session_id,
            "completed": False,
            "question_number": session["answered_count"] + 1,
            "total_questions": ADAPTIVE_TOTAL_QUESTIONS,
            "progress_percent": progress,
            "last_result": {
                "correct": check["correct"],
                "partial": check.get("partial", False),
                "score": check["score"],
                "reason": check.get("reason", ""),
                "method": check.get("method", ""),
                "next_difficulty": DIFFICULTY_LABELS[new_difficulty],
            },
            "question": self._public_question(nxt),
            "difficulty": DIFFICULTY_LABELS[new_difficulty],
        }

    def finalize_session(self, user_id: int, session_id: str) -> Dict[str, Any]:
        """Convert adaptive session to standard assessment file for full AI evaluation."""
        session = self._load_session(user_id, session_id)
        if session.get("answered_count", 0) < 1:
            raise ValueError("No answers to finalize")

        assessment_id = str(uuid.uuid4())
        assessment_data = {
            "assessment_id": assessment_id,
            "user_id": user_id,
            "subject": session["subject"],
            "grade": session["grade"],
            "curriculum": session["curriculum"],
            "chapter": "Adaptive Diagnostic (10 questions)",
            "mode": "adaptive",
            "adaptive_session_id": session_id,
            "answers": [
                {
                    "question_id": a["question_id"],
                    "answer": a["answer"],
                    "chapter": a["chapter"],
                    "question": a["question"],
                    "question_raw": a.get("question_raw", ""),
                    "expected_answer": a.get("expected_answer"),
                    "answer_type": a.get("answer_type"),
                    "domain": a.get("domain"),
                    "section": a.get("section"),
                    "cognitive_level": a.get("cognitive_level"),
                    "learning_outcome_id": a.get("learning_outcome_id"),
                    "item_type": a.get("item_type"),
                    "context_text": a.get("context_text"),
                    "rubric": a.get("rubric"),
                    "marks": a.get("marks", 1),
                }
                for a in session["answers"]
            ],
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "status": "evaluating",
            "adaptive_summary": {
                "final_difficulty": DIFFICULTY_LABELS[session["difficulty_level"]],
                "questions_answered": len(session["answers"]),
            },
        }

        user_dir = ASSESSMENTS_DIR / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        assessment_file = user_dir / f"{assessment_id}.json"
        with open(assessment_file, "w", encoding="utf-8") as f:
            json.dump(assessment_data, f, indent=2, ensure_ascii=False)

        session["status"] = "finalized"
        session["assessment_id"] = assessment_id
        self._save_session(session)

        return {
            "assessment_id": assessment_id,
            "assessment_file": str(assessment_file),
            "total_questions": len(session["answers"]),
        }

    @staticmethod
    def _public_question(q: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": q["id"],
            "question": q["question"],
            "chapter": q["chapter"],
            "difficulty": q.get("difficulty_label", "medium"),
            "type": q.get("type", "short_answer"),
            "domain": q.get("domain"),
            "section": q.get("section"),
            "context_text": q.get("context_text"),
            "item_type": q.get("item_type"),
            "cognitive_level": q.get("cognitive_level"),
            "generative": q.get("generative", False),
        }


_service: AdaptiveAssessmentService | None = None


def get_adaptive_service() -> AdaptiveAssessmentService:
    global _service
    if _service is None:
        _service = AdaptiveAssessmentService()
    return _service
