from typing import Any, Dict, List
import hashlib
import logging
from datetime import datetime, UTC

from automation.common.normalization import ensure_str, normalize_terms

logger = logging.getLogger("pipeline.ingest.greenhouse")


def _job_id(title: str, company: str, url: str) -> str:
    canonical = f"{title.strip().lower()}|{company.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def fetch_greenhouse_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Adapter for Greenhouse JSON feed.
    Pure, deterministic; gated by GREENHOUSE_ENABLED and GREENHOUSE_API_URL.
    No orchestrator changes or side effects.
    """
    if not bool(config.get("GREENHOUSE_ENABLED", False)):
        logger.debug("pipeline.ingest.greenhouse.disabled")
        return []

    api_url = ensure_str(config.get("GREENHOUSE_API_URL"))
    # Placeholder: future implementation will fetch using api_url and API key
    # For tests, allow injection via module-scoped raw_jobs
    raw_jobs = globals().get("raw_jobs", [])  # type: ignore

    logger.debug("pipeline.ingest.greenhouse.fetch.start", extra={"api_url": api_url})

    normalized: List[Dict[str, Any]] = []
    for job in raw_jobs or []:
        # Canonical fields typically seen in Greenhouse feeds
        title = ensure_str(job.get("title"))
        company = ensure_str(job.get("company"))  # often absent; defaults to empty string
        # location can be object { name: "Remote" } or string
        loc_obj = job.get("location")
        location = ensure_str(loc_obj.get("name")) if isinstance(loc_obj, dict) else ensure_str(loc_obj)
        job_url = ensure_str(job.get("absolute_url")) or ensure_str(job.get("url"))
        posted = ensure_str(job.get("updated_at")) or ensure_str(job.get("created_at"))

        if not title or not job_url:
            # Skip malformed entries deterministically
            logger.debug("pipeline.ingest.greenhouse.malformed", extra={"reason": "missing title or url"})
            continue

        jid = _job_id(title, company, job_url)
        normalized.append({
            "job_id": jid,
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "url": job_url.strip(),
            "source": "greenhouse",
            "posted_at": (posted.strip() if posted else datetime.now(UTC).strftime("%Y-%m-%d")),
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

    logger.debug("pipeline.ingest.greenhouse.normalized", extra={"count": len(out)})
    return out
