"""
Nepal CDC-aligned assessment item schema and validation rules.
"""
from __future__ import annotations

import re
from typing import Any

READING_ITEM_TYPES = frozenset({
    "reading_comprehension",
})

CONTEXT_REQUIRED_TYPES = READING_ITEM_TYPES

# Stems that imply a passage/story must be present
CONTEXT_REFERENCE_PATTERNS = (
    r"\bread the (?:story|passage|text|poem|letter|article|paragraph)\b",
    r"\bread (?:it|them) again\b",
    r"\baccording to the passage\b",
    r"\bin the (?:story|passage|text)\b",
    r"\bthe author\b",
    r"\bthe narrator\b",
    r"\bwhy did (?:he|she|they|the character)\b",
)

WRITING_ITEM_TYPES = frozenset({
    "guided_writing",
    "functional_writing",
    "essay_outline",
})

RUBRIC_ITEM_TYPES = WRITING_ITEM_TYPES


def normalize_item(raw: dict[str, Any], defaults: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge raw item dict with defaults and normalize field names."""
    base = dict(defaults or {})
    base.update(raw)
    stem = (base.get("stem") or base.get("text") or base.get("question") or "").strip()
    item_type = base.get("item_type") or base.get("type") or "short_answer"
    requires_context = base.get("requires_context")
    if requires_context is None:
        requires_context = item_type in CONTEXT_REQUIRED_TYPES

    return {
        "id": base.get("id"),
        "stem": stem,
        "text": stem,
        "item_type": item_type,
        "domain": base.get("domain"),
        "section": base.get("section"),
        "cognitive_level": base.get("cognitive_level", "comprehension"),
        "learning_outcome_id": base.get("learning_outcome_id"),
        "requires_context": bool(requires_context),
        "context_text": (base.get("context_text") or "").strip() or None,
        "context_id": base.get("context_id"),
        "context_source": base.get("context_source"),
        "expected_answer": base.get("expected_answer"),
        "answer_type": base.get("answer_type", "short_answer"),
        "marks": int(base.get("marks") or 1),
        "options": base.get("options"),
        "rubric": base.get("rubric"),
        "difficulty": base.get("difficulty"),
    }


def validate_item(item: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return (is_valid, error_messages)."""
    errors: list[str] = []
    stem = (item.get("stem") or item.get("text") or "").strip()

    if not stem:
        errors.append("Item missing stem/text.")
        return False, errors

    item_type = item.get("item_type") or item.get("type") or "short_answer"
    requires_context = item.get("requires_context", item_type in CONTEXT_REQUIRED_TYPES)
    context_text = (item.get("context_text") or "").strip()
    lower_stem = stem.lower()

    if requires_context or item_type in CONTEXT_REQUIRED_TYPES:
        if not context_text:
            errors.append(
                f"Reading item requires context_text (passage). Stem: {stem[:60]}..."
            )

    if not context_text:
        for pattern in CONTEXT_REFERENCE_PATTERNS:
            if re.search(pattern, lower_stem):
                errors.append(
                    f"Stem references a passage/story but context_text is missing: "
                    f"'{stem[:80]}'"
                )
                break

    if item_type in RUBRIC_ITEM_TYPES and not item.get("rubric"):
        # Warning-level: still valid but flagged for LLM rubric grading
        pass

    if item.get("domain") and item.get("learning_outcome_id") is None:
        # Soft requirement — not blocking
        pass

    return len(errors) == 0, errors
