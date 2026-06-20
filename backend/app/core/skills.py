"""
Canonical skill areas for the diagnostic assessment platform.
"""
from enum import Enum


class SkillArea(str, Enum):
    SPEAKING_ENGLISH = "speaking_english"
    WRITING_ENGLISH = "writing_english"
    MATHEMATICS = "mathematics"
    SCIENCE = "science"


SKILL_AREAS: list[str] = [area.value for area in SkillArea]

SKILL_LABELS: dict[str, str] = {
    SkillArea.SPEAKING_ENGLISH: "Speaking English",
    SkillArea.WRITING_ENGLISH: "Writing English",
    SkillArea.MATHEMATICS: "Mathematics",
    SkillArea.SCIENCE: "Science",
}

# Maps legacy RAG subject names to skill areas (transitional)
LEGACY_SUBJECT_TO_SKILL: dict[str, str] = {
    "maths": SkillArea.MATHEMATICS.value,
    "mathematics": SkillArea.MATHEMATICS.value,
    "science": SkillArea.SCIENCE.value,
    "english": SkillArea.WRITING_ENGLISH.value,
}


def normalize_skill_area(subject: str) -> str:
    key = (subject or "").strip().lower()
    if key in SKILL_AREAS:
        return key
    return LEGACY_SUBJECT_TO_SKILL.get(key, key)
