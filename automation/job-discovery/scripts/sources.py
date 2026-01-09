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
from typing import Dict, List, Any, Optional

# Ensure repo root on path (mirrors orchestrator behavior)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config  # type: ignore
from .scrape_utils import RateLimiter, with_retry  # type: ignore
from .metrics import Metrics  # type: ignore
from .logging_utils import structured_log  # type: ignore
import logging
import requests

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
    url = config.get("LINKEDIN_API_URL", "")
    token = config.get("LINKEDIN_API_TOKEN", config.get("LINKEDIN_API_KEY", "")) or ""
    rpm = int(config.get_int("SCRAPER_RPM", 30))
    timeout = int(config.get_int("SCRAPER_TIMEOUT", 10))
    max_retries = int(config.get_int("SCRAPER_MAX_RETRIES", 3))
    backoff_base = float(config.get_float("SCRAPER_BACKOFF_BASE", 0.5))
    backoff_max = float(config.get_float("SCRAPER_BACKOFF_MAX", 4.0))
    jitter_ms = int(config.get_int("SCRAPER_JITTER_MS", 100))

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

    limiter = RateLimiter(
        rpm=rpm,
        on_sleep=lambda seconds: setattr(_METRICS, "rate_limit_sleeps", _METRICS.rate_limit_sleeps + 1),
    )

    def _fetch() -> List[Dict[str, Any]]:
        limiter.acquire()
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        data = _http_get_json(url, timeout=timeout, headers=headers)
        if not isinstance(data, list):
            raise ValueError("LinkedIn API returned non-list")
        return data

    result = with_retry(
        _fetch,
        max_retries=max_retries,
        backoff_base=backoff_base,
        backoff_max=backoff_max,
        jitter_ms=jitter_ms,
        on_error=lambda attempt, e: structured_log(logger, "error", "scraper_error", source="linkedin", attempt=attempt, message=str(e)),
        on_retry=lambda attempt, delay, e: setattr(_METRICS, "retries_attempted", _METRICS.retries_attempted + 1),
    )
    if result is None:
        structured_log(logger, "error", "scraper_give_up", source="linkedin")
        _METRICS.scraper_failures += 1
        return []

    _METRICS.inc_jobs("linkedin", len(result))
    jobs: List[Dict[str, str]] = []
    for item in result:
        # Map to required fields; use defaults when missing
        mapped = {
            "title": str(item.get("title", "")),
            "location": str(item.get("location", "")),
            "company": str(item.get("company", "")),
            "source": "linkedin",
            "url": str(item.get("url", "")),
            "posted_date": _normalize_date(item.get("posted_date", today), today),
        }
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
    url = config.get("INDEED_API_URL", "")
    token = config.get("INDEED_API_TOKEN", config.get("INDEED_PUBLISHER_KEY", "")) or ""
    rpm = int(config.get_int("SCRAPER_RPM", 30))
    timeout = int(config.get_int("SCRAPER_TIMEOUT", 10))
    max_retries = int(config.get_int("SCRAPER_MAX_RETRIES", 3))
    backoff_base = float(config.get_float("SCRAPER_BACKOFF_BASE", 0.5))
    backoff_max = float(config.get_float("SCRAPER_BACKOFF_MAX", 4.0))
    jitter_ms = int(config.get_int("SCRAPER_JITTER_MS", 100))

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

    limiter = RateLimiter(
        rpm=rpm,
        on_sleep=lambda seconds: setattr(_METRICS, "rate_limit_sleeps", _METRICS.rate_limit_sleeps + 1),
    )

    def _fetch() -> List[Dict[str, Any]]:
        limiter.acquire()
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        data = _http_get_json(url, timeout=timeout, headers=headers)
        if not isinstance(data, list):
            raise ValueError("Indeed API returned non-list")
        return data

    result = with_retry(
        _fetch,
        max_retries=max_retries,
        backoff_base=backoff_base,
        backoff_max=backoff_max,
        jitter_ms=jitter_ms,
        on_error=lambda attempt, e: structured_log(logger, "error", "scraper_error", source="indeed", attempt=attempt, message=str(e)),
        on_retry=lambda attempt, delay, e: setattr(_METRICS, "retries_attempted", _METRICS.retries_attempted + 1),
    )
    if result is None:
        structured_log(logger, "error", "scraper_give_up", source="indeed")
        _METRICS.scraper_failures += 1
        return []

    _METRICS.inc_jobs("indeed", len(result))
    jobs: List[Dict[str, str]] = []
    for item in result:
        mapped = {
            "title": str(item.get("title", "")),
            "location": str(item.get("location", "")),
            "company": str(item.get("company", "")),
            "source": "indeed",
            "url": str(item.get("url", "")),
            "posted_date": _normalize_date(item.get("posted_date", today), today),
        }
        if not all(mapped.get(k) for k in ("title", "location", "company", "url", "posted_date")):
            _METRICS.inc_malformed("indeed", 1)
            structured_log(logger, "warning", "malformed_entry", source="indeed")
        jobs.append(mapped)
    return jobs
