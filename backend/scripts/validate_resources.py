#!/usr/bin/env python3
"""Validate all URLs in resource_index.yaml and refresh the cache."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from app.services.resource_validator import get_resource_validator

INDEX = Path(__file__).resolve().parent.parent / "data" / "resource_index.yaml"


def main() -> int:
    data = yaml.safe_load(INDEX.read_text(encoding="utf-8")) or {}
    validator = get_resource_validator()
    ok_count = 0
    fail_count = 0

    for subject, topics in data.items():
        if not isinstance(topics, dict):
            continue
        for topic, entry in topics.items():
            for res in entry.get("resources") or []:
                url = res.get("url", "")
                title = res.get("title", "")
                provider = res.get("provider", "")
                ok, verified, reason = validator.validate_url(url, provider)
                status = "OK" if ok else "FAIL"
                print(f"[{status}] {subject}/{topic} — {title}")
                if ok and verified:
                    print(f"         → {verified[:60]}")
                elif not ok:
                    print(f"         → {reason}")
                ok_count += int(ok)
                fail_count += int(not ok)

    print(f"\nTotal: {ok_count} OK, {fail_count} FAIL")
    return 1 if fail_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
