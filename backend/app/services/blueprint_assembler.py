"""
Assemble diagnostic tests from CDC-aligned specification grids.
"""
from __future__ import annotations

import random
from typing import Any

from app.services.curriculum_metadata_service import get_curriculum_metadata


class BlueprintAssembler:
    def __init__(self):
        self.meta = get_curriculum_metadata()

    def assemble_pool(
        self,
        subject: str,
        grade: int,
        candidate_pool: list[dict[str, Any]],
        total: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Select items matching spec grid section targets.
        Falls back to shuffled pool if blueprint missing or insufficient items.
        """
        grid = self.meta.get_spec_grid(subject, grade)
        if not grid or not candidate_pool:
            pool = list(candidate_pool)
            random.shuffle(pool)
            limit = total or len(pool)
            return pool[:limit]

        sections = grid.get("sections") or []
        selected: list[dict[str, Any]] = []
        used_ids: set[str] = set()

        for section in sections:
            domain = section.get("domain")
            target = section.get("target_count", 0)
            item_types = section.get("item_types") or []
            section_id = section.get("id")

            section_pool = [
                q for q in candidate_pool
                if q.get("id") not in used_ids
                and (not domain or q.get("domain") == domain)
                and (not item_types or q.get("item_type") in item_types)
            ]

            # Prefer one passage at a time for reading — group by context_id
            if domain == "reading":
                by_context: dict[str, list] = {}
                for q in section_pool:
                    cid = q.get("context_id") or q.get("context_text", "")[:40]
                    by_context.setdefault(cid, []).append(q)
                for _ in range(target):
                    if not by_context:
                        break
                    cid = random.choice(list(by_context.keys()))
                    opts = by_context[cid]
                    pick = random.choice(opts)
                    selected.append(pick)
                    used_ids.add(pick["id"])
                    by_context[cid] = [q for q in opts if q["id"] != pick["id"]]
                    if not by_context[cid]:
                        del by_context[cid]
            else:
                picks = section_pool if len(section_pool) <= target else random.sample(section_pool, target)
                for pick in picks[:target]:
                    if pick["id"] not in used_ids:
                        selected.append(pick)
                        used_ids.add(pick["id"])

        target_total = total or grid.get("total_items") or len(selected)
        if len(selected) < target_total:
            remaining = [q for q in candidate_pool if q.get("id") not in used_ids]
            random.shuffle(remaining)
            for q in remaining:
                if len(selected) >= target_total:
                    break
                selected.append(q)
                used_ids.add(q["id"])

        random.shuffle(selected)
        return selected[:target_total]


_assembler: BlueprintAssembler | None = None


def get_blueprint_assembler() -> BlueprintAssembler:
    global _assembler
    if _assembler is None:
        _assembler = BlueprintAssembler()
    return _assembler
