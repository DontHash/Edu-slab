"""
Load CDC-aligned curriculum metadata: domains, learning outcomes, spec grids.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.core.paths import DATA_DIR

CURRICULUM_DIR = DATA_DIR / "curriculum"


class CurriculumMetadataService:
    def __init__(self, root: Path = CURRICULUM_DIR):
        self.root = root
        self._domains: dict[str, Any] = {}
        self._outcomes: dict[str, Any] = {}
        self._grids: dict[str, Any] = {}
        self._load()

    def _load_yaml(self, name: str) -> dict:
        path = self.root / name
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load(self) -> None:
        self._domains = self._load_yaml("domains.yaml")
        self._outcomes = self._load_yaml("learning_outcomes.yaml")
        self._grids = self._load_yaml("spec_grids.yaml")

    def get_spec_grid(self, subject: str, grade: int) -> dict[str, Any] | None:
        subject_key = self._subject_key(subject)
        return (self._grids.get(subject_key) or {}).get(f"grade_{grade}")

    def get_learning_outcomes(self, subject: str, grade: int) -> dict[str, list]:
        subject_key = self._subject_key(subject)
        grade_data = (self._outcomes.get(subject_key) or {}).get(f"grade_{grade}") or {}
        return grade_data

    def get_domains(self, subject: str) -> dict[str, Any]:
        subject_key = self._subject_key(subject)
        return self._domains.get(subject_key) or {}

    def get_proficiency_bands(self) -> list[dict]:
        return self._domains.get("proficiency_bands") or []

    def proficiency_band_for_score(self, pct: float) -> dict:
        for band in self.get_proficiency_bands():
            if pct >= band.get("min_pct", 0):
                return band
        return {"band": "intensive_support", "label": "Needs Intensive Support"}

    def curriculum_summary(self, grade: int) -> dict[str, Any]:
        summary: dict[str, Any] = {"grade": grade, "subjects": {}}
        for subject in ("english", "mathematics", "science"):
            grid = self.get_spec_grid(subject, grade)
            if grid:
                summary["subjects"][subject] = {
                    "spec_grid": grid,
                    "domains": self.get_domains(subject),
                    "learning_outcomes": self.get_learning_outcomes(subject, grade),
                }
        summary["proficiency_bands"] = self.get_proficiency_bands()
        summary["cognitive_levels"] = self._domains.get("cognitive_levels") or {}
        summary["assessment_guidelines"] = self._load_yaml("assessment_guidelines.yaml")
        return summary

    @staticmethod
    def _subject_key(subject: str) -> str:
        s = (subject or "").lower()
        if s in ("maths", "math", "mathematics"):
            return "mathematics"
        if s in ("english", "writing_english"):
            return "english"
        return s


@lru_cache(maxsize=1)
def get_curriculum_metadata() -> CurriculumMetadataService:
    return CurriculumMetadataService()
