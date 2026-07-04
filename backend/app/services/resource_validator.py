"""
Validate curated resource URLs — never serve links that fail live checks.
Results cached on disk to avoid repeated network calls.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from app.core.paths import DATA_DIR

CACHE_PATH = DATA_DIR / "resource_url_cache.json"
CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days

YOUTUBE_ID_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{11})"
)


def extract_youtube_id(url: str) -> str | None:
    m = YOUTUBE_ID_RE.search(url or "")
    return m.group(1) if m else None


class ResourceValidator:
    def __init__(self, cache_path: Path = CACHE_PATH):
        self.cache_path = cache_path
        self._cache: dict[str, dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, encoding="utf-8") as f:
                    self._cache = json.load(f) or {}
            except (json.JSONDecodeError, OSError):
                self._cache = {}

    def _save_cache(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=2)

    def _cache_get(self, url: str) -> dict[str, Any] | None:
        entry = self._cache.get(url)
        if not entry:
            return None
        if time.time() - entry.get("checked_at", 0) > CACHE_TTL_SECONDS:
            return None
        return entry

    def _cache_set(self, url: str, ok: bool, title: str = "", reason: str = "") -> None:
        self._cache[url] = {
            "ok": ok,
            "title": title,
            "reason": reason,
            "checked_at": time.time(),
        }

    def validate_youtube(self, url: str) -> tuple[bool, str, str]:
        """Return (ok, title, reason). Uses YouTube oEmbed — no API key."""
        cached = self._cache_get(url)
        if cached is not None:
            return cached["ok"], cached.get("title", ""), cached.get("reason", "")

        try:
            oembed = (
                "https://www.youtube.com/oembed?"
                + urllib.parse.urlencode({"url": url, "format": "json"})
            )
            req = urllib.request.Request(oembed, headers={"User-Agent": "EduAssess/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            title = data.get("title", "")
            self._cache_set(url, True, title=title)
            self._save_cache()
            return True, title, ""
        except Exception as exc:
            reason = str(exc)[:120]
            self._cache_set(url, False, reason=reason)
            self._save_cache()
            return False, "", reason

    def validate_khan_academy(self, url: str) -> tuple[bool, str, str]:
        """Khan Academy pages — HEAD request, accept redirects."""
        cached = self._cache_get(url)
        if cached is not None:
            return cached["ok"], cached.get("title", ""), cached.get("reason", "")

        try:
            req = urllib.request.Request(
                url,
                method="HEAD",
                headers={"User-Agent": "Mozilla/5.0 (compatible; EduAssess/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                ok = resp.status < 400
            self._cache_set(url, ok, title="Khan Academy")
            self._save_cache()
            return ok, "Khan Academy", ""
        except urllib.error.HTTPError as exc:
            # Some Khan pages block HEAD — try GET with range
            if exc.code in (403, 405):
                return self._validate_khan_get(url)
            reason = f"HTTP {exc.code}"
            self._cache_set(url, False, reason=reason)
            self._save_cache()
            return False, "", reason
        except Exception as exc:
            reason = str(exc)[:120]
            self._cache_set(url, False, reason=reason)
            self._save_cache()
            return False, "", reason

    def _validate_khan_get(self, url: str) -> tuple[bool, str, str]:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; EduAssess/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                ok = resp.status < 400 and len(resp.read(2048)) > 100
            self._cache_set(url, ok, title="Khan Academy")
            self._save_cache()
            return ok, "Khan Academy", ""
        except Exception as exc:
            reason = str(exc)[:120]
            self._cache_set(url, False, reason=reason)
            self._save_cache()
            return False, "", reason

    def validate_url(self, url: str, provider: str = "") -> tuple[bool, str, str]:
        if not url or not url.startswith("http"):
            return False, "", "missing url"
        provider = (provider or "").lower()
        if provider == "youtube" or "youtube.com" in url or "youtu.be" in url:
            return self.validate_youtube(url)
        if provider == "khan_academy" or "khanacademy.org" in url:
            return self.validate_khan_academy(url)
        # Other providers — basic reachability
        cached = self._cache_get(url)
        if cached is not None:
            return cached["ok"], cached.get("title", ""), cached.get("reason", "")
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "EduAssess/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                ok = resp.status < 400
            self._cache_set(url, ok)
            self._save_cache()
            return ok, "", ""
        except Exception as exc:
            self._cache_set(url, False, reason=str(exc)[:120])
            self._save_cache()
            return False, "", str(exc)[:120]

    def filter_resources(
        self,
        resources: list[dict[str, Any]],
        *,
        validate_live: bool = True,
    ) -> list[dict[str, Any]]:
        """Drop broken links; attach verified_title when available."""
        if not validate_live:
            return resources

        valid: list[dict[str, Any]] = []
        for raw in resources:
            url = raw.get("url", "")
            provider = raw.get("provider", "")
            ok, title, reason = self.validate_url(url, provider)
            if not ok:
                continue
            entry = dict(raw)
            if title and provider == "youtube":
                entry["verified_title"] = title
            entry["url_verified"] = True
            valid.append(entry)
        return valid


_validator: ResourceValidator | None = None


def get_resource_validator() -> ResourceValidator:
    global _validator
    if _validator is None:
        _validator = ResourceValidator()
    return _validator
