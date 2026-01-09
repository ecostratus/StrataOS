"""
Job Discovery Orchestrator v1

Loads configuration, calls per-source fetchers, applies filtering, and exports
discovered jobs. Designed to be extended to real scrapers per scraper-spec.
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime
try:  # Python 3.11+
    from datetime import UTC  # type: ignore
except Exception:  # Python <3.11
    from datetime import timezone as _tz  # type: ignore
    UTC = _tz.utc  # type: ignore
from typing import Dict, List, Callable, Any, Optional
import argparse
import logging
import json

# Ensure repo root on path to import config and filters
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config  # type: ignore

# Add scripts dir to path to import modules despite hyphen in folder name
_SCRIPTS_DIR = os.path.join(_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from filters import normalize_terms, matches_filters  # type: ignore
import sources  # type: ignore
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

REQUIRED_KEYS = {"title", "location", "company", "source", "url", "posted_date"}


def _validate_job(job: Dict[str, Any]) -> bool:
    if not isinstance(job, dict):
        return False
    if not REQUIRED_KEYS.issubset(job.keys()):
        return False
    # ensure string-like values
    for k in REQUIRED_KEYS:
        v = job.get(k)
        if v is None:
            return False
        # Allow non-string values but coerce later; for now require str-like
        if not isinstance(v, (str, int, float)):
            return False
    return True


def _safe_fetch(name: str, func: Callable[[], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    try:
        res = func()
        if not isinstance(res, list):
            logger.error("source '%s' returned non-list result", name)
            return []
        valid = [j for j in res if _validate_job(j)]
        invalid = len(res) - len(valid)
        if invalid:
            logger.warning("source '%s' returned %d invalid jobs", name, invalid)
        return valid
    except Exception:
        logger.error("source '%s' failed", name, exc_info=True)
        return []


def discover_jobs() -> List[Dict[str, str]]:
    """Collect jobs from enabled sources. Each job has keys:
    title, location, company, source, url, posted_date (YYYY-MM-DD).
    """
    jobs: List[Dict[str, str]] = []
    if config.get_bool("LINKEDIN_ENABLED", False):
        jobs.extend(_safe_fetch("linkedin", sources.fetch_linkedin_jobs))
    if config.get_bool("INDEED_ENABLED", True):
        jobs.extend(_safe_fetch("indeed", sources.fetch_indeed_jobs))
    if not jobs:
        # Fallback minimal placeholder (kept for bootstrapping)
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        jobs = [
            {
                "title": "Senior Software Engineer - Remote",
                "location": "Remote",
                "company": "Acme Corp",
                "source": "sample",
                "url": "https://example.com/jobs/1",
                "posted_date": today,
            }
        ]
    return jobs


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def export_to_csv(rows: List[Dict[str, str]], out_dir: str) -> str:
    ensure_dir(out_dir)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"jobs_discovered_{ts}.csv")
    fieldnames = [
        "title",
        "location",
        "company",
        "source",
        "url",
        "posted_date",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    return path


def export_to_csv_with_ts(rows: List[Dict[str, str]], out_dir: str, ts: str) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"jobs_discovered_{ts}.csv")
    fieldnames = [
        "title",
        "location",
        "company",
        "source",
        "url",
        "posted_date",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    return path


def export_summary(out_dir: str, ts: str, summary: Dict[str, Any]) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"jobs_discovered_{ts}.summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, separators=(",", ":"))
    return path


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Job discovery orchestrator")
    parser.add_argument("--out-dir", dest="out_dir", default=None, help="Override output directory")
    args = parser.parse_args(argv)

    config.initialize()

    environment = config.get("SYSTEM_ENVIRONMENT", "development")
    log_level = config.get("SYSTEM_LOG_LEVEL", "INFO")
    out_dir = args.out_dir or config.get("SYSTEM_OUTPUT_DIRECTORY", "output")

    # Filters from config
    keywords = normalize_terms(config.get_list("JOB_FILTER_KEYWORDS", ["software engineer", "developer"]) or [])
    locations = normalize_terms(config.get_list("JOB_FILTER_LOCATIONS", ["Remote"]) or [])
    exclude = normalize_terms(config.get_list("JOB_FILTER_EXCLUDE_KEYWORDS", ["volunteer"]) or [])

    print("Job discovery v1 — starting")
    print(
        f"Env: {environment} | Log: {log_level} | "
        f"Keywords: {', '.join(keywords) or '-'} | Locations: {', '.join(locations) or '-'} | Exclude: {', '.join(exclude) or '-'}"
    )

    # Reset per-run source metrics
    if hasattr(sources, "reset_metrics"):
        sources.reset_metrics()

    # Fetch and filter
    jobs = discover_jobs()
    matched: List[Dict[str, str]] = []
    for job in jobs:
        if matches_filters(job.get("title", ""), job.get("location", ""), keywords, locations, exclude):
            matched.append(job)

    print(f"Found {len(jobs)} jobs; {len(matched)} matched filters")
    # Single timestamp for CSV + summary for determinism
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_csv = export_to_csv_with_ts(matched, out_dir, ts)

    # Build summary artifact
    enabled_sources = {
        "linkedin": bool(config.get_bool("LINKEDIN_ENABLED", False)),
        "indeed": bool(config.get_bool("INDEED_ENABLED", True)),
    }
    per_source = {}
    if hasattr(sources, "get_metrics"):
        m = sources.get_metrics().to_dict()
        per_source = {
            "jobs_fetched": m.get("jobs_fetched", {}),
            "malformed_entries": m.get("malformed_entries", {}),
            "retries_attempted": m.get("retries_attempted", 0),
            "rate_limit_sleeps": m.get("rate_limit_sleeps", 0),
            "scraper_failures": m.get("scraper_failures", 0),
        }

    filtered_out = max(0, len(jobs) - len(matched))
    summary = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "enabled_sources": enabled_sources,
        "counts": {
            "total_discovered": len(jobs),
            "filtered_out": filtered_out,
            "exported": len(matched),
        },
        "per_source": per_source,
    }
    out_json = export_summary(out_dir, ts, summary)
    print(f"Exported matched jobs to: {out_csv}\nSummary: {out_json}")


if __name__ == "__main__":
    main()
