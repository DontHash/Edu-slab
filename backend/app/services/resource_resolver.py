"""
Strict topic → resource matching for Nepal CDC diagnostics.

Uses domain keys, chapter aliases, and tag overlap — never fuzzy-guesses
unrelated topics. Falls back to subject default only below confidence threshold.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from app.core.curriculum import normalize_subject_key, resolve_chapter_alias

# Assessment domain (structured banks) → resource_index topic key
DOMAIN_TOPIC_MAP: dict[str, dict[str, str]] = {
    "mathematics": {
        "number_algebra": "Linear Equations",
        "geometry": "Trigonometry",
        "data": "Statistics",
        "problem_solving": "Statistics",
    },
    "science": {
        "knowledge": "Cell - The Unit of Life",
        "understanding": "Motion and Force",
        "application": "Electricity and Magnetism",
    },
    "writing_english": {
        "reading": "Comprehension",
        "grammar_vocabulary": "Grammar",
        "writing": "Essay Writing",
    },
    "english": {
        "reading": "Comprehension",
        "grammar_vocabulary": "Grammar",
        "writing": "Essay Writing",
    },
}

# Section titles from structured banks → topic key
SECTION_TITLE_MAP: dict[str, dict[str, str]] = {
    "mathematics": {
        "number & algebra": "Linear Equations",
        "number and algebra": "Linear Equations",
        "geometry": "Trigonometry",
        "geometry & trigonometry": "Trigonometry",
        "data & application": "Statistics",
        "statistics & application": "Statistics",
        "algebra": "Linear Equations",
        "mensuration": "Mensuration",
    },
    "science": {
        "life science": "Cell - The Unit of Life",
        "physical science": "Motion and Force",
        "application": "Electricity and Magnetism",
    },
    "writing_english": {
        "reading comprehension": "Comprehension",
        "grammar & vocabulary": "Grammar",
        "grammar and vocabulary": "Grammar",
        "writing": "Essay Writing",
    },
    "english": {
        "reading comprehension": "Comprehension",
        "grammar & vocabulary": "Grammar",
        "writing": "Essay Writing",
    },
}

# Learning outcome ID prefix → topic
LO_PREFIX_MAP: dict[str, str] = {
    "EN_G8_LO_READ": "Comprehension",
    "EN_G10_LO_READ": "Comprehension",
    "EN_G8_LO_GV": "Grammar",
    "EN_G10_LO_GV": "Grammar",
    "EN_G8_LO_WRITE": "Essay Writing",
    "EN_G10_LO_WRITE": "Essay Writing",
    "MA_G8_LO_ALG": "Linear Equations",
    "MA_G10_LO_ALG": "Quadratic Equations",
    "MA_G8_LO_GEO": "Trigonometry",
    "MA_G10_LO_GEO": "Trigonometry",
    "MA_G8_LO_DATA": "Statistics",
    "MA_G10_LO_DATA": "Statistics",
    "SC_G8_LO_K": "Cell - The Unit of Life",
    "SC_G10_LO_K": "Heredity",
    "SC_G8_LO_U": "Motion and Force",
    "SC_G10_LO_U": "Chemical Reaction",
    "SC_G8_LO_A": "Electricity and Magnetism",
    "SC_G10_LO_A": "Electricity and Magnetism",
}

# Exact chapter name → topic (assessment chapter labels)
CHAPTER_EXACT_MAP: dict[str, dict[str, str]] = {
    "mathematics": {
        "number & algebra": "Linear Equations",
        "geometry": "Trigonometry",
        "data & application": "Statistics",
        "set theory": "Set Theory",
        "compound interest": "Compound Interest",
        "quadratic equations": "Quadratic Equations",
        "linear equations": "Linear Equations",
        "algebra": "Linear Equations",
        "trigonometry": "Trigonometry",
        "mensuration": "Mensuration",
        "statistics": "Statistics",
        "probability": "Probability",
    },
    "science": {
        "life science": "Cell - The Unit of Life",
        "physical science": "Motion and Force",
        "application": "Electricity and Magnetism",
        "motion and force": "Motion and Force",
        "electricity and magnetism": "Electricity and Magnetism",
        "cell - the unit of life": "Cell - The Unit of Life",
        "heredity": "Heredity",
        "chemical reaction": "Chemical Reaction",
        "heat": "Heat",
    },
    "writing_english": {
        "grammar & vocabulary": "Grammar",
        "reading comprehension": "Comprehension",
        "writing": "Essay Writing",
        "grammar": "Grammar",
        "comprehension": "Comprehension",
        "essay writing": "Essay Writing",
        "vocabulary": "Vocabulary",
    },
}


class ResourceResolver:
    MIN_CONFIDENCE = 0.55

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

    def resolve_topic_key(
        self,
        subject: str,
        chapter: str,
        *,
        domain: str | None = None,
        learning_outcome_id: str | None = None,
        available_topics: set[str] | None = None,
    ) -> tuple[Optional[str], float, str]:
        """
        Return (topic_key, confidence 0-1, match_reason).
        Returns (None, 0, reason) if no confident match.
        """
        subject_key = normalize_subject_key(subject)
        index_key = {
            "maths": "mathematics",
            "math": "mathematics",
            "english": "writing_english",
        }.get(subject_key, subject_key)

        chapter_raw = (chapter or "").strip()
        chapter_alias = resolve_chapter_alias(subject, chapter_raw)
        norm_chapter = self._normalize(chapter_raw)
        norm_alias = self._normalize(chapter_alias)

        available = available_topics or set()

        def _ok(key: str | None) -> tuple[Optional[str], float, str]:
            if not key:
                return None, 0.0, "no_key"
            if available and key not in available:
                return None, 0.0, f"key_not_in_index:{key}"
            return key, 1.0, "exact"

        # 1. Learning outcome ID (highest precision)
        if learning_outcome_id:
            for prefix, topic in LO_PREFIX_MAP.items():
                if learning_outcome_id.startswith(prefix):
                    key, conf, reason = _ok(topic)
                    if key:
                        return key, conf, f"lo:{learning_outcome_id}"

        # 2. Explicit domain from structured assessment
        if domain:
            domain_key = DOMAIN_TOPIC_MAP.get(index_key, {}).get(domain)
            if domain_key:
                key, conf, reason = _ok(domain_key)
                if key:
                    return key, 0.95, f"domain:{domain}"

        # 3. Exact chapter maps
        exact_map = CHAPTER_EXACT_MAP.get(index_key, {})
        for candidate in (norm_chapter, norm_alias):
            if candidate in exact_map:
                key, conf, reason = _ok(exact_map[candidate])
                if key:
                    return key, 0.9, f"chapter_exact:{candidate}"

        # 4. Section title map
        section_map = SECTION_TITLE_MAP.get(index_key, {})
        for candidate in (norm_chapter, norm_alias):
            if candidate in section_map:
                key, conf, reason = _ok(section_map[candidate])
                if key:
                    return key, 0.88, f"section:{candidate}"

        # 5. Direct topic key match in index
        if chapter_alias in (available or {chapter_alias}):
            if not available or chapter_alias in available:
                return chapter_alias, 0.85, "alias_direct"

        # 6. Strict word overlap (require 2+ shared words AND >60% of topic key words)
        if available:
            best_key = None
            best_score = 0.0
            for topic_key in available:
                if topic_key.startswith("_"):
                    continue
                norm_key = self._normalize(topic_key)
                key_words = set(norm_key.split())
                chap_words = set(norm_chapter.split()) | set(norm_alias.split())
                if not key_words:
                    continue
                overlap = key_words & chap_words
                score = len(overlap) / len(key_words)
                if len(overlap) >= 2 and score >= 0.6 and score > best_score:
                    best_score = score
                    best_key = topic_key
            if best_key and best_score >= self.MIN_CONFIDENCE:
                return best_key, best_score, f"word_overlap:{best_score:.2f}"

        return None, 0.0, "no_confident_match"


_resolver: ResourceResolver | None = None


def get_resource_resolver() -> ResourceResolver:
    global _resolver
    if _resolver is None:
        _resolver = ResourceResolver()
    return _resolver
