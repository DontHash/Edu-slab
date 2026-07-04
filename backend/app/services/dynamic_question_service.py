"""
Dynamic question generation from templates.

Loads YAML registries + infers templates from structured bank items,
then generates validated pool items with swapped parameters.
"""
from __future__ import annotations

import random
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.core.config import settings
from app.core.curriculum import normalize_subject_key
from app.core.paths import DATA_DIR
from app.core.question_templates import GenerativeTemplate, generative_template_from_item
from app.services.generators.english_grammar import EnglishGrammarGenerator
from app.services.generators.math_equations import MathEquationGenerator

TEMPLATES_DIR = DATA_DIR / "templates"


class DynamicQuestionService:
  def __init__(self, templates_dir: Path = TEMPLATES_DIR):
    self.templates_dir = templates_dir
    self._english_gen = EnglishGrammarGenerator()
    self._math_gen = MathEquationGenerator()

  def load_yaml_templates(self, subject_key: str, grade: int) -> list[GenerativeTemplate]:
    files = {
      "english": "english_grammar.yaml",
      "writing_english": "english_grammar.yaml",
      "maths": "mathematics.yaml",
      "mathematics": "mathematics.yaml",
    }
    fname = files.get(subject_key)
    if not fname:
      return []
    path = self.templates_dir / fname
    if not path.exists():
      return []
    with open(path, encoding="utf-8") as f:
      data = yaml.safe_load(f) or {}
    out: list[GenerativeTemplate] = []
    for raw in data.get("templates") or []:
      if int(raw.get("grade", grade)) != grade:
        continue
      out.append(
        GenerativeTemplate(
          template_id=raw["template_id"],
          kind=raw["kind"],
          subject=subject_key,
          grade=grade,
          domain=raw.get("domain", "grammar_vocabulary"),
          item_type=raw.get("item_type", "grammar_correction"),
          cognitive_level=raw.get("cognitive_level", "application"),
          learning_outcome_id=raw.get("learning_outcome_id"),
          marks=int(raw.get("marks") or 2),
          difficulty=int(raw.get("difficulty") or 2),
          seed=raw.get("seed") or {},
          slots=raw.get("slots") or {},
          variants=raw.get("variants") or [],
          section=raw.get("section"),
          chapter=raw.get("chapter"),
        )
      )
    return out

  def extract_templates_from_items(
    self, items: list[dict], grade: int, subject_key: str
  ) -> list[GenerativeTemplate]:
    """Build templates from structured bank items (explicit block or inferred)."""
    seen: set[str] = set()
    templates: list[GenerativeTemplate] = []

    for item in items:
      explicit = generative_template_from_item(item, grade, subject_key)
      if explicit:
        if explicit.template_id not in seen:
          seen.add(explicit.template_id)
          templates.append(explicit)
        continue

      stem = item.get("stem") or item.get("text") or ""
      if subject_key in ("english", "writing_english"):
        inferred = EnglishGrammarGenerator.infer_template_from_stem(
          stem, item, grade, subject_key
        )
        if inferred and inferred.template_id not in seen:
          seen.add(inferred.template_id)
          templates.append(inferred)
      elif subject_key in ("maths", "mathematics"):
        inferred = self._infer_math_template(stem, item, grade, subject_key)
        if inferred and inferred.template_id not in seen:
          seen.add(inferred.template_id)
          templates.append(inferred)

    return templates

  @staticmethod
  def _infer_math_template(stem: str, item: dict, grade: int, subject_key: str) -> GenerativeTemplate | None:
    lower = stem.lower()
    if "solve for" in lower and "²" not in stem and "x²" not in lower:
      return GenerativeTemplate(
        template_id=f"inferred_linear_{grade}",
        kind="linear_equation",
        subject=subject_key,
        grade=grade,
        domain=item.get("domain", "number_algebra"),
        item_type=item.get("item_type", "numeric"),
        learning_outcome_id=item.get("learning_outcome_id"),
        marks=int(item.get("marks") or 2),
        difficulty=2,
      )
    if "factorize" in lower:
      return GenerativeTemplate(
        template_id=f"inferred_factorize_{grade}",
        kind="factorize",
        subject=subject_key,
        grade=grade,
        domain=item.get("domain", "number_algebra"),
        item_type="numeric",
        learning_outcome_id=item.get("learning_outcome_id"),
        marks=int(item.get("marks") or 2),
      )
    if "mean of" in lower:
      return GenerativeTemplate(
        template_id=f"inferred_mean_{grade}",
        kind="arithmetic_mean",
        subject=subject_key,
        grade=grade,
        domain=item.get("domain", "data"),
        item_type="numeric",
        learning_outcome_id=item.get("learning_outcome_id"),
      )
    return None

  def generate_from_template(
    self,
    template: GenerativeTemplate,
    *,
    difficulty: int | None = None,
    rng: random.Random | None = None,
  ) -> dict[str, Any] | None:
    diff = difficulty or template.difficulty
    if template.kind in ("grammar_transform", "grammar_error"):
      gen = EnglishGrammarGenerator(rng=rng)
      return gen.instantiate(template, difficulty=diff)
    if template.kind in (
      "linear_equation",
      "linear_two_step",
      "quadratic_equation",
      "factorize",
      "arithmetic_mean",
      "percentage_word",
    ):
      gen = MathEquationGenerator(rng=rng)
      return gen.instantiate(template, difficulty=diff)
    return None

  def generate_variants(
    self,
    template: GenerativeTemplate,
    count: int,
    *,
    difficulty: int | None = None,
    seed: int | None = None,
  ) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    results: list[dict[str, Any]] = []
    seen_stems: set[str] = set()
    attempts = 0
    max_attempts = count * 8

    while len(results) < count and attempts < max_attempts:
      attempts += 1
      item = self.generate_from_template(template, difficulty=difficulty, rng=rng)
      if not item:
        continue
      stem = item.get("stem", "")
      if stem in seen_stems:
        continue
      seen_stems.add(stem)
      results.append(item)

    return results

  def generate_pool(
    self,
    subject: str,
    grade: int,
    *,
    difficulty: int | None = None,
    structured_items: list[dict] | None = None,
    variants_per_template: int | None = None,
  ) -> list[dict[str, Any]]:
    if not settings.DYNAMIC_QUESTIONS_ENABLED:
      return []

    subject_key = normalize_subject_key(subject)
    if subject_key == "science":
      return []

    per_template = variants_per_template or settings.DYNAMIC_VARIANTS_PER_TEMPLATE
    templates = self.load_yaml_templates(subject_key, grade)
    templates.extend(
      self.extract_templates_from_items(structured_items or [], grade, subject_key)
    )

    # Deduplicate by template_id
    by_id: dict[str, GenerativeTemplate] = {}
    for t in templates:
      by_id[t.template_id] = t

    pool: list[dict[str, Any]] = []
    session_seed = random.randint(0, 2**31)

    for i, template in enumerate(by_id.values()):
      diff = difficulty or template.difficulty
      # Scale difficulty for harder transforms / equation types
      if diff and template.kind == "quadratic_equation":
        diff = max(diff, 3)

      variants = self.generate_variants(
        template,
        per_template,
        difficulty=diff,
        seed=session_seed + i,
      )
      pool.extend(variants)

    return pool

  def list_templates(self, subject: str, grade: int) -> list[dict[str, Any]]:
    subject_key = normalize_subject_key(subject)
    templates = self.load_yaml_templates(subject_key, grade)
    return [t.to_dict() for t in templates]


@lru_cache(maxsize=1)
def get_dynamic_question_service() -> DynamicQuestionService:
  return DynamicQuestionService()
