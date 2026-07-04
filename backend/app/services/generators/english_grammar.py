"""
Rule-based English grammar question generator from SVO templates.

Example seed: subject=Ram, verb=invited, object=Shyam, transform=future
→ "Change into future tense: Ram invited Shyam."
→ expected: "Ram will invite Shyam."
"""
from __future__ import annotations

import hashlib
import random
import re
from typing import Any

from app.core.question_templates import GenerativeTemplate

# Nepal / South-Asia school name pools (CBSE-style drills)
NAMES_MALE = [
    "Ram", "Shyam", "Hari", "Ramesh", "Amit", "Kumar", "Rahul", "Arjun",
    "Bikash", "Nabin", "Suman", "Prakash",
]
NAMES_FEMALE = [
    "Sita", "Gita", "Anita", "Priya", "Sunita", "Anjana", "Reena", "Mina",
    "Puja", "Sarita", "Kamala",
]
NAMES_ALL = NAMES_MALE + NAMES_FEMALE

# past_form -> (base, past_participle)
VERBS_TRANSITIVE: dict[str, tuple[str, str]] = {
    "invited": ("invite", "invited"),
    "kicked": ("kick", "kicked"),
    "helped": ("help", "helped"),
    "called": ("call", "called"),
    "met": ("meet", "met"),
    "gave": ("give", "given"),
    "sent": ("send", "sent"),
    "taught": ("teach", "taught"),
    "bought": ("buy", "bought"),
    "sold": ("sell", "sold"),
    "liked": ("like", "liked"),
    "visited": ("visit", "visited"),
    "praised": ("praise", "praised"),
    "warned": ("warn", "warned"),
    "followed": ("follow", "followed"),
}

TRANSFORM_LABELS = {
    "future": "future tense",
    "negative": "negative form",
    "negative_past": "negative past tense",
    "negative_future": "negative future tense",
    "passive": "passive voice",
    "indirect_speech": "indirect speech",
    "present_perfect": "present perfect tense",
    "past_continuous": "past continuous tense",
}

FEMALE_NAMES = {n.lower() for n in NAMES_FEMALE}


