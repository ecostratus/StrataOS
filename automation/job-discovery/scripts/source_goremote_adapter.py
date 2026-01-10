from typing import Any, Dict, List
import hashlib
import logging
from datetime import datetime, UTC

from automation.common.normalization import ensure_str

logger = logging.getLogger("pipeline.ingest.goremote")


def _job_id(title: str, company: str, url: str) -> str:
    canonical = f"{title.strip().lower()}|{company.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def fetch_goremote_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not bool(config.get("GOREMOTE_ENABLED", False)):
        logger.info("pipeline.ingest.goremote.disabled")
        return []

    api_url = ensure_str(config.get("GOREMOTE_API_URL"))
    if not api_url:
        logger.warning("pipeline.ingest.goremote.misconfigured")
        return []

    raw_jobs = globals().get("raw_jobs", [])  # type: ignore
    normalized: List[Dict[str, Any]] = []
    for job in raw_jobs or []:
        title = ensure_str(job.get("title"))
        company = ensure_str(job.get("company"))
        location = ensure_str(job.get("location"))
        job_url = ensure_str(job.get("url"))
        posted = ensure_str(job.get("datePublished")) or ensure_str(job.get("publishedAt"))

        if not title or not job_url:
            logger.debug("pipeline.ingest.goremote.malformed", extra={"reason": "missing title or url"})
            continue

        jid = _job_id(title, company, job_url)
        normalized.append({
            "job_id": jid,
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "url": job_url.strip(),
            "source": "goremote",
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

    logger.info("pipeline.ingest.goremote.success", extra={"count": len(out)})
    return out
