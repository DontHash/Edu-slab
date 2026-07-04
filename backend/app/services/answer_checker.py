"""
Deterministic answer checking for Nepal CDC assessments.
Used before LLM grading when a confident match is possible.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower().strip())


def _extract_numbers(text: str) -> list[float]:
    cleaned = (text or "").replace(",", "")
    found = re.findall(r"-?\d+(?:\.\d+)?", cleaned)
    return [float(n) for n in found]


def _numbers_close(a: float, b: float, rel_tol: float = 0.02) -> bool:
    if b == 0:
        return abs(a) < 0.01
    return abs(a - b) <= max(0.01, abs(b) * rel_tol)


def _answer_has_number(answer: str, expected: float) -> bool:
    for n in _extract_numbers(answer):
        if _numbers_close(n, expected):
            return True
    return False


def _token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", _normalize_text(text)))


def _keyword_overlap(student: str, expected: str, min_ratio: float = 0.45) -> float:
    s_tokens = _token_set(student)
    e_tokens = _token_set(expected)
    if not e_tokens:
        return 0.0
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "to", "of", "in", "on",
        "and", "or", "that", "this", "it", "her", "his", "their", "she", "he",
    }
    e_tokens -= stop
    if not e_tokens:
        return 0.0
    return len(s_tokens & e_tokens) / len(e_tokens)


def _result(
    correctness: str,
    score: float,
    reason: str,
    *,
    method: str = "deterministic",
) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "correctness": correctness,
        "score": score,
        "medium_reason": reason,
        "grading_method": method,
    }
    if correctness == "correct":
        entry["strengths"] = ["Matches expected answer."]
    elif correctness == "partial":
        entry["weaknesses"] = ["Partial match to model answer."]
    else:
        entry["weaknesses"] = ["Does not match expected answer."]
    return entry


def _check_expected_answer(student_answer: str, expected_answer: str, answer_type: str) -> Optional[Dict[str, Any]]:
    expected = (expected_answer or "").strip()
    if not expected:
        return None

    answer = (student_answer or "").strip()
    atype = (answer_type or "text").lower()

    if atype in ("numeric", "number"):
        exp_parts = [p.strip() for p in re.split(r"[,;/]", expected) if p.strip()]
        nums = _extract_numbers(answer)
        for part in exp_parts:
            exp_nums = _extract_numbers(part)
            if not exp_nums:
                continue
            if nums and any(_numbers_close(n, exp_nums[0]) for n in nums):
                return _result("correct", 1.0, "Correct numeric answer.", method="answer_key")
            if "/" in part and nums:
                try:
                    num, den = part.split("/")
                    target = float(num) / float(den)
                    if any(_numbers_close(n, target, 0.05) for n in nums):
                        return _result("correct", 1.0, f"Correct: {part}.", method="answer_key")
                except (ValueError, ZeroDivisionError):
                    pass
        if exp_parts:
            exp_nums = _extract_numbers(exp_parts[0])
            if exp_nums and nums and any(_numbers_close(n, exp_nums[0]) for n in nums):
                return _result("correct", 1.0, "Correct numeric answer.", method="answer_key")
        if nums:
            return _result("incorrect", 0.0, f"Expected {expected}.", method="answer_key")
        return None

    if atype == "vocabulary":
        exp_norm = _normalize_text(expected.split("(")[0])
        ans_norm = _normalize_text(answer)
        if exp_norm in ans_norm or ans_norm in exp_norm:
            return _result("correct", 1.0, f"Correct: {expected.split('(')[0].strip()}.", method="answer_key")
        exp_first = exp_norm.split()[0] if exp_norm else ""
        if exp_first and exp_first in ans_norm:
            return _result("correct", 1.0, f"Correct vocabulary: {exp_first}.", method="answer_key")
        return _result("incorrect", 0.0, f"Expected word/phrase like '{expected.split('(')[0].strip()}'.", method="answer_key")

    overlap = _keyword_overlap(answer, expected)
    if overlap >= 0.55:
        return _result("correct", 1.0, "Answer covers key points from model response.", method="answer_key_rubric")
    if overlap >= 0.3:
        return _result(
            "partial",
            0.5,
            "Some key ideas present but answer is incomplete.",
            method="answer_key_rubric",
        )
    return _result("incorrect", 0.0, "Answer does not address the expected key points.", method="answer_key_rubric")


def _check_math_patterns(question_raw: str, student_answer: str) -> Optional[Dict[str, Any]]:
    q = question_raw.strip()
    a = student_answer.strip()
    lower_q = q.lower()

    # Simple linear equation: ax + b = c
    m = re.search(r"solve.*?(\d+)x\s*\+\s*(\d+)\s*=\s*(\d+)", lower_q)
    if m:
        coef, const, rhs = (int(x) for x in m.groups())
        if coef:
            expected = (rhs - const) / coef
            if _answer_has_number(a, expected):
                return _result("correct", 1.0, f"Correct: x = {expected:g}.")

    m = re.search(r"area of a triangle with base (\d+(?:\.\d+)?)\s*cm and height (\d+(?:\.\d+)?)", lower_q)
    if m:
        base, height = float(m.group(1)), float(m.group(2))
        expected = 0.5 * base * height
        if _answer_has_number(a, expected):
            return _result("correct", 1.0, f"Correct area = {expected:g} cm².")

    m = re.search(
        r"n\(a\)\s*=\s*(\d+).*n\(b\)\s*=\s*(\d+).*n\(a\s*[×x]\s*b\)",
        lower_q,
        re.DOTALL,
    )
    if m:
        expected = int(m.group(1)) * int(m.group(2))
        if _answer_has_number(a, expected):
            return _result("correct", 1.0, f"Correct: n(A × B) = {expected}.")
        if _extract_numbers(a):
            return _result("incorrect", 0.0, f"Expected n(A × B) = {expected}.")

    m = re.search(
        r"disjoint.*n\(a\)\s*=\s*(\d+).*n\(b\)\s*=\s*(\d+).*n\(a\s*∪\s*b\)",
        lower_q,
        re.DOTALL,
    )
    if m:
        expected = int(m.group(1)) + int(m.group(2))
        if _answer_has_number(a, expected):
            return _result("correct", 1.0, f"Correct: n(A ∪ B) = {expected}.")
        if _extract_numbers(a):
            return _result("incorrect", 0.0, f"Expected n(A ∪ B) = {expected}.")

    m = re.search(
        r"convert\s+rs\.?\s*([\d,]+)\s+to\s+us\s+dollars.*\$1\s*=\s*rs\.?\s*([\d.]+)",
        lower_q,
    )
    if m:
        amount = float(m.group(1).replace(",", ""))
        rate = float(m.group(2))
        expected = round(amount / rate, 2)
        nums = _extract_numbers(a)
        if nums and any(_numbers_close(n, expected, 0.01) for n in nums):
            return _result("correct", 1.0, f"Correct conversion: ${expected:.2f}.")
        if nums:
            return _result("incorrect", 0.0, f"Expected about ${expected:.2f}.")

    m = re.search(
        r"rs\.?\s*([\d,]+)\s+for\s+(\d+)\s+years?\s+at\s+([\d.]+)%.*compounded\s+annually",
        lower_q,
    )
    if m and "compound" in lower_q:
        p = float(m.group(1).replace(",", ""))
        t = int(m.group(2))
        r = float(m.group(3)) / 100
        expected = round(p * ((1 + r) ** t), 2)
        nums = _extract_numbers(a)
        if nums and any(_numbers_close(n, expected, 0.02) for n in nums):
            return _result("correct", 1.0, f"Correct compound amount Rs. {expected:,.2f}.")
        ci_expected = round(expected - p, 2)
        if nums and any(_numbers_close(n, ci_expected, 0.02) for n in nums):
            return _result("correct", 1.0, f"Correct compound interest Rs. {ci_expected:,.2f}.")
        if nums:
            return _result("partial", 0.5, "Numeric attempt but value does not match expected result.")

    return None


def _check_science_patterns(question_raw: str, student_answer: str) -> Optional[Dict[str, Any]]:
    """Basic science checks: numeric formulas and unit values."""
    q = question_raw.lower()
    a = student_answer.strip()

    # Q = mcΔT style
    m = re.search(r"mass.*?(\d+)\s*g.*?(?:temperature|temp).*?(\d+).*?(\d+).*specific heat.*?(\d+)", q, re.DOTALL)
    if m and ("heat" in q or "energy" in q):
        mass, t1, t2, sh = (float(x) for x in m.groups())
        expected = mass * sh * abs(t2 - t1)
        if _answer_has_number(a, expected):
            return _result("correct", 1.0, f"Correct heat energy ≈ {expected:.0f} J.", method="science_formula")

    # F = ma
    m = re.search(r"mass.*?(\d+(?:\.\d+)?)\s*kg.*?(?:acceleration|accel).*?(\d+(?:\.\d+)?)", q, re.DOTALL)
    if m and ("force" in q or "f =" in q):
        mass, accel = float(m.group(1)), float(m.group(2))
        expected = mass * accel
        if _answer_has_number(a, expected):
            return _result("correct", 1.0, f"Correct force = {expected} N.", method="science_formula")

    # Ohm's law I = V/R
    m = re.search(r"(\d+(?:\.\d+)?)\s*ω.*?(?:connected to a|across).*?(\d+(?:\.\d+)?)\s*v", q, re.DOTALL)
    if m and ("current" in q or "i = v/r" in q):
        resistance, voltage = float(m.group(1)), float(m.group(2))
        expected = voltage / resistance if resistance else 0
        if _answer_has_number(a, expected):
            return _result("correct", 1.0, f"Correct current = {expected:g} A.", method="science_formula")

    # Power P = I²R
    m = re.search(r"(\d+(?:\.\d+)?)\s*ω.*?(\d+(?:\.\d+)?)\s*a", q, re.DOTALL)
    if m and ("power" in q or "p = i" in q):
        resistance, current = float(m.group(1)), float(m.group(2))
        expected = current ** 2 * resistance
        if _answer_has_number(a, expected):
            return _result("correct", 1.0, f"Correct power = {expected:g} W.", method="science_formula")

    return None


def try_check_answer(
    question_raw: str,
    student_answer: str,
    subject: str = "",
    expected_answer: str | None = None,
    answer_type: str | None = None,
) -> Optional[Dict[str, Any]]:
    """Return a grading dict when confident; None to defer to AI grader."""
    a = (student_answer or "").strip()
    if not a:
        return _result("incorrect", 0.0, "No answer provided.", method="deterministic_empty")

    if expected_answer:
        keyed = _check_expected_answer(a, expected_answer, answer_type or "text")
        if keyed:
            return keyed

    subject_key = (subject or "").lower()
    q = (question_raw or "").strip()

    if subject_key in ("maths", "mathematics", "math", ""):
        return _check_math_patterns(q, a)

    if subject_key == "science":
        return _check_science_patterns(q, a)

    if subject_key in ("english", "writing_english"):
        return None

    return None
