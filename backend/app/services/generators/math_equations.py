"""
Rule-based mathematics question generator from equation templates.

Swaps coefficients, constants, variable names, and equation degree.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any

from app.core.question_templates import GenerativeTemplate

VARIABLES = ["x", "y", "n", "t", "a", "m"]


class MathEquationGenerator:
    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()

    def instantiate(
        self,
        template: GenerativeTemplate,
        *,
        difficulty: int | None = None,
    ) -> dict[str, Any] | None:
        kind = template.kind
        diff = difficulty or template.difficulty
        if kind == "linear_equation":
            return self._linear(template, diff)
        if kind == "linear_two_step":
            return self._linear_two_step(template, diff)
        if kind == "quadratic_equation":
            return self._quadratic(template, diff)
        if kind == "factorize":
            return self._factorize(template, diff)
        if kind == "arithmetic_mean":
            return self._mean(template, diff)
        if kind == "percentage_word":
            return self._percentage_word(template, diff)
        return None

    def _var(self, template: GenerativeTemplate) -> str:
        allowed = template.slots.get("variable", {}).get("values") or VARIABLES
        return self.rng.choice(allowed)

    def _linear(self, template: GenerativeTemplate, difficulty: int) -> dict[str, Any]:
        var = self._var(template)
        x_sol = self.rng.randint(1, 8 + difficulty * 2)
        a = self.rng.randint(2, 4 + difficulty)
        b = self.rng.randint(1, 10 + difficulty * 2)
        c = a * x_sol + b

        stem = f"Solve for {var}: {a}{var} + {b} = {c}"
        if difficulty >= 2 and self.rng.random() < 0.4:
            b_neg = self.rng.randint(1, 8)
            c = a * x_sol - b_neg
            stem = f"Solve for {var}: {a}{var} - {b_neg} = {c}"
            b = -b_neg

        params = {"a": a, "b": b, "c": c, "var": var, "solution": x_sol}
        return self._pack(template, stem, str(x_sol), params, difficulty)

    def _linear_two_step(self, template: GenerativeTemplate, difficulty: int) -> dict[str, Any]:
        var = self._var(template)
        x_sol = self.rng.randint(2, 6 + difficulty)
        a = self.rng.randint(2, 5)
        inner = self.rng.randint(1, 6)
        c = a * (x_sol + inner)
        stem = f"Solve for {var}: {a}({var} + {inner}) = {c}"
        params = {"a": a, "inner": inner, "c": c, "var": var, "solution": x_sol}
        return self._pack(template, stem, str(x_sol), params, max(difficulty, 2))

    def _quadratic(self, template: GenerativeTemplate, difficulty: int) -> dict[str, Any]:
        var = self._var(template)
        r1 = self.rng.randint(1, 5 + difficulty)
        r2 = self.rng.randint(1, 5 + difficulty)
        if r1 == r2:
            r2 += 1
        # (var - r1)(var - r2) = var² - (r1+r2)var + r1*r2
        b = -(r1 + r2)
        c = r1 * r2
        b_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
        c_str = f"+ {c}" if c >= 0 else f"- {abs(c)}"
        stem = f"Solve for {var}: {var}² {b_str}{var} {c_str} = 0"
        answer = f"{min(r1, r2)}, {max(r1, r2)}"
        params = {"roots": [r1, r2], "var": var}
        return self._pack(template, stem, answer, params, max(difficulty, 3))

    def _factorize(self, template: GenerativeTemplate, difficulty: int) -> dict[str, Any]:
        var = self._var(template)
        r1 = self.rng.randint(2, 4 + difficulty)
        r2 = self.rng.randint(2, 4 + difficulty)
        b = r1 + r2
        c = r1 * r2
        stem = f"Factorize: {var}² + {b}{var} + {c}"
        answer = f"({var} + {r1})({var} + {r2})"
        params = {"r1": r1, "r2": r2, "var": var}
        return self._pack(template, stem, answer, params, difficulty)

    def _mean(self, template: GenerativeTemplate, difficulty: int) -> dict[str, Any]:
        count = 4 + difficulty
        values = [self.rng.randint(5, 20) for _ in range(count)]
        mean = sum(values) / len(values)
        answer = str(int(mean)) if mean == int(mean) else f"{mean:.1f}"
        stem = f"Find the mean of: {', '.join(map(str, values))}."
        return self._pack(template, stem, answer, {"values": values}, difficulty)

    def _percentage_word(self, template: GenerativeTemplate, difficulty: int) -> dict[str, Any]:
        price = self.rng.choice([100, 200, 250, 400, 500, 800])
        pct = self.rng.choice([10, 15, 20, 25])
        answer = str(price * pct // 100)
        stem = (
            f"A shopkeeper in Kathmandu offers {pct}% discount on a Rs. {price} bag. "
            f"Find the discount amount."
        )
        return self._pack(template, stem, answer, {"price": price, "pct": pct}, max(difficulty, 2))

    def _pack(
        self,
        template: GenerativeTemplate,
        stem: str,
        answer: str,
        params: dict,
        difficulty: int,
    ) -> dict[str, Any]:
        qid = "gen_" + hashlib.sha256(
            (template.template_id + stem + answer).encode()
        ).hexdigest()[:14]
        return {
            "id": qid,
            "stem": stem,
            "expected_answer": answer,
            "answer_type": "numeric" if answer.replace(".", "").replace(",", "").isdigit() else "text",
            "item_type": template.item_type,
            "domain": template.domain,
            "section": template.section,
            "cognitive_level": template.cognitive_level,
            "learning_outcome_id": template.learning_outcome_id,
            "marks": template.marks,
            "difficulty": min(3, max(1, difficulty)),
            "generative": True,
            "template_id": template.template_id,
            "template_kind": template.kind,
            "generated_params": params,
        }
