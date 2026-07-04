"""
Rule-based assessment evaluation using Nepal CDC weakness metrics.
Used only when AI grading is unavailable — does not award credit by word count.
"""
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from app.core.curriculum import estimate_grade_level, weakness_level_for_accuracy
from app.core.evaluation_protocol import (
    aggregate_domain_analysis,
    aggregate_learning_outcomes,
    compute_marks_weighted_score,
    compute_overall_score,
    normalize_evaluation_result,
)
from app.services.answer_format import flatten_student_answer
from app.services.answer_checker import try_check_answer
from app.services.learning_resource_service import attach_study_resources


class RuleEvaluationService:
    """Evaluate answers with deterministic checks only; never guess from length."""

    def _score_answer(
        self,
        answer: str,
        question_raw: str,
        subject: str,
        expected_answer: str | None = None,
        answer_type: str | None = None,
    ) -> tuple[str, float, dict]:
        checked = try_check_answer(
            question_raw, answer, subject,
            expected_answer=expected_answer,
            answer_type=answer_type,
        )
        if checked:
            return checked["correctness"], float(checked["score"]), checked

        text = (answer or "").strip()
        if not text:
            return "incorrect", 0.0, {"medium_reason": "No answer provided.", "grading_method": "rule_empty"}

        return (
            "incorrect",
            0.0,
            {
                "medium_reason": "AI grader unavailable; open-ended answer not auto-scored.",
                "grading_method": "unresolved",
                "needs_review": True,
            },
        )

    def evaluate_assessment(self, assessment_file_path: Path) -> Dict[str, Any]:
        with open(assessment_file_path, encoding="utf-8") as f:
            assessment_data = json.load(f)

        subject = assessment_data.get("subject", "")
        answers = assessment_data.get("answers", [])
        question_analysis: Dict[str, Any] = {}
        by_chapter: Dict[str, list] = defaultdict(list)

        for item in answers:
            qid = item.get("question_id", "")
            chapter = item.get("chapter") or "General"
            question_raw = item.get("question_raw") or item.get("question") or ""
            verdict, score, extra = self._score_answer(
                flatten_student_answer(item.get("answer", "")),
                question_raw,
                subject,
                item.get("expected_answer"),
                item.get("answer_type"),
            )
            entry = {"correctness": verdict, "score": score, **extra}
            question_analysis[qid] = entry
            by_chapter[chapter].append(entry)

        chapter_analysis: Dict[str, Any] = {}
        chapter_scores = []

        for chapter, items in by_chapter.items():
            total = len(items)
            correct = sum(1 for x in items if x["correctness"] == "correct")
            partial = sum(1 for x in items if x["correctness"] == "partial")
            incorrect = total - correct - partial
            raw_score = sum(x["score"] for x in items)
            max_score = float(total)
            accuracy = int(round((raw_score / max_score) * 100)) if max_score else 0
            chapter_score_10 = round((raw_score / max_score) * 10, 1) if max_score else 0.0

            chapter_analysis[chapter] = {
                "total_questions": total,
                "correct": correct,
                "partial": partial,
                "incorrect": incorrect,
                "accuracy_percentage": accuracy,
                "chapter_score_out_of_10": chapter_score_10,
                "weakness_level": weakness_level_for_accuracy(accuracy),
            }
            chapter_scores.append((chapter, accuracy))

        chapter_scores.sort(key=lambda x: x[1], reverse=True)
        domain_analysis = aggregate_domain_analysis(question_analysis, answers)
        lo_analysis = aggregate_learning_outcomes(question_analysis, answers)
        chapter_score = compute_overall_score(chapter_analysis)
        marks_score = compute_marks_weighted_score(answers, question_analysis)
        has_marks = any(a.get("marks") for a in answers)
        final_score = marks_score if has_marks else chapter_score

        unresolved = sum(
            1 for q in question_analysis.values() if q.get("grading_method") == "unresolved"
        )

        from app.services.curriculum_metadata_service import get_curriculum_metadata
        proficiency = get_curriculum_metadata().proficiency_band_for_score(final_score)

        overall_analysis = {
            "final_score_out_of_100": final_score,
            "chapter_weighted_score": chapter_score,
            "marks_weighted_score": marks_score,
            "estimated_student_grade_level": estimate_grade_level(final_score),
            "proficiency_band": proficiency.get("band"),
            "proficiency_label": proficiency.get("label"),
            "domain_analysis": domain_analysis,
            "learning_outcome_analysis": lo_analysis,
            "strongest_chapters": [c[0] for c in chapter_scores[:2]],
            "weakest_chapters": [c[0] for c in chapter_scores[-3:]],
            "learning_gap_summary": [
                "Scores are based on deterministic checks only — AI grading was unavailable.",
                f"{unresolved} answer(s) could not be verified and need re-evaluation when Ollama is online.",
                "Re-run the assessment or evaluation for a full Nepal CDC diagnostic report.",
            ],
            "evaluation_method": "rule_based_nepal_cdc_v2",
            "unresolved_questions": unresolved,
        }

        raw = {
            "chapter_analysis": chapter_analysis,
            "domain_analysis": domain_analysis,
            "learning_outcome_analysis": lo_analysis,
            "question_analysis": question_analysis,
            "overall_analysis": overall_analysis,
        }
        result = normalize_evaluation_result(raw, evaluation_method="rule_based_nepal_cdc_v2")
        result["evaluated_at"] = datetime.now(timezone.utc).isoformat()

        grade = int(assessment_data.get("grade") or 10)
        attach_study_resources(result, subject=subject, grade=grade, answers=answers)

        evaluation_file = assessment_file_path.parent / f"{assessment_file_path.stem}_evaluation.json"
        with open(evaluation_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        return result