class EnglishGrammarGenerator:
    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def instantiate(
        self,
        template: GenerativeTemplate,
        *,
        transform: str | None = None,
        difficulty: int | None = None,
    ) -> dict[str, Any] | None:
        kind = template.kind
        if kind == "grammar_transform":
            return self._grammar_transform(template, transform=transform, difficulty=difficulty)
        if kind == "grammar_error":
            return self._grammar_error(template, difficulty=difficulty)
        return None

    def _pick_subject(self, template: GenerativeTemplate) -> str:
        pool = template.slots.get("subject", {}).get("pool")
        if pool == "names_female":
            return self.rng.choice(NAMES_FEMALE)
        if pool == "names_male":
            return self.rng.choice(NAMES_MALE)
        if template.seed.get("subject"):
            return template.seed["subject"]
        return self.rng.choice(NAMES_ALL)

    def _pick_object(self, template: GenerativeTemplate, subject: str) -> str:
        pool = template.slots.get("object", {}).get("pool")
        if pool == "names_female":
            candidates = [n for n in NAMES_FEMALE if n != subject]
            return self.rng.choice(candidates or NAMES_FEMALE)
        if pool == "names_male":
            candidates = [n for n in NAMES_MALE if n != subject]
            return self.rng.choice(candidates or NAMES_MALE)
        if template.seed.get("object"):
            obj = template.seed["object"]
            if obj != subject:
                return obj
        candidates = [n for n in NAMES_ALL if n != subject]
        return self.rng.choice(candidates)

    def _pick_verb_past(self, template: GenerativeTemplate) -> str:
        if template.seed.get("verb"):
            v = template.seed["verb"].lower()
            if v in VERBS_TRANSITIVE:
                return v
            for past, (base, _) in VERBS_TRANSITIVE.items():
                if base == v:
                    return past
        pool = template.slots.get("verb", {}).get("pool")
        if pool == "verbs_transitive_past":
            return self.rng.choice(list(VERBS_TRANSITIVE.keys()))
        return self.rng.choice(list(VERBS_TRANSITIVE.keys()))

    def _pick_transform(self, template: GenerativeTemplate) -> str:
        variants = template.variants or list(TRANSFORM_LABELS.keys())
        return self.rng.choice(variants)

    def _pronoun(self, name: str) -> str:
        return "she" if name.lower() in FEMALE_NAMES else "he"

    def _object_pronoun(self, name: str) -> str:
        return "her" if name.lower() in FEMALE_NAMES else "him"

    def _apply_transform(
        self, transform: str, subject: str, verb_past: str, obj: str
    ) -> str:
        base, pp = VERBS_TRANSITIVE.get(verb_past, (verb_past.rstrip("ed"), verb_past))

        if transform == "future":
            return f"{subject} will {base} {obj}."
        if transform == "negative_past":
            return f"{subject} did not {base} {obj}."
        if transform == "negative_future":
            return f"{subject} will not {base} {obj}."
        if transform == "negative":
            return f"{subject} does not {base} {obj}."
        if transform == "passive":
            return f"{obj} was {pp} by {subject}."
        if transform == "present_perfect":
            return f"{subject} has {pp} {obj}."
        if transform == "past_continuous":
            ing = self._ing_form(base)
            return f"{subject} was {ing} {obj}."
        if transform == "indirect_speech":
            pro = self._pronoun(subject)
            obj_pro = self._object_pronoun(obj)
            return f'{subject} said that {pro} had {pp} {obj_pro}.'
        return f"{subject} will {base} {obj}."

    def _grammar_transform(
        self,
        template: GenerativeTemplate,
        *,
        transform: str | None = None,
        difficulty: int | None = None,
    ) -> dict[str, Any]:
        subject = self._pick_subject(template)
        obj = self._pick_object(template, subject)
        verb_past = self._pick_verb_past(template)
        transform = transform or self._pick_transform(template)
        label = TRANSFORM_LABELS.get(transform, transform.replace("_", " "))

        source = f"{subject} {verb_past} {obj}"
        stem = f"Change into {label}: {source}."
        expected = self._apply_transform(transform, subject, verb_past, obj)

        diff = difficulty or template.difficulty
        if transform in ("indirect_speech", "passive"):
            diff = max(diff, 2)
        if transform in ("negative_future", "present_perfect"):
            diff = max(diff, 2)

        params = {
            "subject": subject,
            "verb": verb_past,
            "object": obj,
            "transform": transform,
        }
        qid = self._make_id(template.template_id, params)

        return {
            "id": qid,
            "stem": stem,
            "expected_answer": expected,
            "answer_type": "text",
            "item_type": template.item_type,
            "domain": template.domain,
            "section": template.section,
            "cognitive_level": template.cognitive_level,
            "learning_outcome_id": template.learning_outcome_id,
            "marks": template.marks,
            "difficulty": diff,
            "generative": True,
            "template_id": template.template_id,
            "template_kind": template.kind,
            "generated_params": params,
        }

    def _grammar_error(self, template: GenerativeTemplate, *, difficulty: int | None = None) -> dict[str, Any]:
        """Generate subject-verb agreement / don't-doesn't correction items."""
        subject = self._pick_subject(template)
        obj_word = self.rng.choice(["cricket", "football", "homework", "the lesson", "mathematics"])
        wrong = self.rng.choice([
            f"{subject} don't like to play {obj_word}.",
            f"{subject} don't likes {obj_word}.",
            f"Each of the students have finished {obj_word}.",
        ])
        if "don't like" in wrong:
            expected = wrong.replace("don't", "doesn't")
        elif "don't likes" in wrong:
            expected = wrong.replace("don't likes", "doesn't like")
        else:
            expected = wrong.replace("have", "has")

        stem = f"Correct the sentence: '{wrong}'"
        params = {"wrong": wrong}
        qid = self._make_id(template.template_id, params)
        return {
            "id": qid,
            "stem": stem,
            "expected_answer": expected,
            "answer_type": "text",
            "item_type": "grammar_correction",
            "domain": template.domain,
            "cognitive_level": template.cognitive_level,
            "learning_outcome_id": template.learning_outcome_id,
            "marks": template.marks,
            "difficulty": difficulty or template.difficulty,
            "generative": True,
            "template_id": template.template_id,
            "template_kind": template.kind,
            "generated_params": params,
        }

    @staticmethod
    def _ing_form(base: str) -> str:
        if base.endswith("ie"):
            return base[:-2] + "ying"
        if base.endswith("e") and not base.endswith("ee"):
            return base[:-1] + "ing"
        if len(base) >= 2 and base[-1] not in "aeiou" and base[-2] in "aeiou" and base[-1] == base[-2]:
            return base + "ing"
        return base + "ing"

    @staticmethod
    def _make_id(template_id: str, params: dict) -> str:
        raw = template_id + "|" + "|".join(f"{k}={v}" for k, v in sorted(params.items()))
        return "gen_" + hashlib.sha256(raw.encode()).hexdigest()[:14]

    @classmethod
    def infer_template_from_stem(cls, stem: str, item: dict, grade: int, subject: str) -> GenerativeTemplate | None:
        """Infer SVO template from an existing structured-bank grammar item."""
        lower = stem.lower()

        # "Change into future tense: Ram invited Shyam."
        m = re.search(
            r"change into ([\w\s]+):\s*([A-Z][a-z]+)\s+(\w+)\s+([A-Z][a-z]+)",
            stem,
            re.IGNORECASE,
        )
        if m:
            transform_raw = m.group(1).strip().lower()
            transform = cls._normalize_transform_label(transform_raw)
            return GenerativeTemplate(
                template_id=f"inferred_svo_{grade}",
                kind="grammar_transform",
                subject=subject,
                grade=grade,
                domain=item.get("domain", "grammar_vocabulary"),
                item_type=item.get("item_type", "grammar_correction"),
                learning_outcome_id=item.get("learning_outcome_id"),
                marks=int(item.get("marks") or 2),
                seed={
                    "subject": m.group(2),
                    "verb": m.group(3).lower(),
                    "object": m.group(4),
                },
                variants=[transform] if transform else [],
                slots={
                    "subject": {"pool": "names_male"},
                    "verb": {"pool": "verbs_transitive_past"},
                    "object": {"pool": "names_male"},
                },
            )

        if "correct the sentence" in lower and item.get("expected_answer"):
            return GenerativeTemplate(
                template_id=f"inferred_error_{grade}",
                kind="grammar_error",
                subject=subject,
                grade=grade,
                domain=item.get("domain", "grammar_vocabulary"),
                item_type="grammar_correction",
                learning_outcome_id=item.get("learning_outcome_id"),
                marks=int(item.get("marks") or 2),
            )

        return None

    @staticmethod
    def _normalize_transform_label(label: str) -> str:
        label = label.replace("tense", "").strip()
        for key, full in TRANSFORM_LABELS.items():
            if key.replace("_", " ") in label or full in label:
                return key
        if "passive" in label:
            return "passive"
        if "indirect" in label:
            return "indirect_speech"
        if "negative" in label and "future" in label:
            return "negative_future"
        if "negative" in label:
            return "negative_past"
        if "future" in label:
            return "future"
        return "future"
