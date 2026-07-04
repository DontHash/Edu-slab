"""Flatten structured student answers (JSON) to plain text for grading."""
from __future__ import annotations

import json
from typing import Any


def flatten_student_answer(answer: str | None) -> str:
    """
    Convert structured_v1 JSON answers to readable plain text for AI/rule graders.
    Returns the original string if not structured.
    """
    if not answer:
        return ""
    text = answer.strip()
    if not text.startswith("{"):
        return answer

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return answer

    if not isinstance(data, dict) or data.get("v") != 1:
        return answer

    parts: list[str] = []
    working = (data.get("working") or "").strip()
    final = (data.get("final") or "").strip()
    graph = data.get("graph") if isinstance(data.get("graph"), dict) else None

    if working:
        parts.append(f"WORKING:\n{working}")
    if final:
        parts.append(f"FINAL ANSWER:\n{final}")
    if graph and graph.get("image"):
        parts.append("[Student attached a graph or diagram sketch.]")
        caption = (graph.get("caption") or "").strip()
        if caption:
            parts.append(f"GRAPH NOTE: {caption}")

    return "\n\n".join(parts) if parts else answer


def answer_metadata_from_item(item: dict[str, Any]) -> dict[str, Any]:
    """Extract grading fields from an assessment answer item."""
    raw = item.get("answer") or ""
    flat = flatten_student_answer(raw)
    return {
        "answer": flat,
        "answer_raw_structured": raw if raw.strip().startswith("{") else None,
        "question_raw": item.get("question_raw") or item.get("question") or "",
        "expected_answer": item.get("expected_answer"),
        "answer_type": item.get("answer_type"),
    }
