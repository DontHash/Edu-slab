"""
Nepal CDC-aligned curriculum configuration.

Source material: python_RAG/data (Mathematics & Science grade JSON, English JSONL).
Framework: Nepal National Curriculum — Basic Level (Grades 6–10).
"""
from app.core.skills import LEGACY_SUBJECT_TO_SKILL, SkillArea

CURRICULUM_FRAMEWORK = "Nepal CDC National Curriculum (Grades 6–10)"
CURRICULUM_BOARD = "CDC Nepal"
SUPPORTED_GRADES = [6, 7, 8, 9, 10]

# Legacy UI subject keys → skill area + file prefix
SUBJECT_CONFIG: dict[str, dict] = {
    "maths": {
        "skill_area": SkillArea.MATHEMATICS.value,
        "label": "Mathematics",
        "file_pattern": "MathematicsGrade{grade}.json",
    },
    "mathematics": {
        "skill_area": SkillArea.MATHEMATICS.value,
        "label": "Mathematics",
        "file_pattern": "MathematicsGrade{grade}.json",
    },
    "science": {
        "skill_area": SkillArea.SCIENCE.value,
        "label": "Science and Technology",
        "file_pattern": "ScienceGrade{grade}.json",
    },
    "english": {
        "skill_area": SkillArea.WRITING_ENGLISH.value,
        "label": "English",
        "source": "jsonl",
        "file_pattern": "EnglishGrade{grade}.json",
    },
    "writing_english": {
        "skill_area": SkillArea.WRITING_ENGLISH.value,
        "label": "English (Writing)",
        "source": "jsonl",
        "file_pattern": "EnglishGrade{grade}.json",
    },
}

# Standardized diagnostic defaults (one question per chapter for initial battery)
DEFAULT_QUESTIONS_PER_CHAPTER = 1
MAX_QUESTIONS_PER_CHAPTER = 5

# Nepal CDC-style weakness bands (accuracy % per topic/chapter)
WEAKNESS_FROM_ACCURACY = [
    (85, "none"),
    (70, "mild"),
    (50, "moderate"),
    (0, "severe"),
]

# Estimated Nepal grade level from overall diagnostic score (0–100)
GRADE_LEVEL_THRESHOLDS = [
    (85, 10),
    (70, 9),
    (55, 8),
    (40, 7),
    (0, 6),
]

# Roadmap study time by weakness severity (hours per chapter)
ROADMAP_HOURS_BY_WEAKNESS = {
    "severe": 4.0,
    "moderate": 2.5,
    "mild": 1.5,
    "none": 1.0,
}

ROADMAP_STEP_MINUTES_BY_WEAKNESS = {
    "severe": 30,
    "moderate": 25,
    "mild": 20,
    "none": 15,
}

# Map curriculum chapter names → resource_index.yaml topic keys
CHAPTER_ALIASES: dict[str, dict[str, str]] = {
    "mathematics": {
        "Mensuration - Area": "Mensuration",
        "Mensuration - Volume and Surface Area": "Mensuration",
        "Ratio, Proportion and Variation": "Linear Equations",
        "Geometric Sequences": "Algebraic Expressions",
        "Triangles and Similarity": "Trigonometry",
        "Shares and Dividends": "Money Exchange and Tax",
        "Polygons": "Mensuration",
        "Algebraic Expressions": "Linear Equations",
    },
    "science": {
        "Physiological Structure and Life Process": "Heredity",
        "Classification of Living Beings": "Heredity",
        "Living Beings": "Living Beings",
        "Cell - The Unit of Life": "Cell - The Unit of Life",
        "Reproduction in Living Beings": "Reproduction in Living Beings",
        "Honey Bee": "Heredity",
        "Nature and Environment": "Heat",
        "Pressure": "Motion and Force",
        "Wave": "Motion and Force",
        "Universe": "Motion and Force",
        "Information and Communication Technology": "Electricity and Magnetism",
        "Gases": "Chemical Reaction",
        "Hydrocarbon and its Compounds": "Chemical Reaction",
        "Chemicals used in Daily Life": "Chemical Reaction",
        "Scientific Learning": "Motion and Force",
    },
    "writing_english": {
        "English Unit Grammar": "Grammar",
        "English Unit Writing": "Essay Writing",
        "English Unit Reading": "Comprehension",
        "Vocabulary": "Vocabulary",
    },
}

# Question filters aligned with Nepal exam style
MATH_EXCLUDE_PATTERNS = ("prove that", "prove ", "show that")
SCIENCE_EXCLUDE_PATTERNS = ("prove that", "prove ", "derive ")


def normalize_subject_key(subject: str) -> str:
    key = (subject or "").strip().lower()
    if key in SUBJECT_CONFIG:
        return key
    return LEGACY_SUBJECT_TO_SKILL.get(key, key)


def weakness_level_for_accuracy(accuracy_pct: float) -> str:
    for threshold, level in WEAKNESS_FROM_ACCURACY:
        if accuracy_pct >= threshold:
            return level
    return "severe"


def estimate_grade_level(final_score: int) -> int:
    """Map overall diagnostic score (0–100) to estimated Nepal grade 6–10."""
    for threshold, grade in GRADE_LEVEL_THRESHOLDS:
        if final_score >= threshold:
            return grade
    return 6


def resolve_chapter_alias(subject: str, chapter: str) -> str:
    """Map a curriculum chapter name to a resource_index topic key when possible."""
    subject_key = SUBJECT_INDEX_KEY_FOR_ALIASES.get(normalize_subject_key(subject), "mathematics")
    aliases = CHAPTER_ALIASES.get(subject_key, {})
    return aliases.get(chapter, chapter)


def infer_domain_from_chapter(subject: str, chapter: str) -> str | None:
    """Map legacy chapter titles to CDC/CBSE-style assessment domains."""
    subject_key = normalize_subject_key(subject)
    name = (chapter or "").lower()

    if subject_key in ("english", "writing_english"):
        if "read" in name or "comprehension" in name:
            return "reading"
        if "grammar" in name or "vocabulary" in name:
            return "grammar_vocabulary"
        if "writ" in name or "essay" in name:
            return "writing"
        return None

    if subject_key in ("maths", "mathematics"):
        if any(k in name for k in ("algebra", "linear", "equation", "number", "ratio")):
            return "number_algebra"
        if any(k in name for k in ("geometry", "mensuration", "triangle", "circle", "trigon")):
            return "geometry"
        if any(k in name for k in ("stat", "data", "probability")):
            return "data"
        return "number_algebra"

    if subject_key == "science":
        if any(k in name for k in ("cell", "life", "heredity", "reproduction", "plant", "animal")):
            return "knowledge"
        if any(k in name for k in ("force", "motion", "heat", "wave", "sound", "light", "chemical", "gas")):
            return "understanding"
        return "application"

    return None


SUBJECT_INDEX_KEY_FOR_ALIASES = {
    "maths": "mathematics",
    "mathematics": "mathematics",
    "science": "science",
    "english": "writing_english",
    "writing_english": "writing_english",
}
