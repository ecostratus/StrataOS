from typing import Any, Dict, List
import hashlib
from datetime import datetime, UTC
from urllib.parse import urlparse

from automation.common.normalization import ensure_str

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore


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


def _company_from_url(job_url: str) -> str:
    parsed = urlparse(job_url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return ""
    return parts[-2].replace("-", " ").replace("_", " ").title()


def _normalize_lever_url(api_url: str) -> List[str]:
    urls = [api_url]
    if "api.lever.co/postings/" in api_url and "/v0/" not in api_url:
        urls.append(api_url.replace("api.lever.co/postings/", "api.lever.co/v0/postings/"))
    return urls


def _source_urls(config: Dict[str, Any]) -> List[str]:
    urls: List[str] = []
    raw_urls = config.get("LEVER_API_URLS")
    if isinstance(raw_urls, list):
        for url in raw_urls:
            urls.extend(_normalize_lever_url(ensure_str(url)))
    api_url = ensure_str(config.get("LEVER_API_URL"))
    if api_url:
        urls.extend(_normalize_lever_url(api_url))
    seen = set()
    return [url for url in urls if url and not (url in seen or seen.add(url))]


def fetch_lever_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Adapter for Lever JSON feed.
    Pure, deterministic; gated by LEVER_ENABLED and LEVER_API_URL.
    """
    if not bool(config.get("LEVER_ENABLED", False)):
        return []

    timeout_seconds = int(config.get("LEVER_TIMEOUT_SECONDS", 20) or 20)
    injected = globals().get("raw_jobs")  # type: ignore
    if isinstance(injected, list):
        raw_jobs = injected
    else:
        raw_jobs = []
        for api_url in _source_urls(config):
            payload = _http_get_json(api_url, timeout_seconds)
            if isinstance(payload, list):
                raw_jobs.extend(payload)
            elif isinstance(payload, dict):
                postings = payload.get("postings") or payload.get("data") or payload.get("results")
                if isinstance(postings, list):
                    raw_jobs.extend(postings)

    normalized: List[Dict[str, Any]] = []
    for job in raw_jobs or []:
        title = ensure_str(job.get("text")) or ensure_str(job.get("title"))
        company = ensure_str(job.get("company")) or ensure_str(job.get("companyName")) or ""
        location = ensure_str(job.get("categories", {}).get("location")) if isinstance(job.get("categories"), dict) else ensure_str(job.get("location"))
        job_url = ensure_str(job.get("hostedUrl")) or ensure_str(job.get("url"))
        posted = ensure_str(job.get("createdAt")) or ensure_str(job.get("publishedAt"))
        description = (
            ensure_str(job.get("descriptionPlain"))
            or ensure_str(job.get("descriptionBodyPlain"))
            or ensure_str(job.get("openingPlain"))
            or ensure_str(job.get("description"))
        )

        if not title or not job_url:
            continue

        if not company:
            company = _company_from_url(job_url)

        jid = _job_id(title, company, job_url)
        normalized.append({
            "job_id": jid,
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "url": job_url.strip(),
            "source": "lever",
            "posted_at": posted.strip() or datetime.now(UTC).strftime("%Y-%m-%d"),
            "description": description,
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
