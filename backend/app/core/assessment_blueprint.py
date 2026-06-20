"""
Fixed structure for the initial diagnostic battery (v1 base).
Counts are targets; question banks will enforce these in later phases.
"""
from app.core.skills import SkillArea

DIAGNOSTIC_BLUEPRINT: dict[str, dict] = {
    SkillArea.SPEAKING_ENGLISH.value: {
        "label": "Speaking English",
        "estimated_minutes": 15,
        "sections": [
            {"id": "read_aloud", "format": "audio", "count": 2},
            {"id": "picture_description", "format": "audio", "count": 1},
            {"id": "short_answer", "format": "audio", "count": 3},
            {"id": "listening_mcq", "format": "mcq", "count": 5},
        ],
    },
    SkillArea.WRITING_ENGLISH.value: {
        "label": "Writing English",
        "estimated_minutes": 25,
        "sections": [
            {"id": "grammar_correction", "format": "short_answer", "count": 5},
            {"id": "sentence_completion", "format": "short_answer", "count": 5},
            {"id": "paragraph", "format": "essay", "count": 1},
            {"id": "essay", "format": "essay", "count": 1},
        ],
    },
    SkillArea.MATHEMATICS.value: {
        "label": "Mathematics",
        "estimated_minutes": 30,
        "sections": [
            {"id": "topic_mcq", "format": "mcq", "count_per_topic": 4},
            {"id": "topic_short", "format": "short_answer", "count_per_topic": 2},
        ],
    },
    SkillArea.SCIENCE.value: {
        "label": "Science",
        "estimated_minutes": 30,
        "sections": [
            {"id": "topic_mcq", "format": "mcq", "count_per_topic": 4},
            {"id": "topic_short", "format": "short_answer", "count_per_topic": 2},
        ],
    },
}
