"""
Curated free learning resources mapped to Nepal CDC chapters.
Only URLs from resource_index.yaml — validated live before serving.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from app.core.config import settings
from app.core.curriculum import (
    ROADMAP_HOURS_BY_WEAKNESS,
    normalize_subject_key,
)
from app.services.resource_resolver import get_resource_resolver
from app.services.resource_validator import get_resource_validator

INDEX_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "resource_index.yaml"

PROVIDER_LABELS = {
    "khan_academy": "Khan Academy",
    "youtube": "YouTube",
    "ncert": "NCERT",
    "openstax": "OpenStax",
}

STUDY_STEPS_BY_WEAKNESS = {
    "severe": [
        "Re-read the Nepal CDC textbook section for this topic from the beginning.",
        "Watch the verified tutorial below — pause and write down key definitions.",
        "Solve 5 basic worked examples before attempting exam-style questions.",
    ],
    "moderate": [
        "Review your incorrect answers and identify the exact step where you went wrong.",
        "Watch one tutorial below and redo similar practice problems.",
        "Check units, formulas, and Nepal-specific context (Rs., %, cm).",
    ],
    "mild": [
        "Skim the topic summary and attempt 3 mixed practice questions.",
        "Use the resources below to close small gaps before your next assessment.",
    ],
}

SUBJECT_INDEX_KEY = {
    "maths": "mathematics",
    "mathematics": "mathematics",
    "math": "mathematics",
    "science": "science",
    "english": "writing_english",
    "writing_english": "writing_english",
}


class LearningResourceService:
    def __init__(self):
        self._index: Dict[str, Any] = {}
        self._resolver = get_resource_resolver()
        self._validator = get_resource_validator()
        self._load()

    def _load(self) -> None:
        if not INDEX_PATH.exists():
            self._index = {}
            return
        with open(INDEX_PATH, encoding="utf-8") as f:
            self._index = yaml.safe_load(f) or {}

    def _subject_topics(self, subject: str) -> Dict[str, Any]:
        key = SUBJECT_INDEX_KEY.get(normalize_subject_key(subject), normalize_subject_key(subject))
        return self._index.get(key, {}) or {}

    def _available_topic_keys(self, subject: str) -> set[str]:
        return {k for k in self._subject_topics(subject) if not k.startswith("_")}

    def get_chapter_resources(
        self,
        subject: str,
        chapter: str,
        *,
        domain: str | None = None,
        learning_outcome_id: str | None = None,
        max_resources: int = 3,
    ) -> List[Dict[str, Any]]:
        topics = self._subject_topics(subject)
        available = self._available_topic_keys(subject)

        topic_key, confidence, match_reason = self._resolver.resolve_topic_key(
            subject,
            chapter,
            domain=domain,
            learning_outcome_id=learning_outcome_id,
            available_topics=available,
        )

        raw_resources: list[dict] = []
        match_label = "default"

        if topic_key and confidence >= self._resolver.MIN_CONFIDENCE:
            entry = topics.get(topic_key, {})
            raw_resources = list(entry.get("resources") or [])
            match_label = f"{topic_key} ({match_reason})"
        else:
            raw_resources = list(topics.get("_default", {}).get("resources") or [])
            match_label = f"default (no match for '{chapter}')"

        validate_live = getattr(settings, "RESOURCE_URL_VALIDATION", True)
        validated = self._validator.filter_resources(raw_resources, validate_live=validate_live)

        # If topic match yielded all broken links, try default as secondary
        if not validated and topic_key:
            fallback = self._validator.filter_resources(
                list(topics.get("_default", {}).get("resources") or []),
                validate_live=validate_live,
            )
            validated = fallback
            match_label = f"default_fallback (topic {topic_key} links unavailable)"

        formatted = [self._format_resource(r, chapter, match_label) for r in validated[:max_resources]]
        return formatted

    @staticmethod
    def _format_resource(raw: dict, chapter: str, match_reason: str) -> Dict[str, Any]:
        provider = raw.get("provider", "other")
        title = raw.get("title", "Learning resource")
        if raw.get("verified_title") and provider == "youtube":
            title = raw["verified_title"]

        return {
            "title": title,
            "url": raw.get("url", ""),
            "provider": provider,
            "provider_label": PROVIDER_LABELS.get(provider, provider.replace("_", " ").title()),
            "type": raw.get("type", "tutorial"),
            "description": raw.get("description", ""),
            "estimated_time_minutes": raw.get("estimated_time_minutes", 15),
            "chapter": chapter,
            "topic_match": match_reason,
            "url_verified": raw.get("url_verified", False),
        }

    def build_study_plan(
        self,
        subject: str,
        chapter_analysis: Dict[str, Any],
        grade: int = 10,
        *,
        domain_analysis: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        weak_chapters: List[Dict[str, Any]] = []
        all_resources: List[Dict[str, Any]] = []
        seen_urls: set[str] = set()

        domain_analysis = domain_analysis or {}
        sorted_chapters = sorted(
            chapter_analysis.items(),
            key=lambda x: x[1].get("accuracy_percentage", 0),
        )

        for chapter, data in sorted_chapters:
            accuracy = data.get("accuracy_percentage", 100)
            weakness = data.get("weakness_level", "none")
            if weakness == "none" and accuracy >= 85:
                continue

            domain = data.get("domain")
            if not domain:
                # Infer domain from domain_analysis if chapter is a section title
                for dom, dom_data in domain_analysis.items():
                    if dom_data.get("accuracy_percentage", 100) < 85:
                        domain = dom
                        break

            resources = self.get_chapter_resources(
                subject,
                chapter,
                domain=domain,
                learning_outcome_id=data.get("learning_outcome_id"),
            )

            steps = STUDY_STEPS_BY_WEAKNESS.get(
                weakness if weakness in STUDY_STEPS_BY_WEAKNESS else "moderate",
                STUDY_STEPS_BY_WEAKNESS["moderate"],
            )

            entry = {
                "chapter": chapter,
                "accuracy_percentage": accuracy,
                "weakness_level": weakness,
                "priority": {"severe": 1, "moderate": 2, "mild": 3}.get(weakness, 4),
                "estimated_time_hours": ROADMAP_HOURS_BY_WEAKNESS.get(weakness, 2.0),
                "study_steps": steps,
                "recommended_resources": resources,
            }
            weak_chapters.append(entry)

            for res in resources:
                url = res.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_resources.append(res)

        weak_chapters.sort(key=lambda x: x["priority"])

        return {
            "grade": grade,
            "subject": subject,
            "weak_topics": weak_chapters,
            "all_resources": all_resources[:12],
            "message": (
                f"Focus on {len(weak_chapters)} topic(s) below. "
                "Each link is topic-matched and verified before display."
                if weak_chapters
                else "Strong performance — use resources below for optional revision."
            ),
        }


def attach_study_resources(
    evaluation: Dict[str, Any],
    subject: str,
    grade: int = 10,
    answers: List[dict] | None = None,
) -> Dict[str, Any]:
    """Add study plan and per-chapter resources to an evaluation result."""
    svc = get_learning_resource_service()
    chapter_analysis = evaluation.get("chapter_analysis") or {}
    domain_analysis = evaluation.get("domain_analysis") or {}
    overall = evaluation.get("overall_analysis") or {}
    if not domain_analysis:
        domain_analysis = overall.get("domain_analysis") or {}

    # Enrich chapter entries with domain hints from answers if present
    answer_list = answers or evaluation.get("answers") or []
    chapter_domains: dict[str, list[str]] = {}
    for ans in answer_list:
        ch = ans.get("chapter") or "General"
        dom = ans.get("domain")
        if dom:
            chapter_domains.setdefault(ch, []).append(dom)

    enriched_analysis = {}
    for chapter, data in chapter_analysis.items():
        entry = dict(data)
        doms = chapter_domains.get(chapter, [])
        if doms:
            entry["domain"] = max(set(doms), key=doms.count)
        enriched_analysis[chapter] = entry

    study_plan = svc.build_study_plan(
        subject, enriched_analysis, grade, domain_analysis=domain_analysis
    )

    for chapter, data in enriched_analysis.items():
        if data.get("accuracy_percentage", 100) < 85 or data.get("weakness_level") != "none":
            data["recommended_resources"] = svc.get_chapter_resources(
                subject,
                chapter,
                domain=data.get("domain"),
                learning_outcome_id=data.get("learning_outcome_id"),
            )
            if not data.get("study_steps"):
                weakness = data.get("weakness_level", "moderate")
                data["study_steps"] = STUDY_STEPS_BY_WEAKNESS.get(
                    weakness, STUDY_STEPS_BY_WEAKNESS["moderate"]
                )

    evaluation["chapter_analysis"] = enriched_analysis
    overall = evaluation.setdefault("overall_analysis", {})
    overall["study_plan"] = study_plan
    evaluation["recommended_resources"] = study_plan.get("all_resources", [])
    return evaluation


_service: LearningResourceService | None = None


def get_learning_resource_service() -> LearningResourceService:
    global _service
    if _service is None:
        _service = LearningResourceService()
    return _service
