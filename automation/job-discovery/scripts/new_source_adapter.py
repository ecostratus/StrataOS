import hashlib
from datetime import datetime
from typing import Dict, List, Any

from automation.common.normalization import ensure_str, normalize_terms


def _canonical_job_id(title: str, company: str, url: str) -> str:
    base = f"{title.strip().lower()}|{company.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def adapt_new_source(items: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    enabled = bool(config.get("NEW_SOURCE_ENABLED", False))
    if not enabled:
        return []

    out: List[Dict[str, Any]] = []
    for raw in items or []:
        title = ensure_str(raw.get("title"))
        company = ensure_str(raw.get("company"))
        url = ensure_str(raw.get("url"))
        location = ensure_str(raw.get("location"))
        posted = ensure_str(raw.get("posted_at"))

        if not title or not company or not url:
            continue

        job_id = _canonical_job_id(title, company, url)

        # Normalize optional keyword lists for enrichment boundaries (example)
        _ = normalize_terms(config.get("enrichment", {}).get("keywords", {}).get("role"))
        _ = normalize_terms(config.get("enrichment", {}).get("keywords", {}).get("stack"))

        out.append({
            "job_id": job_id,
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "url": url.strip(),
            "posted_at": posted.strip() or datetime.utcnow().strftime("%Y-%m-%d"),
        })

    # Deterministic ordering
    out.sort(key=lambda x: x["job_id"])
    return out
