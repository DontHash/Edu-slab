"""Shared filesystem paths for the backend."""
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
ASSESSMENTS_DIR = BACKEND_ROOT / "assessments"
ADAPTIVE_SESSIONS_DIR = ASSESSMENTS_DIR / "adaptive"
DATA_DIR = BACKEND_ROOT / "data"
QUESTION_DATA_DIR = BACKEND_ROOT.parent / "python_RAG" / "data"
