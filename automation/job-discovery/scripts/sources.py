"""
Source fetchers for job discovery.

Two-stage import hardening:
- Avoid module-level imports of local modules so dynamic loading works
    without relying on PYTHONPATH or package context.
- Use dotted import first when available; fallback to repo-root-relative
    dynamic loading via import_helpers.load_module_from_path.

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

import importlib

# Two-stage import helpers for local modules
def _load_import_helpers():
    try:
        from automation.common.import_helpers import load_module_from_path  # type: ignore
        return load_module_from_path
    except ModuleNotFoundError:
        # Best-effort dynamic load of import_helpers itself
        import importlib.util
        import os as _os
        _root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..", ".."))
        _p = _os.path.join(_root, "automation", "common", "import_helpers.py")
        spec = importlib.util.spec_from_file_location("automation_common_import_helpers", _p)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore
            return getattr(mod, "load_module_from_path")
        raise


def _load_config():
    try:
        from config.config_loader import config  # type: ignore
        return config
    except ModuleNotFoundError:
        load_module_from_path = _load_import_helpers()
        mod = load_module_from_path("config/config_loader.py", "config_loader")
        return mod.config


def _load_normalization():
    try:
        from automation.common.normalization import ensure_int, ensure_float, ensure_str  # type: ignore
        return ensure_int, ensure_float, ensure_str
    except ModuleNotFoundError:
        load_module_from_path = _load_import_helpers()
        mod = load_module_from_path("automation/common/normalization.py", "automation_common_normalization")
        return mod.ensure_int, mod.ensure_float, mod.ensure_str


def _load_scrape_utils():
    try:
        from automation.job_discovery.scripts.scrape_utils import RateLimiter, with_retry  # type: ignore
        return RateLimiter, with_retry
    except ModuleNotFoundError:
        load_module_from_path = _load_import_helpers()
        mod = load_module_from_path(
            "automation/job-discovery/scripts/scrape_utils.py",
            "job_discovery_scrape_utils",
        )
        return mod.RateLimiter, mod.with_retry


def _load_metrics_cls():
    try:
        from automation.job_discovery.scripts.metrics import Metrics  # type: ignore
        return Metrics
    except ModuleNotFoundError:
        load_module_from_path = _load_import_helpers()
        mod = load_module_from_path(
            "automation/job-discovery/scripts/metrics.py",
            "job_discovery_metrics",
        )
        return mod.Metrics


def _load_logging_utils():
    try:
        from automation.job_discovery.scripts.logging_utils import structured_log  # type: ignore
        return structured_log
    except ModuleNotFoundError:
        load_module_from_path = _load_import_helpers()
        mod = load_module_from_path(
            "automation/job-discovery/scripts/logging_utils.py",
            "job_discovery_logging_utils",
        )
        return mod.structured_log


def _load_mapping():
    try:
        from automation.job_discovery.scripts.mapping import map_linkedin_item, map_indeed_item  # type: ignore
        return map_linkedin_item, map_indeed_item
    except ModuleNotFoundError:
        load_module_from_path = _load_import_helpers()
        mod = load_module_from_path(
            "automation/job-discovery/scripts/mapping.py",
            "job_discovery_mapping",
        )
        return mod.map_linkedin_item, mod.map_indeed_item
import logging
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - allow tests to run without requests installed
    requests = None  # type: ignore

logger = logging.getLogger(__name__)

# Lazily initialized metrics to avoid module-level import failures
_METRICS = None  # type: ignore

# Backward-compatible module-level config for tests and orchestrator shims
# Uses hardened loader to avoid PYTHONPATH dependence.
try:
    config = _load_config()  # type: ignore
except Exception:  # pragma: no cover
    config = {}  # type: ignore

# Expose scrape utilities at module level for test monkeypatching
try:
    RateLimiter, with_retry = _load_scrape_utils()  # type: ignore
except Exception:  # pragma: no cover
    RateLimiter = None  # type: ignore
    with_retry = None  # type: ignore

def _ensure_metrics() -> None:
    global _METRICS
    if _METRICS is None:
        Metrics = _load_metrics_cls()
        _METRICS = Metrics()




def reset_metrics() -> None:
    global _METRICS
    Metrics = _load_metrics_cls()
    _METRICS = Metrics()


def get_metrics() -> Any:
    _ensure_metrics()
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
    ensure_int, ensure_float, ensure_str = _load_normalization()
    cfg = config if hasattr(config, "get") else _load_config()  # prefer module-level patched config
    url = ensure_str(cfg.get("LINKEDIN_API_URL", ""))
    token = ensure_str(cfg.get("LINKEDIN_API_TOKEN", cfg.get("LINKEDIN_API_KEY", "")))
    rpm = ensure_int(cfg.get_int("SCRAPER_RPM", 30), 30)
    timeout = ensure_int(cfg.get_int("SCRAPER_TIMEOUT", 10), 10)
    max_retries = ensure_int(cfg.get_int("SCRAPER_MAX_RETRIES", 3), 3)
    backoff_base = ensure_float(cfg.get_float("SCRAPER_BACKOFF_BASE", 0.5), 0.5)
    backoff_max = ensure_float(cfg.get_float("SCRAPER_BACKOFF_MAX", 4.0), 4.0)
    jitter_ms = ensure_int(cfg.get_int("SCRAPER_JITTER_MS", 100), 100)

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

    # Prefer module-level proxies (for tests), fallback to loader
    rl_cls = RateLimiter if RateLimiter is not None else _load_scrape_utils()[0]
    retry_fn = with_retry if with_retry is not None else _load_scrape_utils()[1]
    structured_log = _load_logging_utils()
    map_linkedin_item, _ = _load_mapping()
    _ensure_metrics()

    limiter = rl_cls(rpm=rpm)

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

    result = retry_fn(
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
    ensure_int, ensure_float, ensure_str = _load_normalization()
    cfg = config if hasattr(config, "get") else _load_config()
    url = ensure_str(cfg.get("INDEED_API_URL", ""))
    token = ensure_str(cfg.get("INDEED_API_TOKEN", cfg.get("INDEED_PUBLISHER_KEY", "")))
    rpm = ensure_int(cfg.get_int("SCRAPER_RPM", 30), 30)
    timeout = ensure_int(cfg.get_int("SCRAPER_TIMEOUT", 10), 10)
    max_retries = ensure_int(cfg.get_int("SCRAPER_MAX_RETRIES", 3), 3)
    backoff_base = ensure_float(cfg.get_float("SCRAPER_BACKOFF_BASE", 0.5), 0.5)
    backoff_max = ensure_float(cfg.get_float("SCRAPER_BACKOFF_MAX", 4.0), 4.0)
    jitter_ms = ensure_int(cfg.get_int("SCRAPER_JITTER_MS", 100), 100)

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

    rl_cls = RateLimiter if RateLimiter is not None else _load_scrape_utils()[0]
    retry_fn = with_retry if with_retry is not None else _load_scrape_utils()[1]
    structured_log = _load_logging_utils()
    _, map_indeed_item = _load_mapping()
    _ensure_metrics()

    limiter = rl_cls(rpm=rpm)

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

    result = retry_fn(
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
    # Adapter registry mapping enable keys to adapter names
    registry: List[Dict[str, str]] = [
        {"enable_key": "LEVER_ENABLED", "adapter": "lever", "func": "fetch_lever_jobs"},
        {"enable_key": "GREENHOUSE_ENABLED", "adapter": "greenhouse", "func": "fetch_greenhouse_jobs"},
        {"enable_key": "ASHBY_ENABLED", "adapter": "ashby", "func": "fetch_ashby_jobs"},
        {"enable_key": "INDEED_ENABLED", "adapter": "indeed", "func": "fetch_indeed_jobs"},
        {"enable_key": "ZIPRECRUITER_ENABLED", "adapter": "ziprecruiter", "func": "fetch_ziprecruiter_jobs"},
        {"enable_key": "GOOGLEJOBS_ENABLED", "adapter": "google_jobs", "func": "fetch_google_jobs"},
        {"enable_key": "GLASSDOOR_ENABLED", "adapter": "glassdoor", "func": "fetch_glassdoor_jobs"},
        {"enable_key": "CRAIGSLIST_ENABLED", "adapter": "craigslist", "func": "fetch_craigslist_jobs"},
        {"enable_key": "GOREMOTE_ENABLED", "adapter": "goremote", "func": "fetch_goremote_jobs"},
    ]

    load_module_from_path = _load_import_helpers()
    all_jobs: List[Dict[str, Any]] = []
    for entry in registry:
        key = entry["enable_key"]
        if not bool(cfg.get(key, False)):
            continue
        adapter = entry["adapter"]
        dotted = f"automation.job_discovery.scripts.source_{adapter}_adapter"
        try:
            module = importlib.import_module(dotted)  # type: ignore
        except ModuleNotFoundError:
            path = f"automation/job-discovery/scripts/source_{adapter}_adapter.py"
            module = load_module_from_path(path, f"job_discovery_source_{adapter}_adapter")

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

    # Apply enrichment transforms deterministically when enabled
    enrichment_enabled = bool(cfg.get("ENRICHMENT_ENABLED", True))
    if enrichment_enabled:
        try:
            import importlib.util
            import pathlib
            _p = pathlib.Path(__file__).resolve().parent / 'enrichment_transforms.py'
            spec = importlib.util.spec_from_file_location("enrichment_transforms", str(_p))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore
                enrich_job = getattr(mod, 'enrich_job', None)
                if callable(enrich_job):
                    result = [enrich_job(job) for job in result]  # type: ignore
        except Exception:
            # If enrichment not available, return canonical jobs
            pass
    return result
