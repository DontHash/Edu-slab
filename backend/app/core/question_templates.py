"""
Generative question template schema.

Structured bank items and YAML registries define slot patterns;
generators instantiate new questions by swapping parameters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerativeTemplate:
    """Blueprint for parameterised question generation."""

    template_id: str
    kind: str  # grammar_transform | grammar_error | linear_equation | quadratic_equation | ...
    subject: str
    grade: int
    domain: str = "grammar_vocabulary"
    item_type: str = "grammar_correction"
    cognitive_level: str = "application"
    learning_outcome_id: str | None = None
    marks: int = 2
    difficulty: int = 2
    # Fixed or pooled seed values
    seed: dict[str, Any] = field(default_factory=dict)
    # Slot definitions: {slot_name: {pool, range, values, ...}}
    slots: dict[str, Any] = field(default_factory=dict)
    # Which transforms / equation kinds to rotate through
    variants: list[str] = field(default_factory=list)
    section: str | None = None
    chapter: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "template_id": self.template_id,
            "kind": self.kind,
            "subject": self.subject,
            "grade": self.grade,
            "domain": self.domain,
            "item_type": self.item_type,
            "cognitive_level": self.cognitive_level,
            "learning_outcome_id": self.learning_outcome_id,
            "marks": self.marks,
            "difficulty": self.difficulty,
            "seed": self.seed,
            "slots": self.slots,
            "variants": self.variants,
            "section": self.section,
            "chapter": self.chapter,
        }


def generative_template_from_item(item: dict[str, Any], grade: int, subject: str) -> GenerativeTemplate | None:
    """Read explicit generative_template block from a structured bank item."""
    block = item.get("generative_template")
    if not isinstance(block, dict):
        return None
    return GenerativeTemplate(
        template_id=block.get("template_id") or f"item_{hash(item.get('stem', ''))}",
        kind=block.get("kind", "grammar_transform"),
        subject=subject,
        grade=grade,
        domain=item.get("domain") or block.get("domain", "grammar_vocabulary"),
        item_type=item.get("item_type") or block.get("item_type", "grammar_correction"),
        cognitive_level=item.get("cognitive_level") or "application",
        learning_outcome_id=item.get("learning_outcome_id"),
        marks=int(item.get("marks") or block.get("marks") or 2),
        difficulty=int(block.get("difficulty") or 2),
        seed=block.get("seed") or {},
        slots=block.get("slots") or {},
        variants=block.get("variants") or block.get("transforms") or [],
        section=item.get("section"),
        chapter=item.get("chapter"),
    )
