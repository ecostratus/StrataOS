"""
Job Discovery Orchestrator v1

Loads configuration, applies simple filtering, and exports discovered jobs.
This is a starter pipeline you can extend to call real scrapers per scraper-spec.
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime
from typing import Dict, List

# Ensure repo root on path to import config and filters
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config  # type: ignore

# Add scripts dir to path to import filters.py despite hyphen in folder name
_SCRIPTS_DIR = os.path.join(_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from filters import normalize_terms, matches_filters  # type: ignore


def fetch_sample_jobs() -> List[Dict[str, str]]:
    """Placeholder job fetcher. Replace with real scraping per scraper-spec.md.

    Each job dict should include: title, location, company, source, url, posted_date.
    """
    return [
        {
            "title": "Senior Software Engineer - Remote",
            "location": "Remote",
            "company": "Acme Corp",
            "source": "sample",
            "url": "https://example.com/jobs/1",
            "posted_date": datetime.utcnow().strftime("%Y-%m-%d"),
        },
        {
            "title": "Volunteer Developer Internship",
            "location": "San Francisco, CA",
            "company": "Helping Hands",
            "source": "sample",
            "url": "https://example.com/jobs/2",
            "posted_date": datetime.utcnow().strftime("%Y-%m-%d"),
        },
        {
            "title": "Data Analyst",
            "location": "New York, NY",
            "company": "DataWorks",
            "source": "sample",
            "url": "https://example.com/jobs/3",
            "posted_date": datetime.utcnow().strftime("%Y-%m-%d"),
        },
    ]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def export_to_csv(rows: List[Dict[str, str]], out_dir: str) -> str:
    ensure_dir(out_dir)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
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


def main() -> None:
    config.initialize()

    environment = config.get("SYSTEM_ENVIRONMENT", "development")
    log_level = config.get("SYSTEM_LOG_LEVEL", "INFO")
    out_dir = config.get("SYSTEM_OUTPUT_DIRECTORY", "output")

    # Filters from config
    keywords = normalize_terms(config.get_list("JOB_FILTER_KEYWORDS", ["software engineer", "developer"]) or [])
    locations = normalize_terms(config.get_list("JOB_FILTER_LOCATIONS", ["Remote"]) or [])
    exclude = normalize_terms(config.get_list("JOB_FILTER_EXCLUDE_KEYWORDS", ["volunteer"]) or [])

    print("Job discovery v1 — starting")
    print(
        f"Env: {environment} | Log: {log_level} | "
        f"Keywords: {', '.join(keywords) or '-'} | Locations: {', '.join(locations) or '-'} | Exclude: {', '.join(exclude) or '-'}"
    )

    # Fetch and filter
    jobs = fetch_sample_jobs()
    matched: List[Dict[str, str]] = []
    for job in jobs:
        if matches_filters(job.get("title", ""), job.get("location", ""), keywords, locations, exclude):
            matched.append(job)

    print(f"Found {len(jobs)} jobs; {len(matched)} matched filters")
    out_csv = export_to_csv(matched, out_dir)
    print(f"Exported matched jobs to: {out_csv}")


if __name__ == "__main__":
    main()
