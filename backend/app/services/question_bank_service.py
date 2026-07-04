"""
Load standardized questions from the Nepal CDC curriculum knowledge base.
Supports legacy chapter JSON and CDC-aligned structured banks (sections + passages).
"""
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.adaptive_config import (
    MATH_COMPUTE_PATTERNS,
    MATH_THEORY_PATTERNS,
)
from app.core.curriculum import (
    CURRICULUM_BOARD,
    CURRICULUM_FRAMEWORK,
    DEFAULT_QUESTIONS_PER_CHAPTER,
    MATH_EXCLUDE_PATTERNS,
    SCIENCE_EXCLUDE_PATTERNS,
    SUBJECT_CONFIG,
    infer_domain_from_chapter,
    normalize_subject_key,
)
from app.core.item_schema import normalize_item, validate_item
from app.core.paths import QUESTION_DATA_DIR
from app.services.blueprint_assembler import get_blueprint_assembler


class QuestionBankService:
    def __init__(self, data_dir: Path = QUESTION_DATA_DIR):
        self.data_dir = data_dir
        self._validation_log: list[str] = []

    def _stable_id(self, subject: str, grade: int, chapter: str, index: int, text: str) -> str:
        raw = f"{subject}|{grade}|{chapter}|{index}|{text[:80]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _should_include_question(self, subject_key: str, entry: dict) -> bool:
        text = (entry.get("text") or entry.get("stem") or "").strip()
        lower = text.lower()
        if subject_key in ("maths", "mathematics"):
            return not any(p in lower for p in MATH_EXCLUDE_PATTERNS)
        if subject_key == "science":
            return not any(p in lower for p in SCIENCE_EXCLUDE_PATTERNS)
        return len(text) >= 15

    def _parse_structured_bank(self, data: dict) -> List[dict[str, Any]]:
        """Flatten sections/passages into validated pool-ready items."""
        items: list[dict[str, Any]] = []
        grade = int(data.get("grade") or 10)
        subject = normalize_subject_key(data.get("subject", "english"))
        idx = 0

        for section in data.get("sections") or []:
            section_id = section.get("section", "")
            domain = section.get("domain")
            chapter = section.get("title") or f"Section {section_id}"

            for passage in section.get("passages") or []:
                context_text = (passage.get("context_text") or "").strip()
                context_id = passage.get("context_id")
                context_source = passage.get("context_source")
                default_lo = passage.get("learning_outcome_id")

                for q in passage.get("questions") or []:
                    raw = {
                        **q,
                        "domain": domain,
                        "section": section_id,
                        "context_text": context_text,
                        "context_id": context_id,
                        "context_source": context_source,
                        "learning_outcome_id": q.get("learning_outcome_id") or default_lo,
                        "item_type": q.get("item_type") or "reading_comprehension",
                        "requires_context": True,
                    }
                    item = normalize_item(raw)
                    valid, errors = validate_item(item)
                    if not valid:
                        self._validation_log.extend(errors)
                        continue
                    idx += 1
                    item["chapter"] = chapter
                    item["grade"] = grade
                    item["subject"] = subject
                    item["_index"] = idx
                    items.append(item)

            for q in section.get("questions") or []:
                raw = {
                    **q,
                    "domain": domain,
                    "section": section_id,
                    "requires_context": False,
                }
                item = normalize_item(raw)
                valid, errors = validate_item(item)
                if not valid:
                    self._validation_log.extend(errors)
                    continue
                idx += 1
                item["chapter"] = chapter
                item["grade"] = grade
                item["subject"] = subject
                item["_index"] = idx
                items.append(item)

        return items

    def _structured_bank_path(self, subject_key: str, grade: int) -> Path | None:
        filenames = {
            "english": f"EnglishGrade{grade}_structured.json",
            "writing_english": f"EnglishGrade{grade}_structured.json",
            "maths": f"MathematicsGrade{grade}_structured.json",
            "mathematics": f"MathematicsGrade{grade}_structured.json",
            "science": f"ScienceGrade{grade}_structured.json",
        }
        name = filenames.get(subject_key)
        if not name:
            return None
        path = self.data_dir / name
        return path if path.exists() else None

    def _load_structured_bank(self, subject: str, grade: int) -> List[dict[str, Any]] | None:
        subject_key = normalize_subject_key(subject)
        path = self._structured_bank_path(subject_key, grade)
        if not path:
            return None
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return self._parse_structured_bank(data)

    def _parse_grade_json(self, path: Path) -> List[dict]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and data.get("sections"):
            flat = self._parse_structured_bank(data)
            chapters: dict[str, list] = {}
            for item in flat:
                ch = item.get("chapter") or "General"
                chapters.setdefault(ch, []).append(item)
            return [{"chapter": k, "questions": v} for k, v in chapters.items()]

        chapters: List[dict] = []
        if isinstance(data, list):
            chapters = data
        elif isinstance(data, dict):
            if "chapters" in data and isinstance(data["chapters"], list):
                chapters = data["chapters"]
            else:
                for key, value in data.items():
                    if isinstance(value, list):
                        chapters = value
                        break

        result = []
        for item in chapters:
            if not isinstance(item, dict):
                continue
            name = item.get("chapter") or item.get("title")
            questions = item.get("questions") or []
            if name and isinstance(questions, list):
                normalized = []
                for q in questions:
                    entry = self._normalize_question_entry(q)
                    if entry.get("text"):
                        ni = normalize_item(entry)
                        valid, errors = validate_item(ni)
                        if valid:
                            normalized.append({**entry, **ni})
                        else:
                            self._validation_log.extend(errors)
                if normalized:
                    result.append({"chapter": str(name).strip(), "questions": normalized})
        return result

    @staticmethod
    def _normalize_question_entry(raw: Any) -> dict:
        if isinstance(raw, str):
            return {"text": raw.strip(), "expected_answer": None, "answer_type": "short_answer"}
        if isinstance(raw, dict):
            text = (raw.get("stem") or raw.get("text") or raw.get("question") or "").strip()
            return {
                "text": text,
                "stem": text,
                "expected_answer": raw.get("expected_answer"),
                "answer_type": raw.get("answer_type", "short_answer"),
                "item_type": raw.get("item_type"),
                "domain": raw.get("domain"),
                "context_text": raw.get("context_text"),
            }
        return {"text": str(raw).strip(), "expected_answer": None, "answer_type": "short_answer"}

    def load_chapters(self, subject: str, grade: int = 10) -> List[dict]:
        subject_key = normalize_subject_key(subject)
        config = SUBJECT_CONFIG.get(subject_key)
        if not config:
            return []

        structured = self._load_structured_bank(subject_key, grade)
        if structured:
            chapters: dict[str, list] = {}
            for item in structured:
                ch = item.get("chapter") or "General"
                chapters.setdefault(ch, []).append(item)
            return [{"chapter": k, "questions": v} for k, v in chapters.items()]

        if config.get("source") == "jsonl":
            if grade == 10:
                chapters = self._load_english_chapters()
                if chapters:
                    return chapters
            pattern = config.get("file_pattern", "").format(grade=grade)
            path = self.data_dir / pattern
            if path.exists():
                return self._parse_grade_json(path)
            return []

        pattern = config.get("file_pattern", "").format(grade=grade)
        path = self.data_dir / pattern
        if not path.exists() and subject_key == "science" and grade == 10:
            alt = self.data_dir / "scienceclass10.json"
            if alt.exists():
                path = alt
        if not path.exists():
            return []
        return self._parse_grade_json(path)

    def _load_english_chapters(self) -> List[dict]:
        """English: CDC exercises from formatted JSONL — skips invalid reading-without-passage items."""
        chapters: List[dict] = []
        for path in sorted(self.data_dir.glob("*_formatted.jsonl")):
            unit_name = path.stem.replace("_formatted", "").replace("_", " ")
            entries: List[dict] = []
            seen: set[str] = set()

            def add_entry(
                text: str,
                expected: str | None = None,
                answer_type: str = "short_answer",
                context_text: str | None = None,
                item_type: str = "short_answer",
                domain: str = "grammar_vocabulary",
            ):
                text = text.strip()[:500]
                if len(text) < 20 or text in seen:
                    return
                item = normalize_item({
                    "stem": text,
                    "expected_answer": expected,
                    "answer_type": answer_type,
                    "context_text": context_text,
                    "item_type": item_type,
                    "domain": domain,
                })
                valid, errors = validate_item(item)
                if not valid:
                    self._validation_log.extend(errors)
                    return
                seen.add(text)
                entries.append(item)

            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    section = (obj.get("section_label") or "").upper()
                    if section not in ("A", "B", "C", "D", "E"):
                        continue

                    if section == "A":
                        word_bank = ""
                        if obj.get("text") and "Choose the words" in obj["text"]:
                            word_bank = obj["text"].split("\n", 1)[-1][:300]
                        for item in obj.get("left_items") or []:
                            text = (item.get("text") or "").strip()
                            if " -" in text:
                                definition, answer = text.rsplit(" -", 1)
                                q = f"Which word matches this definition? {definition.strip()}"
                                if word_bank:
                                    q += f"\n\nWord bank excerpt: {word_bank[:200]}"
                                add_entry(q, answer.strip(), "vocabulary", item_type="vocabulary")

                    elif section == "C" and obj.get("text"):
                        body = obj["text"]
                        if body.lower().startswith("c. read the story"):
                            continue
                        for block in re.split(r"\n(?=[a-h]\.\s)", body):
                            block = block.strip()
                            m = re.match(
                                r"^[a-h]\.\s*(.+?\?)\s*\n+(.+)",
                                block,
                                re.DOTALL | re.IGNORECASE,
                            )
                            if m:
                                q = m.group(1).strip()
                                model = re.split(r"\n\s*\n", m.group(2).strip())[0].strip()
                                if len(q) > 15 and len(model) > 10:
                                    add_entry(q, model[:400], "comprehension", item_type="grammar_correction")

                    else:
                        for item in obj.get("left_items") or []:
                            text = (item.get("text") or "").strip()
                            if text and len(text) > 20 and "?" in text:
                                add_entry(text.split("\n")[0], item_type="grammar_correction")

            if entries:
                chapters.append({
                    "chapter": f"English Unit {unit_name}",
                    "questions": entries[:25],
                })

        return chapters

    def list_subjects_for_grade(self, grade: int = 10, grid_check=None) -> dict:
        out = {}
        for key, config in SUBJECT_CONFIG.items():
            if key in ("mathematics", "writing_english"):
                continue
            chapters = self.load_chapters(key, grade)
            if chapters:
                structured = self._structured_bank_path(key, grade) is not None
                has_grid = grid_check(key, grade) if grid_check else False
                out[key] = {
                    "label": config["label"],
                    "skill_area": config["skill_area"],
                    "chapter_count": len(chapters),
                    "chapters": [{"name": c["chapter"], "available": True} for c in chapters],
                    "structured_bank": structured,
                    "blueprint_ready": structured and has_grid,
                }
        return out

    def get_curriculum_info(self, grade: int = 10) -> dict:
        from app.services.curriculum_metadata_service import get_curriculum_metadata

        meta = get_curriculum_metadata()

        def meta_has_grid(subject_key: str, g: int) -> bool:
            sk = "mathematics" if subject_key in ("maths", "mathematics") else subject_key
            return meta.get_spec_grid(sk, g) is not None

        subjects = self.list_subjects_for_grade(grade, meta_has_grid)
        return {
            "framework": CURRICULUM_FRAMEWORK,
            "board": CURRICULUM_BOARD,
            "grade": grade,
            "questions_per_chapter_default": DEFAULT_QUESTIONS_PER_CHAPTER,
            "subjects": subjects,
            "data_source": str(self.data_dir),
            "curriculum_metadata": meta.curriculum_summary(grade),
        }

    def _is_theory_question(self, subject_key: str, text: str, entry: dict | None = None) -> bool:
        if entry and (entry.get("expected_answer") or entry.get("domain") or entry.get("learning_outcome_id")):
            return False
        lower = text.lower().strip()
        if subject_key in ("english", "writing_english"):
            return False
        if subject_key in ("maths", "mathematics"):
            if any(p in lower for p in MATH_THEORY_PATTERNS):
                return True
            if not any(p in lower for p in MATH_COMPUTE_PATTERNS):
                if lower.startswith(("define", "what", "explain", "state", "write")):
                    return True
        if subject_key == "science":
            if lower.startswith(("define ", "what is ", "what are ", "state ")) and "?" not in lower:
                return True
        return False

    def _estimate_difficulty(self, subject_key: str, text: str, cognitive_level: str | None = None) -> int:
        if cognitive_level == "knowledge":
            return 1
        if cognitive_level in ("application", "analysis"):
            return 3
        if cognitive_level == "comprehension":
            return 2
        lower = text.lower()
        length = len(text)
        if subject_key in ("maths", "mathematics"):
            if any(w in lower for w in ("survey", "percentage", "percent", "both", "neither")):
                return 3
            if any(w in lower for w in ("find", "calculate", "if n(")):
                return 1 if length < 80 else 2
        if length > 150:
            return 3
        if length > 90:
            return 2
        return 1

    def _build_display(
        self,
        entry: dict,
        chapter: str,
        subject_key: str,
        grade: int,
    ) -> tuple[str, str]:
        """Return (question_display, question_raw)."""
        stem = entry.get("stem") or entry.get("text") or ""
        context = (entry.get("context_text") or "").strip()
        subject_label = {"maths": "Mathematics", "science": "Science", "english": "English"}.get(
            subject_key, subject_key.title()
        )

        header = f"**Context:** Grade {grade} Nepal CDC — {subject_label}"
        if entry.get("section"):
            header += f" | Section {entry['section']}"
        if entry.get("domain"):
            header += f" | {entry['domain'].replace('_', ' ').title()}"
        header += f" | {chapter}\n\n"

        if context:
            display = f"{header}**Question:** {stem}"
            question_raw = f"[Passage]\n{context}\n\n[Question]\n{stem}"
        elif subject_key in ("maths", "mathematics"):
            display = (
                f"{header}"
                f"A standard school-level problem. Use Rs., %, cm where relevant.\n\n"
                f"**Question:** {stem}"
            )
            question_raw = stem
        elif subject_key == "science":
            display = f"{header}Answer based on the Nepal CDC science syllabus.\n\n**Question:** {stem}"
            question_raw = stem
        else:
            display = f"{header}**Question:** {stem}"
            question_raw = stem

        return display, question_raw

    def _entry_to_pool_item(
        self,
        entry: dict,
        subject_key: str,
        grade: int,
        chapter: str,
        index: int,
    ) -> dict[str, Any]:
        stem = entry.get("stem") or entry.get("text") or ""
        difficulty = entry.get("difficulty") or self._estimate_difficulty(
            subject_key, stem, entry.get("cognitive_level")
        )
        qid = entry.get("id") or self._stable_id(subject_key, grade, chapter, index, stem)
        display, question_raw = self._build_display(entry, chapter, subject_key, grade)
        domain = entry.get("domain") or infer_domain_from_chapter(subject_key, chapter)

        return {
            "id": qid,
            "question": display,
            "question_raw": question_raw,
            "stem": stem,
            "expected_answer": entry.get("expected_answer"),
            "answer_type": entry.get("answer_type", "short_answer"),
            "item_type": entry.get("item_type", "short_answer"),
            "domain": domain,
            "section": entry.get("section"),
            "cognitive_level": entry.get("cognitive_level"),
            "learning_outcome_id": entry.get("learning_outcome_id"),
            "context_text": entry.get("context_text"),
            "context_id": entry.get("context_id"),
            "context_source": entry.get("context_source"),
            "rubric": entry.get("rubric"),
            "marks": entry.get("marks", 1),
            "chapter": chapter,
            "subject": subject_key,
            "grade": grade,
            "difficulty": difficulty,
            "difficulty_label": {1: "easy", 2: "medium", 3: "hard"}[min(3, max(1, difficulty))],
            "type": "computational" if subject_key in ("maths", "mathematics") else "short_answer",
            "curriculum": CURRICULUM_FRAMEWORK,
            "generative": bool(entry.get("generative")),
            "template_id": entry.get("template_id"),
            "template_kind": entry.get("template_kind"),
            "generated_params": entry.get("generated_params"),
        }

    def build_classified_pool(
        self,
        subject: str,
        grade: int = 10,
        *,
        include_dynamic: bool = True,
        difficulty: int | None = None,
    ) -> List[Dict[str, Any]]:
        subject_key = normalize_subject_key(subject)
        chapters_data = self.load_chapters(subject_key, grade)
        pool: List[Dict[str, Any]] = []
        structured_raw: List[dict[str, Any]] = []

        structured_path = self._structured_bank_path(subject_key, grade)
        if structured_path:
            with open(structured_path, encoding="utf-8") as f:
                structured_raw = self._parse_structured_bank(json.load(f))

        for ch in chapters_data:
            for i, entry in enumerate(ch["questions"]):
                if isinstance(entry, str):
                    entry = self._normalize_question_entry(entry)
                if not self._should_include_question(subject_key, entry):
                    continue
                if self._is_theory_question(
                    subject_key, entry.get("text") or entry.get("stem") or "", entry
                ):
                    continue
                pool.append(self._entry_to_pool_item(entry, subject_key, grade, ch["chapter"], i))

        if include_dynamic and subject_key != "science":
            from app.services.dynamic_question_service import get_dynamic_question_service

            dyn_svc = get_dynamic_question_service()
            dyn_entries = dyn_svc.generate_pool(
                subject,
                grade,
                difficulty=difficulty,
                structured_items=structured_raw,
            )
            for i, entry in enumerate(dyn_entries):
                chapter = (
                    entry.get("chapter")
                    or (entry.get("domain") or "Generated").replace("_", " ").title()
                )
                pool.append(
                    self._entry_to_pool_item(entry, subject_key, grade, chapter, 10000 + i)
                )

        return pool

    def assemble_blueprint_pool(
        self,
        subject: str,
        grade: int,
        total: int | None = None,
        difficulty: int | None = None,
    ) -> List[Dict[str, Any]]:
        """Build pool and select items per CDC spec grid when available."""
        pool = self.build_classified_pool(subject, grade, difficulty=difficulty)
        assembler = get_blueprint_assembler()
        return assembler.assemble_pool(subject, grade, pool, total)

    def pick_adaptive_question(
        self,
        pool: List[Dict[str, Any]],
        difficulty: int,
        used_ids: set,
        used_chapters: set | None = None,
    ) -> Dict[str, Any] | None:
        used_chapters = used_chapters or set()

        def candidates(level: int):
            return [
                q for q in pool
                if q["id"] not in used_ids
                and q["difficulty"] == level
                and q["chapter"] not in used_chapters
            ]

        for level in [difficulty, difficulty - 1, difficulty + 1, 2, 1, 3]:
            if level < 1 or level > 3:
                continue
            opts = candidates(level)
            if opts:
                return random.choice(opts)

        remaining = [q for q in pool if q["id"] not in used_ids]
        return random.choice(remaining) if remaining else None

    def pick_questions(
        self,
        subject: str,
        grade: int = 10,
        chapter: Optional[str] = None,
        questions_per_chapter: int = DEFAULT_QUESTIONS_PER_CHAPTER,
    ) -> List[Dict[str, Any]]:
        subject_key = normalize_subject_key(subject)
        chapters_data = self.load_chapters(subject_key, grade)

        if chapter:
            chapters_data = [c for c in chapters_data if c["chapter"].lower() == chapter.lower()]

        if not chapters_data:
            return []

        questions_per_chapter = max(1, min(questions_per_chapter, 5))
        formatted: List[Dict[str, Any]] = []
        order = 0

        for ch in chapters_data:
            pool = [q for q in ch["questions"] if self._should_include_question(subject_key, q)]
            if not pool:
                continue
            selected = pool if len(pool) <= questions_per_chapter else random.sample(pool, questions_per_chapter)

            for i, entry in enumerate(selected):
                if isinstance(entry, str):
                    entry = self._normalize_question_entry(entry)
                order += 1
                item = self._entry_to_pool_item(entry, subject_key, grade, ch["chapter"], i)
                item["order"] = order
                formatted.append(item)

        return formatted


_bank: QuestionBankService | None = None


def get_question_bank() -> QuestionBankService:
    global _bank
    if _bank is None:
        _bank = QuestionBankService()
    return _bank
