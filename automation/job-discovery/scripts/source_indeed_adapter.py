from typing import Any, Dict, List
import hashlib
import logging
from datetime import datetime, UTC

from automation.common.normalization import ensure_str

logger = logging.getLogger("pipeline.ingest.indeed")


def _job_id(title: str, company: str, url: str) -> str:
    canonical = f"{title.strip().lower()}|{company.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def fetch_indeed_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Adapter for Indeed JSON feed (skeleton).
    Pure, deterministic; gated by INDEED_ENABLED and INDEED_API_URL/API_KEY.
    No orchestrator changes or side effects.
    """
    if not bool(config.get("INDEED_ENABLED", False)):
        logger.info("pipeline.ingest.indeed.disabled")
        return []

    api_url = ensure_str(config.get("INDEED_API_URL"))
    api_key = ensure_str(config.get("INDEED_API_KEY")) or ensure_str(config.get("INDEED_PUBLISHER_KEY"))
    if not api_url or not api_key:
        logger.warning("pipeline.ingest.indeed.misconfigured")
        return []

    # Placeholder: future implementation will fetch using api_url/api_key
    raw_jobs = globals().get("raw_jobs", [])  # type: ignore
    logger.debug("pipeline.ingest.indeed.fetch.start", extra={"api_url": api_url})

    normalized: List[Dict[str, Any]] = []
    for job in raw_jobs or []:
        title = ensure_str(job.get("title"))
        company = ensure_str(job.get("company"))
        location = ensure_str(job.get("location"))
        job_url = ensure_str(job.get("url"))
        posted = ensure_str(job.get("datePublished")) or ensure_str(job.get("publishedAt"))

        if not title or not job_url:
            logger.debug("pipeline.ingest.indeed.malformed", extra={"reason": "missing title or url"})
            continue

        jid = _job_id(title, company, job_url)
        normalized.append({
            "job_id": jid,
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "url": job_url.strip(),
            "source": "indeed",
            "posted_at": (posted.strip() if posted else datetime.now(UTC).strftime("%Y-%m-%d")),
        })

    normalized.sort(key=lambda x: x["job_id"])  
    out: List[Dict[str, Any]] = []
    seen = set()
    for item in normalized:
        jid = item["job_id"]
        if jid in seen:
            continue
        seen.add(jid)
        out.append(item)

    logger.info("pipeline.ingest.indeed.success", extra={"count": len(out)})
    return out
