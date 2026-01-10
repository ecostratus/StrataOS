from typing import Any, Dict, List
import hashlib
from datetime import datetime, UTC

from automation.common.normalization import ensure_str


def _job_id(title: str, company: str, url: str) -> str:
    canonical = f"{title.strip().lower()}|{company.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def fetch_lever_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Adapter for Lever JSON feed.
    Pure, deterministic; gated by LEVER_ENABLED and LEVER_API_URL.
    """
    if not bool(config.get("LEVER_ENABLED", False)):
        return []

    api_url = ensure_str(config.get("LEVER_API_URL"))
    # Placeholder: in future, fetch from api_url
    raw_jobs: List[Dict[str, Any]] = []

    normalized: List[Dict[str, Any]] = []
    for job in raw_jobs or []:
        title = ensure_str(job.get("text")) or ensure_str(job.get("title"))
        company = ensure_str(job.get("company")) or ""
        location = ensure_str(job.get("categories", {}).get("location")) if isinstance(job.get("categories"), dict) else ensure_str(job.get("location"))
        job_url = ensure_str(job.get("hostedUrl")) or ensure_str(job.get("url"))
        posted = ensure_str(job.get("createdAt")) or ensure_str(job.get("publishedAt"))

        if not title or not job_url:
            continue

        jid = _job_id(title, company, job_url)
        normalized.append({
            "job_id": jid,
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "url": job_url.strip(),
            "source": "lever",
            "posted_at": posted.strip() or datetime.now(UTC).strftime("%Y-%m-%d"),
        })

    # Deterministic ordering and de-duplication
    normalized.sort(key=lambda x: x["job_id"]) 
    out: List[Dict[str, Any]] = []
    seen = set()
    for item in normalized:
        jid = item["job_id"]
        if jid in seen:
            continue
        seen.add(jid)
        out.append(item)
    return out
