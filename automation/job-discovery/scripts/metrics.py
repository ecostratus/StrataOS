"""
Lightweight metrics for job discovery pipeline.
"""
from __future__ import annotations

from typing import Dict, Any


class Metrics:
    def __init__(self) -> None:
        self.retries_attempted = 0
        self.rate_limit_sleeps = 0
        self.scraper_failures = 0
        self.jobs_fetched: Dict[str, int] = {}
        self.malformed_entries: Dict[str, int] = {}

    def inc_jobs(self, source: str, n: int) -> None:
        self.jobs_fetched[source] = self.jobs_fetched.get(source, 0) + int(n)

    def inc_malformed(self, source: str, n: int) -> None:
        self.malformed_entries[source] = self.malformed_entries.get(source, 0) + int(n)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retries_attempted": self.retries_attempted,
            "rate_limit_sleeps": self.rate_limit_sleeps,
            "scraper_failures": self.scraper_failures,
            "jobs_fetched": dict(self.jobs_fetched),
            "malformed_entries": dict(self.malformed_entries),
        }
