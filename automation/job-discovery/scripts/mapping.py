"""
Field mapping helpers for real endpoints.
"""
from __future__ import annotations

from typing import Dict, Any


def _normalize_text(value: Any) -> str:
    s = "" if value is None else str(value)
    # Collapse whitespace and trim
    return " ".join(s.split()).strip()


def _normalize_date(value: Any, default_today: str) -> str:
    try:
        s = str(value) if value is not None else ""
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            return s[:10]
    except Exception:
        pass
    return default_today


def map_linkedin_item(item: Dict[str, Any], today: str) -> Dict[str, str]:
    return {
        "title": _normalize_text(item.get("title", "")),
        "location": _normalize_text(item.get("location", "")),
        "company": _normalize_text(item.get("company", "")),
        "source": "linkedin",
        "url": _normalize_text(item.get("url", "")),
        "posted_date": _normalize_date(item.get("posted_date", today), today),
    }


def map_indeed_item(item: Dict[str, Any], today: str) -> Dict[str, str]:
    return {
        "title": _normalize_text(item.get("title", "")),
        "location": _normalize_text(item.get("location", "")),
        "company": _normalize_text(item.get("company", "")),
        "source": "indeed",
        "url": _normalize_text(item.get("url", "")),
        "posted_date": _normalize_date(item.get("posted_date", today), today),
    }
