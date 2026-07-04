"""
Professional evaluation protocol — Nepal CDC aligned metrics and JSON schema.
Used by the AI evaluator (Ollama / optional cloud).
"""
from app.core.curriculum import CURRICULUM_BOARD, CURRICULUM_FRAMEWORK, estimate_grade_level, weakness_level_for_accuracy

EVALUATOR_SYSTEM_PROMPT = f"""
You are a senior Nepal CDC ({CURRICULUM_BOARD}) assessment evaluator for Grades 6–10.
Framework: {CURRICULUM_FRAMEWORK}.

ROLE
- Grade student responses with professional, consistent, evidence-based judgment.
- Behave like a national-curriculum examiner — not a tutor, not lenient, not vague.
- Every score must be justified by what the student actually wrote.

NON-NEGOTIABLE RULES
1. Judge each answer independently using the question text and Nepal grade-level expectations.
2. Do NOT invent facts the student did not state.
3. Empty, placeholder, or off-topic answers = incorrect (score 0).
4. Correct method with minor arithmetic slip = partial (score 0.5).
5. Fully correct, complete short answers = correct (score 1).
6. Use Nepal context where relevant (NPR, local examples, CDC terminology).

PER-QUESTION SCORING (use question_id as JSON key)
- correctness: "correct" | "partial" | "incorrect"
- score: 1 | 0.5 | 0
- medium_reason: required when partial/incorrect (10–25 words, specific mistake)
- strengths: optional list of 1–2 short phrases when score is 1 or 0.5
- weaknesses: optional list of 1–2 short phrases when score < 1

PER-CHAPTER ANALYSIS (exact chapter names from input)
Compute from question scores:
- total_questions, correct, partial, incorrect
- accuracy_percentage (integer, weighted: correct=1, partial=0.5, incorrect=0)
- chapter_score_out_of_10 (round to 1 decimal)
- weakness_level using Nepal CDC bands:
  * none: ≥85%
  * mild: 70–84%
  * moderate: 50–69%
  * severe: <50%
- strengths: 1–3 bullet strings (what the student did well in this chapter)
- weaknesses: 1–3 bullet strings (specific gaps)
- reasoning: 2–4 sentences explaining performance in this chapter (professional tone)

OVERALL ANALYSIS
- final_score_out_of_100 (integer, weighted by question count across chapters — NOT equal chapter mean)
- estimated_student_grade_level: 10 if ≥85%, 9 if 70–84%, 8 if 55–69%, 7 if 40–54%, 6 if <40%
- strongest_chapters: top 2 chapter names by accuracy
- weakest_chapters: bottom 3 chapter names by accuracy
- learning_gap_summary: 3–5 short diagnostic paragraphs (not motivational fluff)

OUTPUT
Return ONLY valid JSON matching this structure — no markdown, no extra text:
{{
  "chapter_analysis": {{ "Chapter Name": {{ ... }} }},
  "question_analysis": {{ "question_id": {{ ... }} }},
  "overall_analysis": {{ ... }}
}}
"""


def build_evaluation_input(assessment_data: dict, grade: int = 10) -> dict:
    """Package assessment for the AI evaluator."""
    return {
        "framework": CURRICULUM_FRAMEWORK,
        "board": CURRICULUM_BOARD,
        "grade": grade,
        "subject": assessment_data.get("subject", ""),
        "chapter": assessment_data.get("chapter", ""),
        "answers": [
            {
                "question_id": a.get("question_id"),
                "chapter": a.get("chapter"),
                "question": a.get("question"),
                "question_raw": a.get("question_raw"),
                "expected_answer": a.get("expected_answer"),
                "answer_type": a.get("answer_type"),
                "domain": a.get("domain"),
                "item_type": a.get("item_type"),
                "learning_outcome_id": a.get("learning_outcome_id"),
                "cognitive_level": a.get("cognitive_level"),
                "marks": a.get("marks", 1),
                "rubric": a.get("rubric"),
                "context_text": a.get("context_text"),
                "student_answer": a.get("answer"),
            }
            for a in assessment_data.get("answers", [])
        ],
    }


def compute_overall_score(chapter_analysis: dict) -> int:
    """
    Weighted overall score: sum(accuracy × questions) / total questions.
    Avoids inflating/deflating scores when each chapter has one adaptive question.
    """
    if not chapter_analysis:
        return 0
    total_questions = sum(int(c.get("total_questions", 0)) for c in chapter_analysis.values())
    if total_questions <= 0:
        accuracies = [c.get("accuracy_percentage", 0) for c in chapter_analysis.values()]
        return int(round(sum(accuracies) / len(accuracies))) if accuracies else 0
    weighted = sum(
        int(c.get("accuracy_percentage", 0)) * int(c.get("total_questions", 0))
        for c in chapter_analysis.values()
    )
    return int(round(weighted / total_questions))


