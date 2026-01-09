"""
End-to-end integration tests for the job discovery pipeline.
Covers config-driven enable/disable, rate limit + retry behavior, filtering,
malformed entry handling, spec-shaped jobs, and deterministic CSV export.
"""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path

import pytest

# Path setup
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import job_discovery_v1 as orchestrator  # type: ignore
import sources  # type: ignore
from filters import normalize_terms, matches_filters  # type: ignore


def test_config_enable_disable_and_malformed_filtered(monkeypatch):
    # Enable only LinkedIn
    class DummyConfig:
        def get_bool(self, key, default=False):
            return key == "LINKEDIN_ENABLED"

    monkeypatch.setattr(orchestrator, "config", DummyConfig())

    # Return one valid and one malformed entry from LinkedIn
    def fake_linkedin():
        return [
            {
                "title": "Software Engineer",
                "location": "Remote",
                "company": "Co",
                "source": "linkedin",
                "url": "http://x",
                "posted_date": "2026-01-09",
            },
            {"title": "Bad"},
        ]

    monkeypatch.setattr(sources, "fetch_linkedin_jobs", fake_linkedin)
    # Ensure indeed isn't used
    monkeypatch.setattr(sources, "fetch_indeed_jobs", lambda: pytest.fail("indeed should be disabled"))

    jobs = orchestrator.discover_jobs()
    assert isinstance(jobs, list)
    # Only the valid entry should remain after orchestrator validation
    assert len(jobs) == 1
    j = jobs[0]
    assert set(j.keys()) == {"title", "location", "company", "source", "url", "posted_date"}
    assert j["source"] == "linkedin"


def test_rate_limit_and_retry_in_scraper(monkeypatch):
    # Force LinkedIn to use API path by providing a URL via sources.config
    class DummyConfig:
        def get(self, key, default=None):
            if key == "LINKEDIN_API_URL":
                return "http://fake.linkedin"
            return default

        def get_int(self, key, default=0):
            return default

        def get_float(self, key, default=0.0):
            return default

    monkeypatch.setattr(sources, "config", DummyConfig())

    # Track acquire calls
    acquires = {"n": 0}

    class FakeRL:
        def __init__(self, rpm=60):
            pass

        def acquire(self):
            acquires["n"] += 1

    monkeypatch.setattr(sources, "RateLimiter", lambda rpm=60: FakeRL(rpm))

    # Simulate one failure then success from HTTP layer
    calls = {"n": 0}

    def fake_http(url, timeout=10):
        calls["n"] += 1
        if calls["n"] == 1:
            raise TimeoutError("boom")
        return [
            {"title": "SWE", "location": "Remote", "company": "Co", "url": "http://x", "posted_date": "2026-01-09"}
        ]

    monkeypatch.setattr(sources, "_http_get_json", fake_http)

    # Use with_retry that actually retries once without sleeping
    def fake_with_retry(f, **kwargs):
        try:
            return f()
        except Exception:
            return f()

    monkeypatch.setattr(sources, "with_retry", fake_with_retry)

    jobs = sources.fetch_linkedin_jobs()
    assert acquires["n"] >= 1  # rate limiter was invoked
    assert isinstance(jobs, list) and len(jobs) == 1


def test_main_filters_and_csv_export_deterministic(monkeypatch, tmp_path):
    # Provide deterministic filters via config and fixed timestamp
    class DummyConfig:
        def initialize(self):
            return None

        def get(self, key, default=None):
            if key == "SYSTEM_ENVIRONMENT":
                return "test"
            if key == "SYSTEM_LOG_LEVEL":
                return "INFO"
            if key == "SYSTEM_OUTPUT_DIRECTORY":
                return str(tmp_path)
            if key == "JOB_FILTER_KEYWORDS":
                return None
            return default

        def get_list(self, key, default=None):
            if key == "JOB_FILTER_KEYWORDS":
                return ["engineer"]
            if key == "JOB_FILTER_LOCATIONS":
                return ["remote"]
            if key == "JOB_FILTER_EXCLUDE_KEYWORDS":
                return ["volunteer"]
            return default or []

        def get_bool(self, key, default=False):
            # No fetching; we'll stub discover_jobs directly
            return False

    monkeypatch.setattr(orchestrator, "config", DummyConfig())

    # Fixed timestamp for deterministic filename
    class FixedDT:
        @staticmethod
        def now(tz):  # tz unused in this fake
            class T:
                def strftime(self, fmt):
                    return "20260109_010203"
            return T()

    monkeypatch.setattr(orchestrator, "datetime", FixedDT)

    # Provide known jobs for filtering
    jobs = [
        {
            "title": "Senior Software Engineer - Remote",
            "location": "Remote",
            "company": "A",
            "source": "sample",
            "url": "http://a",
            "posted_date": "2026-01-09",
        },
        {
            "title": "Volunteer Engineer",
            "location": "Remote",
            "company": "B",
            "source": "sample",
            "url": "http://b",
            "posted_date": "2026-01-09",
        },
    ]
    monkeypatch.setattr(orchestrator, "discover_jobs", lambda: jobs)

    # Run main to generate CSV
    orchestrator.main(["--out-dir", str(tmp_path)])

    # Assert deterministic filename exists
    expected = tmp_path / "jobs_discovered_20260109_010203.csv"
    assert expected.exists()

    # Check CSV content
    content = expected.read_text(encoding="utf-8").strip().splitlines()
    # Header + one matched row (volunteer excluded)
    assert content[0].split(",") == ["title", "location", "company", "source", "url", "posted_date"]
    assert len(content) == 2
