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
from typing import Dict, List

# Ensure repo root on path (mirrors orchestrator behavior)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def fetch_linkedin_jobs() -> List[Dict[str, str]]:
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    # Placeholder data structure; replace with real LinkedIn fetch
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


def fetch_indeed_jobs() -> List[Dict[str, str]]:
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    # Placeholder data structure; replace with real Indeed fetch
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
