"""
Professional AI assessment evaluator — local Ollama with Nepal CDC protocol.
Uses per-question grading for reliable performance on local GPU hardware.
"""
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.core.config import settings
from app.core.curriculum import weakness_level_for_accuracy, estimate_grade_level
from app.core.evaluation_protocol import (
    aggregate_domain_analysis,
    aggregate_learning_outcomes,
    compute_marks_weighted_score,
    compute_overall_score,
    normalize_evaluation_result,
)
from app.services.answer_checker import try_check_answer
from app.services.answer_format import flatten_student_answer
from app.services.learning_resource_service import attach_study_resources
from app.services.ollama_client import OllamaClient
from app.services.curriculum_metadata_service import get_curriculum_metadata

QUESTION_GRADER_PROMPT = """
You are a strict Nepal CDC examiner for Grades 6–10.
Judge ONE student answer only. Return ONLY valid JSON:
{
  "correctness": "correct" | "partial" | "incorrect",
  "score": 1 | 0.5 | 0,
  "medium_reason": "10–25 words when partial/incorrect",
  "strengths": ["optional short phrase"],
  "weaknesses": ["optional short phrase"]
}
Rules: empty, placeholder, or off-topic = incorrect (score 0).
Correct method with minor slip = partial (0.5). Fully correct = 1.
For maths, check the numeric/logical result — not just effort.
"""

WRITING_RUBRIC_PROMPT = """
You are a Nepal CDC English examiner grading ONE writing response.
Score each rubric criterion 0, 1, or 2 (0=missing, 1=partial, 2=strong).
Return ONLY valid JSON:
{
  "correctness": "correct" | "partial" | "incorrect",
  "score": 1 | 0.5 | 0,
  "rubric_scores": {"criterion_name": 0|1|2, ...},
  "medium_reason": "10–25 words when partial/incorrect",
  "strengths": ["optional"],
  "weaknesses": ["optional"]
}
Map total rubric performance to score: mostly 2s = 1; mixed 1–2 = 0.5; mostly 0–1 = 0.
Empty or off-topic = incorrect (0).
"""

SUMMARY_PROMPT = """
You are a Nepal CDC diagnostic report writer.
Given chapter performance stats, return ONLY JSON:
{"learning_gap_summary": ["3–5 short professional diagnostic sentences"]}
No markdown. Be specific to the weakest chapters listed.
"""


