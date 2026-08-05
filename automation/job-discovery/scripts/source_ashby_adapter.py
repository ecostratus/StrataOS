from typing import Any, Dict, List
import hashlib
import logging
from urllib.parse import urlparse
from datetime import datetime, UTC

from automation.common.normalization import ensure_str

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

logger = logging.getLogger("pipeline.ingest.ashby")


def _humanize_company_slug(slug: str) -> str:
    normalized = slug.strip().lower()
    if not normalized:
        return ""
    special_cases = {
        "openai": "OpenAI",
        "gitlab": "GitLab",
        "okta": "Okta",
        "datadog": "Datadog",
        "vanta": "Vanta",
        "drata": "Drata",
        "ramp": "Ramp",
        "notion": "Notion",
        "perplexity": "Perplexity",
    }
    if normalized in special_cases:
        return special_cases[normalized]
    return " ".join(part.capitalize() for part in normalized.replace("-", " ").replace("_", " ").split())


def _company_from_url(job_url: str) -> str:
    parsed = urlparse(job_url)
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return ""
    return _humanize_company_slug(parts[0])


def _job_id(title: str, company: str, url: str) -> str:
    canonical = f"{title.strip().lower()}|{company.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _http_get_json(url: str, timeout_seconds: int) -> Any:
    if requests is None:
        raise RuntimeError("requests library is not available")
    headers = {"User-Agent": "StrataOS/1.0 (+job-discovery)"}
    res = requests.get(url, timeout=timeout_seconds, headers=headers)
    res.raise_for_status()
    return res.json()


def _source_urls(config: Dict[str, Any]) -> List[str]:
    urls: List[str] = []
    raw_orgs = config.get("ASHBY_ORGS")
    if isinstance(raw_orgs, list):
        for org in raw_orgs:
            org_slug = ensure_str(org).strip()
            if not org_slug:
                continue
            urls.append(f"https://api.ashbyhq.com/posting-api/job-board/{org_slug}?includeCompensation=true")
    raw_urls = config.get("ASHBY_API_URLS")
    if isinstance(raw_urls, list):
        urls.extend(ensure_str(x) for x in raw_urls)
    api_url = ensure_str(config.get("ASHBY_API_URL"))
    if api_url:
        urls.append(api_url)
    seen = set()
    return [url for url in urls if url and not (url in seen or seen.add(url))]


def fetch_ashby_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Adapter for Ashby JSON feed (skeleton).
    Pure, deterministic; gated by ASHBY_ENABLED and ASHBY_API_URL/API_KEY.
    No orchestrator changes or side effects.
    """
    if not bool(config.get("ASHBY_ENABLED", False)):
        logger.info("pipeline.ingest.ashby.disabled")
        return []

    timeout_seconds = int(config.get("ASHBY_TIMEOUT_SECONDS", 20) or 20)
    source_urls = _source_urls(config)
    if not source_urls and not isinstance(globals().get("raw_jobs"), list):  # type: ignore
        logger.warning("pipeline.ingest.ashby.misconfigured")
        return []

    injected = globals().get("raw_jobs")  # type: ignore
    if isinstance(injected, list):
        raw_jobs = injected
    else:
        raw_jobs = []
        for api_url in source_urls:
            logger.debug("pipeline.ingest.ashby.fetch.start", extra={"api_url": api_url})
            payload = _http_get_json(api_url, timeout_seconds)
            if isinstance(payload, dict):
                jobs = payload.get("jobs") or payload.get("jobPostings") or payload.get("results") or payload.get("data")
                if isinstance(jobs, list):
                    raw_jobs.extend(jobs)

    normalized: List[Dict[str, Any]] = []
    for job in raw_jobs or []:
        title = ensure_str(job.get("title"))
        company = ensure_str(job.get("companyName")) or ensure_str(job.get("company"))
        location = ensure_str(job.get("location"))
        job_url = ensure_str(job.get("jobUrl")) or ensure_str(job.get("url"))
        posted = ensure_str(job.get("publishedAt")) or ensure_str(job.get("createdAt"))
        description = ensure_str(job.get("descriptionPlain")) or ensure_str(job.get("descriptionHtml"))
        department = ensure_str(job.get("department"))
        team = ensure_str(job.get("team"))

        if not company and job_url:
            company = _company_from_url(job_url)

        if not title or not job_url:
            logger.debug("pipeline.ingest.ashby.malformed", extra={"reason": "missing title or url"})
            continue

        jid = _job_id(title, company, job_url)
        normalized.append({
            "job_id": jid,
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "url": job_url.strip(),
            "source": "ashby",
            "posted_at": (posted.strip() if posted else datetime.now(UTC).strftime("%Y-%m-%d")),
            "description": description,
            "department": department,
            "team": team,
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

    logger.info("pipeline.ingest.ashby.success", extra={"count": len(out)})
    return out