def compute_marks_weighted_score(answers: list, question_analysis: dict) -> int:
    """Overall score weighted by item marks (CBSE-style mark scheme)."""
    total_marks = 0
    earned = 0.0
    for item in answers or []:
        qid = item.get("question_id", "")
        marks = int(item.get("marks") or 1)
        result = question_analysis.get(qid) or {}
        score = float(result.get("score", 0))
        total_marks += marks
        earned += score * marks
    if total_marks <= 0:
        return 0
    return int(round((earned / total_marks) * 100))


def aggregate_domain_analysis(question_analysis: dict, answers: list) -> dict:
    """Roll up scores by assessment domain (reading, number_algebra, etc.)."""
    from collections import defaultdict
    from app.core.curriculum import weakness_level_for_accuracy

    by_domain: dict[str, list] = defaultdict(list)
    for item in answers or []:
        qid = item.get("question_id", "")
        domain = item.get("domain") or item.get("section") or "general"
        result = question_analysis.get(qid)
        if result:
            by_domain[domain].append(result)

    domain_analysis: dict = {}
    for domain, items in by_domain.items():
        total = len(items)
        correct = sum(1 for x in items if x.get("correctness") == "correct")
        partial = sum(1 for x in items if x.get("correctness") == "partial")
        incorrect = total - correct - partial
        raw_score = sum(float(x.get("score", 0)) for x in items)
        accuracy = int(round((raw_score / total) * 100)) if total else 0
        domain_analysis[domain] = {
            "total_questions": total,
            "correct": correct,
            "partial": partial,
            "incorrect": incorrect,
            "accuracy_percentage": accuracy,
            "weakness_level": weakness_level_for_accuracy(accuracy),
        }
    return domain_analysis


def aggregate_learning_outcomes(question_analysis: dict, answers: list) -> dict:
    """Roll up scores by learning_outcome_id."""
    from collections import defaultdict
    from app.core.curriculum import weakness_level_for_accuracy

    by_lo: dict[str, list] = defaultdict(list)
    for item in answers or []:
        lo_id = item.get("learning_outcome_id")
        if not lo_id:
            continue
        qid = item.get("question_id", "")
        result = question_analysis.get(qid)
        if result:
            by_lo[lo_id].append(result)

    lo_analysis: dict = {}
    for lo_id, items in by_lo.items():
        total = len(items)
        raw_score = sum(float(x.get("score", 0)) for x in items)
        accuracy = int(round((raw_score / total) * 100)) if total else 0
        lo_analysis[lo_id] = {
            "total_questions": total,
            "accuracy_percentage": accuracy,
            "weakness_level": weakness_level_for_accuracy(accuracy),
        }
    return lo_analysis


def normalize_chapter_analysis(chapter_analysis: dict) -> dict:
    """Ensure Nepal CDC metrics are consistent even if the model rounds differently."""
    normalized = {}
    for chapter, data in (chapter_analysis or {}).items():
        if not isinstance(data, dict):
            continue
        entry = dict(data)
        accuracy = int(entry.get("accuracy_percentage", 0))
        entry["weakness_level"] = weakness_level_for_accuracy(accuracy)
        if "chapter_score_out_of_10" not in entry and accuracy is not None:
            entry["chapter_score_out_of_10"] = round(accuracy / 10, 1)
        normalized[chapter] = entry
    return normalized


def normalize_evaluation_result(raw: dict, evaluation_method: str) -> dict:
    """Validate and normalize AI evaluation output."""
    chapter_analysis = normalize_chapter_analysis(raw.get("chapter_analysis", {}))
    question_analysis = raw.get("question_analysis") or {}
    overall = raw.get("overall_analysis") or {}

    if chapter_analysis and "final_score_out_of_100" not in overall:
        overall["final_score_out_of_100"] = compute_overall_score(chapter_analysis)

    if chapter_analysis and "estimated_student_grade_level" not in overall:
        overall["estimated_student_grade_level"] = estimate_grade_level(
            int(overall.get("final_score_out_of_100", 0))
        )

    overall["evaluation_method"] = evaluation_method
    summary = overall.get("learning_gap_summary")
    if isinstance(summary, str):
        overall["learning_gap_summary"] = [p.strip() for p in summary.split("\n") if p.strip()]
    elif not isinstance(summary, list):
        overall["learning_gap_summary"] = []
    overall.setdefault("strongest_chapters", [])
    overall.setdefault("weakest_chapters", [])

    for chapter, data in chapter_analysis.items():
        if isinstance(data.get("strengths"), str):
            data["strengths"] = [data["strengths"]]
        if isinstance(data.get("weaknesses"), str):
            data["weaknesses"] = [data["weaknesses"]]
        data.setdefault("strengths", [])
        data.setdefault("weaknesses", [])

    result = {
        "chapter_analysis": chapter_analysis,
        "question_analysis": question_analysis,
        "overall_analysis": overall,
    }
    if raw.get("domain_analysis"):
        result["domain_analysis"] = raw["domain_analysis"]
    if raw.get("learning_outcome_analysis"):
        result["learning_outcome_analysis"] = raw["learning_outcome_analysis"]
    return result