class AIEvaluationService:
    """Grade assessments using a local LLM with structured Nepal CDC rubrics."""

    def __init__(self):
        self.client = OllamaClient(timeout=settings.OLLAMA_EVAL_TIMEOUT)
        self._question_timeout = min(settings.OLLAMA_EVAL_TIMEOUT, 120)

    def evaluate_assessment(self, assessment_file_path: Path) -> Dict[str, Any]:
        with open(assessment_file_path, encoding="utf-8") as f:
            assessment_data = json.load(f)

        if not self.client.is_available():
            raise RuntimeError(self.client.readiness_message())

        if not self.client.is_model_ready():
            raise RuntimeError(self.client.readiness_message())

        grade = int(assessment_data.get("grade") or settings.DEFAULT_STUDENT_GRADE)
        subject = assessment_data.get("subject", "")
        answers = assessment_data.get("answers", [])

        if not answers:
            raise ValueError("Assessment has no answers to evaluate")

        question_analysis: Dict[str, Any] = {}
        for item in answers:
            qid = item.get("question_id", "")
            if not qid:
                continue
            question_analysis[qid] = self._grade_single_answer(
                grade=grade,
                subject=subject,
                item=item,
            )

        chapter_analysis = self._aggregate_chapter_analysis(question_analysis, answers)
        domain_analysis = aggregate_domain_analysis(question_analysis, answers)
        lo_analysis = aggregate_learning_outcomes(question_analysis, answers)
        overall_analysis = self._build_overall_analysis(
            chapter_analysis, grade, subject, question_analysis, domain_analysis, answers, lo_analysis
        )

        raw = {
            "chapter_analysis": chapter_analysis,
            "domain_analysis": domain_analysis,
            "learning_outcome_analysis": lo_analysis,
            "question_analysis": question_analysis,
            "overall_analysis": overall_analysis,
        }
        result = normalize_evaluation_result(
            raw,
            evaluation_method=f"ai_ollama_{settings.OLLAMA_MODEL}_per_question",
        )
        result["evaluated_at"] = datetime.now(timezone.utc).isoformat()
        attach_study_resources(result, subject=subject, grade=grade, answers=answers)

        evaluation_file = assessment_file_path.parent / f"{assessment_file_path.stem}_evaluation.json"
        with open(evaluation_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result

    def _grade_single_answer(self, grade: int, subject: str, item: dict) -> Dict[str, Any]:
        question_raw = item.get("question_raw") or item.get("question") or ""
        student_answer = flatten_student_answer(item.get("answer", ""))

        checked = try_check_answer(
            question_raw,
            student_answer,
            subject,
            expected_answer=item.get("expected_answer"),
            answer_type=item.get("answer_type"),
        )
        if checked:
            return checked

        item_type = (item.get("item_type") or "").lower()
        rubric = item.get("rubric")
        use_rubric = bool(rubric) or item_type in ("guided_writing", "functional_writing")

        payload = {
            "grade": grade,
            "subject": subject,
            "chapter": item.get("chapter"),
            "domain": item.get("domain"),
            "item_type": item.get("item_type"),
            "question": question_raw[:600],
            "student_answer": student_answer[:800],
        }
        if item.get("context_text"):
            payload["reading_passage"] = str(item["context_text"])[:1200]
        if item.get("expected_answer"):
            payload["model_answer"] = str(item["expected_answer"])[:400]
            payload["grading_note"] = (
                "Compare student answer to model_answer. Partial credit if key ideas match."
            )
        if use_rubric and rubric:
            payload["rubric_criteria"] = rubric

        system_prompt = WRITING_RUBRIC_PROMPT if use_rubric and rubric else QUESTION_GRADER_PROMPT
        try:
            raw = self.client.chat_json(
                system=system_prompt,
                user=json.dumps(payload, ensure_ascii=False),
                temperature=0.1,
            )
            return self._normalize_question_result(raw)
        except Exception as exc:
            print(f"Question grade fallback ({item.get('question_id')}): {exc}")
            return self._heuristic_question_result(
                student_answer,
                question_raw,
                subject,
                item.get("expected_answer"),
                item.get("answer_type"),
            )

    @staticmethod
    def _normalize_question_result(raw: dict) -> Dict[str, Any]:
        score = float(raw.get("score", 0))
        correctness = raw.get("correctness", "incorrect")
        if correctness == "correct":
            score = max(score, 1.0)
        elif correctness == "partial":
            score = max(score, 0.5)
        else:
            score = min(score, 0.0)
            correctness = "incorrect"

        entry: Dict[str, Any] = {
            "correctness": correctness,
            "score": score,
        }
        if raw.get("medium_reason"):
            entry["medium_reason"] = raw["medium_reason"]
        if raw.get("strengths"):
            entry["strengths"] = raw["strengths"] if isinstance(raw["strengths"], list) else [raw["strengths"]]
        if raw.get("weaknesses"):
            entry["weaknesses"] = raw["weaknesses"] if isinstance(raw["weaknesses"], list) else [raw["weaknesses"]]
        if raw.get("rubric_scores") and isinstance(raw["rubric_scores"], dict):
            entry["rubric_scores"] = raw["rubric_scores"]
        return entry

    @staticmethod
    def _heuristic_question_result(
        answer: str,
        question_raw: str = "",
        subject: str = "",
        expected_answer: str | None = None,
        answer_type: str | None = None,
    ) -> Dict[str, Any]:
        checked = try_check_answer(
            question_raw, answer, subject,
            expected_answer=expected_answer,
            answer_type=answer_type,
        )
        if checked:
            return checked
        text = (answer or "").strip()
        if not text:
            return {"correctness": "incorrect", "score": 0.0, "medium_reason": "No answer provided."}
        return {
            "correctness": "incorrect",
            "score": 0.0,
            "medium_reason": "AI grader unavailable; answer could not be verified.",
            "grading_method": "unresolved",
            "needs_review": True,
        }

    def _aggregate_chapter_analysis(
        self, question_analysis: Dict[str, Any], answers: List[dict]
    ) -> Dict[str, Any]:
        by_chapter: Dict[str, list] = defaultdict(list)
        for item in answers:
            qid = item.get("question_id", "")
            chapter = item.get("chapter") or "General"
            result = question_analysis.get(qid)
            if result:
                by_chapter[chapter].append(result)

        chapter_analysis: Dict[str, Any] = {}
        for chapter, items in by_chapter.items():
            total = len(items)
            correct = sum(1 for x in items if x.get("correctness") == "correct")
            partial = sum(1 for x in items if x.get("correctness") == "partial")
            incorrect = total - correct - partial
            raw_score = sum(float(x.get("score", 0)) for x in items)
            accuracy = int(round((raw_score / total) * 100)) if total else 0

            strengths: List[str] = []
            weaknesses: List[str] = []
            for x in items:
                strengths.extend(x.get("strengths") or [])
                weaknesses.extend(x.get("weaknesses") or [])

            chapter_analysis[chapter] = {
                "total_questions": total,
                "correct": correct,
                "partial": partial,
                "incorrect": incorrect,
                "accuracy_percentage": accuracy,
                "chapter_score_out_of_10": round((raw_score / total) * 10, 1) if total else 0.0,
                "weakness_level": weakness_level_for_accuracy(accuracy),
                "strengths": list(dict.fromkeys(strengths))[:3],
                "weaknesses": list(dict.fromkeys(weaknesses))[:3],
                "reasoning": (
                    f"Answered {correct} fully correct, {partial} partial, "
                    f"and {incorrect} incorrect out of {total} in {chapter}."
                ),
            }
        return chapter_analysis

    def _build_overall_analysis(
        self,
        chapter_analysis: Dict[str, Any],
        grade: int,
        subject: str,
        question_analysis: Dict[str, Any] | None = None,
        domain_analysis: Dict[str, Any] | None = None,
        answers: List[dict] | None = None,
        lo_analysis: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if not chapter_analysis:
            return {
                "final_score_out_of_100": 0,
                "estimated_student_grade_level": grade,
                "strongest_chapters": [],
                "weakest_chapters": [],
                "learning_gap_summary": [],
                "unresolved_questions": 0,
            }

        chapter_scores = sorted(
            chapter_analysis.items(),
            key=lambda x: x[1].get("accuracy_percentage", 0),
            reverse=True,
        )
        chapter_score = compute_overall_score(chapter_analysis)
        marks_score = compute_marks_weighted_score(answers or [], question_analysis or {})
        has_marks = any(a.get("marks") for a in (answers or []))
        final_score = marks_score if has_marks else chapter_score
        meta = get_curriculum_metadata()
        proficiency = meta.proficiency_band_for_score(final_score)

        overall = {
            "final_score_out_of_100": final_score,
            "chapter_weighted_score": compute_overall_score(chapter_analysis),
            "marks_weighted_score": compute_marks_weighted_score(answers or [], question_analysis or {}),
            "estimated_student_grade_level": estimate_grade_level(final_score),
            "proficiency_band": proficiency.get("band"),
            "proficiency_label": proficiency.get("label"),
            "strongest_chapters": [c[0] for c in chapter_scores[:2]],
            "weakest_chapters": [c[0] for c in chapter_scores[-3:]],
            "learning_gap_summary": self._generate_learning_summary(
                subject, chapter_scores
            ),
            "unresolved_questions": sum(
                1 for q in (question_analysis or {}).values()
                if q.get("grading_method") == "unresolved" or q.get("needs_review")
            ),
        }
        if domain_analysis:
            overall["domain_analysis"] = domain_analysis
            weakest_domains = sorted(
                domain_analysis.items(),
                key=lambda x: x[1].get("accuracy_percentage", 0),
            )[:2]
            if weakest_domains and weakest_domains[0][1].get("accuracy_percentage", 100) < 85:
                overall["weakest_domains"] = [d[0] for d in weakest_domains]
        if lo_analysis:
            overall["learning_outcome_analysis"] = lo_analysis
            weak_los = sorted(lo_analysis.items(), key=lambda x: x[1].get("accuracy_percentage", 0))[:3]
            overall["weakest_learning_outcomes"] = [lo[0] for lo in weak_los if lo[1].get("accuracy_percentage", 100) < 85]
        return overall

    def _generate_learning_summary(
        self, subject: str, chapter_scores: List[tuple]
    ) -> List[str]:
        weakest = [
            {"chapter": name, **data}
            for name, data in chapter_scores[-3:]
            if data.get("accuracy_percentage", 100) < 85
        ]
        if not weakest:
            return [
                f"Strong performance across {subject} topics at Nepal CDC grade level.",
                "Continue periodic revision to maintain accuracy.",
            ]

        payload = {
            "subject": subject,
            "chapters": [
                {
                    "chapter": w["chapter"],
                    "accuracy": w.get("accuracy_percentage"),
                    "weakness_level": w.get("weakness_level"),
                }
                for w in weakest
            ],
        }
        try:
            raw = self.client.chat_json(
                system=SUMMARY_PROMPT,
                user=json.dumps(payload, ensure_ascii=False),
                temperature=0.2,
            )
            summary = raw.get("learning_gap_summary")
            if isinstance(summary, list) and summary:
                return [str(s) for s in summary[:5]]
        except Exception as exc:
            print(f"Summary generation fallback: {exc}")

        return [
            f"Focus revision on: {', '.join(w['chapter'] for w in weakest)}.",
            "Practice step-by-step worked examples from the Nepal CDC textbook.",
            "Re-check calculations and units (Rs., %, cm) in word problems.",
        ]
