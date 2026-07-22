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
    # Accept common external API shapes (e.g., position/company_name/publication_date)
    # while preserving the canonical discovery schema.
    title = item.get("title") or item.get("position") or item.get("job_title")
    location = item.get("location") or item.get("candidate_required_location")
    company = item.get("company") or item.get("company_name")
    url = item.get("url") or item.get("job_url")
    posted_date = (
        item.get("posted_date")
        or item.get("publication_date")
        or item.get("date")
        or item.get("created_at")
    )

    return {
        "title": _normalize_text(title),
        "location": _normalize_text(location),
        "company": _normalize_text(company),
        "source": "indeed",
        "url": _normalize_text(url),
        "posted_date": _normalize_date(posted_date if posted_date is not None else today, today),
    }
