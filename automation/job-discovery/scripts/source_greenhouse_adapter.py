from typing import Any, Dict, List
import hashlib
import logging
import time
from datetime import datetime, UTC

from automation.common.normalization import ensure_str, normalize_terms

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

logger = logging.getLogger("pipeline.ingest.greenhouse")


def _job_id(title: str, company: str, url: str) -> str:
    canonical = f"{title.strip().lower()}|{company.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _http_get_json(url: str, params: Dict[str, Any], timeout_seconds: int) -> Any:
    if requests is None:
        raise RuntimeError("requests library is not available")
    headers = {"User-Agent": "StrataOS/1.0 (+job-discovery)"}
    res = requests.get(url, params=params, timeout=timeout_seconds, headers=headers)
    res.raise_for_status()
    return res.json()


def _fetch_live_greenhouse_jobs(config: Dict[str, Any], api_url: str) -> List[Dict[str, Any]]:
    """Fetch Greenhouse jobs from a live endpoint with page-based traversal.

    Supports common response shapes:
    - List payload
    - Object payload with jobs/results/data list
    - Optional metadata.next for continuation
    """
    timeout_seconds = int(config.get("GREENHOUSE_TIMEOUT_SECONDS", 10) or 10)
    per_page = int(config.get("GREENHOUSE_PER_PAGE", 100) or 100)
    max_pages = int(config.get("GREENHOUSE_MAX_PAGES", 25) or 25)
    max_retries = int(config.get("GREENHOUSE_MAX_RETRIES", 3) or 3)
    backoff_base = float(config.get("GREENHOUSE_BACKOFF_BASE_SECONDS", 0.5) or 0.5)

    out: List[Dict[str, Any]] = []
    for page in range(1, max_pages + 1):
        payload = None
        for attempt in range(1, max_retries + 1):
            try:
                payload = _http_get_json(
                    api_url,
                    params={"page": page, "per_page": per_page},
                    timeout_seconds=timeout_seconds,
                )
                break
            except Exception:
                if attempt >= max_retries:
                    raise
                time.sleep(backoff_base * (2 ** (attempt - 1)))

        if payload is None:
            break

        page_jobs: List[Dict[str, Any]]
        has_next = False
        if isinstance(payload, dict):
            raw_list = payload.get("jobs")
            if not isinstance(raw_list, list):
                raw_list = payload.get("results")
            if not isinstance(raw_list, list):
                raw_list = payload.get("data")
            page_jobs = raw_list if isinstance(raw_list, list) else []

            metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else payload.get("meta")
            if isinstance(metadata, dict):
                has_next = bool(metadata.get("next"))
        elif isinstance(payload, list):
            page_jobs = payload
            has_next = len(page_jobs) >= per_page
        else:
            page_jobs = []

        if not page_jobs:
            break

        out.extend(page_jobs)
        if not has_next and len(page_jobs) < per_page:
            break

    return out


def fetch_greenhouse_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Adapter for Greenhouse JSON feed.
    Pure, deterministic; gated by GREENHOUSE_ENABLED and GREENHOUSE_API_URL.
    No orchestrator changes or side effects.
    """
    if not bool(config.get("GREENHOUSE_ENABLED", False)):
        logger.debug("pipeline.ingest.greenhouse.disabled")
        return []

    api_url = ensure_str(config.get("GREENHOUSE_API_URL"))
    # Keep raw_jobs injection for deterministic tests; otherwise fetch live.
    injected = globals().get("raw_jobs")  # type: ignore
    if isinstance(injected, list):
        raw_jobs = injected
    elif api_url:
        raw_jobs = _fetch_live_greenhouse_jobs(config, api_url)
    else:
        logger.warning("pipeline.ingest.greenhouse.misconfigured", extra={"reason": "missing GREENHOUSE_API_URL"})
        raw_jobs = []

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
