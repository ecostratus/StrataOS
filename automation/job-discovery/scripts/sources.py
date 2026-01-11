"""
Source fetchers for job discovery.

Replace placeholder implementations with real scrapers per scraper-spec.md.
Each function returns a list of jobs with keys:
- title, location, company, source, url, posted_date (YYYY-MM-DD)
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
try:  # Python 3.11+
    from datetime import UTC  # type: ignore
except Exception:  # Python <3.11
    from datetime import timezone as _tz  # type: ignore
    UTC = _tz.utc  # type: ignore
from typing import Dict, List, Any, Optional, Callable

# Ensure repo root on path (mirrors orchestrator behavior)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config  # type: ignore
from automation.common.normalization import ensure_int, ensure_float, ensure_str
from scrape_utils import RateLimiter, with_retry  # type: ignore
from metrics import Metrics  # type: ignore
from logging_utils import structured_log  # type: ignore
from mapping import map_linkedin_item, map_indeed_item  # type: ignore
import logging
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - allow tests to run without requests installed
    requests = None  # type: ignore

logger = logging.getLogger(__name__)

# Module-level metrics to keep orchestrator simple
_METRICS = Metrics()




def reset_metrics() -> None:
    global _METRICS
    _METRICS = Metrics()


def get_metrics() -> Metrics:
    return _METRICS


def _http_get_json(url: str, params: Optional[Dict[str, Any]] = None, timeout: int = 10, headers: Optional[Dict[str, str]] = None) -> Any:
    """HTTP GET returning parsed JSON. Raises on non-200 or parse error."""
    if requests is None:
        raise RuntimeError("requests library not available")
    res = requests.get(url, params=params or {}, timeout=timeout, headers=headers or {})
    res.raise_for_status()
    return res.json()


def _normalize_date(date_value: Any, default_today: str) -> str:
    """Normalize a date-like value to YYYY-MM-DD string in UTC.

    Attempts to parse ISO-like strings; otherwise falls back to default_today.
    """
    try:
        if isinstance(date_value, str):
            # Fast path: already YYYY-MM-DD
            if len(date_value) >= 10 and date_value[4] == "-" and date_value[7] == "-":
                return date_value[:10]
        # No robust parser by design (keep deps minimal). Fallback.
    except Exception:
        pass
    return default_today


def fetch_linkedin_jobs() -> List[Dict[str, str]]:
    """Config-driven LinkedIn scraper.

    If LINKEDIN_API_URL is not set, return a small sample to keep the pipeline operable.
    Applies rate limiting and retries around the HTTP request.
    Expects the API to return a JSON list of items with at least title, company, location, url, posted_date.
    """
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    url = ensure_str(config.get("LINKEDIN_API_URL", ""))
    token = ensure_str(config.get("LINKEDIN_API_TOKEN", config.get("LINKEDIN_API_KEY", "")))
    rpm = ensure_int(config.get_int("SCRAPER_RPM", 30), 30)
    timeout = ensure_int(config.get_int("SCRAPER_TIMEOUT", 10), 10)
    max_retries = ensure_int(config.get_int("SCRAPER_MAX_RETRIES", 3), 3)
    backoff_base = ensure_float(config.get_float("SCRAPER_BACKOFF_BASE", 0.5), 0.5)
    backoff_max = ensure_float(config.get_float("SCRAPER_BACKOFF_MAX", 4.0), 4.0)
    jitter_ms = ensure_int(config.get_int("SCRAPER_JITTER_MS", 100), 100)

    # Safe fallback when no configured endpoint
    if not url:
        return [
            {
                "title": "Software Engineer",
                "location": "Remote",
                "company": "LinkedIn Co",
                "source": "linkedin",
                "url": "https://linkedin.com/jobs/example",
                "posted_date": today,
            }
        ]

    limiter = RateLimiter(rpm=rpm)

    def _fetch() -> List[Dict[str, Any]]:
        limiter.acquire()
        # Authorization header handled internally when real HTTP is used
        data = _http_get_json(ensure_str(url), timeout=timeout)
        if not isinstance(data, list):
            raise ValueError("LinkedIn API returned non-list")
        return data

    def _on_error(attempt: int, e: Exception) -> None:
        structured_log(logger, "error", "scraper_error", source="linkedin", attempt=attempt, message=str(e))

    def _on_retry(attempt: int, delay: float, e: Exception) -> None:
        _METRICS.retries_attempted += 1
        structured_log(logger, "error", "scraper_retry_error", source="linkedin", attempt=attempt, delay=round(delay, 3))

    result = with_retry(
        _fetch,
        max_retries=max_retries,
        backoff_base=backoff_base,
        backoff_max=backoff_max,
        jitter_ms=jitter_ms,
        on_error=_on_error,
        on_retry=_on_retry,
    )
    if result is None:
        structured_log(logger, "error", "scraper_give_up", source="linkedin")
        _METRICS.scraper_failures += 1
        return []

    _METRICS.inc_jobs("linkedin", len(result))
    jobs: List[Dict[str, str]] = []
    for item in result:
        # Map via helper
        mapped = map_linkedin_item(item, today)
        # Track malformed if critical fields missing
        if not all(mapped.get(k) for k in ("title", "location", "company", "url", "posted_date")):
            _METRICS.inc_malformed("linkedin", 1)
            structured_log(logger, "warning", "malformed_entry", source="linkedin")
        jobs.append(mapped)
    return jobs


def fetch_indeed_jobs() -> List[Dict[str, str]]:
    """Config-driven Indeed scraper.

    If INDEED_API_URL is not set, return a small sample to keep the pipeline operable.
    Applies rate limiting and retries around the HTTP request.
    Expects the API to return a JSON list of items with at least title, company, location, url, posted_date.
    """
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    url = ensure_str(config.get("INDEED_API_URL", ""))
    token = ensure_str(config.get("INDEED_API_TOKEN", config.get("INDEED_PUBLISHER_KEY", "")))
    rpm = ensure_int(config.get_int("SCRAPER_RPM", 30), 30)
    timeout = ensure_int(config.get_int("SCRAPER_TIMEOUT", 10), 10)
    max_retries = ensure_int(config.get_int("SCRAPER_MAX_RETRIES", 3), 3)
    backoff_base = ensure_float(config.get_float("SCRAPER_BACKOFF_BASE", 0.5), 0.5)
    backoff_max = ensure_float(config.get_float("SCRAPER_BACKOFF_MAX", 4.0), 4.0)
    jitter_ms = ensure_int(config.get_int("SCRAPER_JITTER_MS", 100), 100)

    if not url:
        return [
            {
                "title": "Data Analyst",
                "location": "New York, NY",
                "company": "Indeed LLC",
                "source": "indeed",
                "url": "https://indeed.com/viewjob/example",
                "posted_date": today,
            }
        ]

    limiter = RateLimiter(rpm=rpm)

    def _fetch() -> List[Dict[str, Any]]:
        limiter.acquire()
        data = _http_get_json(ensure_str(url), timeout=timeout)
        if not isinstance(data, list):
            raise ValueError("Indeed API returned non-list")
        return data

    def _on_error(attempt: int, e: Exception) -> None:
        structured_log(logger, "error", "scraper_error", source="indeed", attempt=attempt, message=str(e))

    def _on_retry(attempt: int, delay: float, e: Exception) -> None:
        _METRICS.retries_attempted += 1
        structured_log(logger, "error", "scraper_retry_error", source="indeed", attempt=attempt, delay=round(delay, 3))

    result = with_retry(
        _fetch,
        max_retries=max_retries,
        backoff_base=backoff_base,
        backoff_max=backoff_max,
        jitter_ms=jitter_ms,
        on_error=_on_error,
        on_retry=_on_retry,
    )
    if result is None:
        structured_log(logger, "error", "scraper_give_up", source="indeed")
        _METRICS.scraper_failures += 1
        return []

    _METRICS.inc_jobs("indeed", len(result))
    jobs: List[Dict[str, str]] = []
    for item in result:
        mapped = map_indeed_item(item, today)
        if not all(mapped.get(k) for k in ("title", "location", "company", "url", "posted_date")):
            _METRICS.inc_malformed("indeed", 1)
            structured_log(logger, "warning", "malformed_entry", source="indeed")
        jobs.append(mapped)
    return jobs

# ------------------
# Phase 3D Orchestrator
# ------------------
def fetch_all_sources(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fetch jobs from all enabled source adapters and return a single canonical list.

    - Config-gated activation per source
    - De-duplication by job_id across sources
    - Deterministic ordering by job_id
    """
    import importlib

    registry: List[Dict[str, str]] = [
        {"enable_key": "LEVER_ENABLED", "module": "automation.job-discovery.scripts.source_lever_adapter", "func": "fetch_lever_jobs"},
        {"enable_key": "GREENHOUSE_ENABLED", "module": "automation.job-discovery.scripts.source_greenhouse_adapter", "func": "fetch_greenhouse_jobs"},
        {"enable_key": "ASHBY_ENABLED", "module": "automation.job-discovery.scripts.source_ashby_adapter", "func": "fetch_ashby_jobs"},
        {"enable_key": "INDEED_ENABLED", "module": "automation.job-discovery.scripts.source_indeed_adapter", "func": "fetch_indeed_jobs"},
        {"enable_key": "ZIPRECRUITER_ENABLED", "module": "automation.job-discovery.scripts.source_ziprecruiter_adapter", "func": "fetch_ziprecruiter_jobs"},
        {"enable_key": "GOOGLEJOBS_ENABLED", "module": "automation.job-discovery.scripts.source_google_jobs_adapter", "func": "fetch_google_jobs"},
        {"enable_key": "GLASSDOOR_ENABLED", "module": "automation.job-discovery.scripts.source_glassdoor_adapter", "func": "fetch_glassdoor_jobs"},
        {"enable_key": "CRAIGSLIST_ENABLED", "module": "automation.job-discovery.scripts.source_craigslist_adapter", "func": "fetch_craigslist_jobs"},
        {"enable_key": "GOREMOTE_ENABLED", "module": "automation.job-discovery.scripts.source_goremote_adapter", "func": "fetch_goremote_jobs"},
    ]

    all_jobs: List[Dict[str, Any]] = []
    for entry in registry:
        key = entry["enable_key"]
        if not bool(cfg.get(key, False)):
            continue
        module = importlib.import_module(entry["module"])  # type: ignore
        fetch_fn = getattr(module, entry["func"])  # type: ignore
        out = fetch_fn(cfg)
        if isinstance(out, list):
            all_jobs.extend(out)

    # De-duplicate by job_id
    dedup: Dict[str, Dict[str, Any]] = {}
    for job in all_jobs:
        jid = str(job.get("job_id", ""))
        if not jid:
            # Skip entries missing canonical id
            continue
        if jid not in dedup:
            dedup[jid] = job

    result = list(dedup.values())
    result.sort(key=lambda x: str(x.get("job_id", "")))
    return result
