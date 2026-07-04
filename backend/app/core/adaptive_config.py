"""Adaptive assessment settings."""
ADAPTIVE_TOTAL_QUESTIONS = 10
DIFFICULTY_MIN = 1
DIFFICULTY_MAX = 3
DIFFICULTY_LABELS = {1: "easy", 2: "medium", 3: "hard"}
STARTING_DIFFICULTY = 2  # fallback when grade unknown


def starting_difficulty_for_grade(grade: int) -> int:
    """Map Nepal CDC grade (6–10) to initial easy/medium/hard level."""
    g = max(6, min(10, int(grade)))
    if g <= 7:
        return 1
    if g <= 9:
        return 2
    return 3

# Maths: exclude pure theory prompts
MATH_THEORY_PATTERNS = (
    "define ",
    "what is ",
    "what are ",
    "explain ",
    "describe ",
    "state the ",
    "write the formula",
    "prove ",
    "draw a ",
    "draw ",
    "represent the relation",
    "distinguish between",
    "list the ",
    "name the ",
)

MATH_COMPUTE_PATTERNS = (
    "find ",
    "calculate ",
    "convert ",
    "solve ",
    "simplify ",
    "evaluate ",
    "how many ",
    "how much ",
    "if ",
    "a person ",
    "a student ",
    "in a ",
    "rs.",
    "rs ",
    "%",
)
