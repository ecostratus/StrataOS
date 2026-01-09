"""
Phase 2C tests: structured logging, metrics, and summary artifact.
"""
from __future__ import annotations

import os
import sys
import json

import types
import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import job_discovery_v1 as orchestrator  # type: ignore
import sources  # type: ignore


def test_structured_logs_and_metrics(monkeypatch, caplog):
    # Provide config with URL to trigger API path
    class DummyConfig:
        def get(self, k, d=None):
            if k == "LINKEDIN_API_URL":
                return "http://fake.linkedin"
            return d

        def get_int(self, k, d=0):
            return d

        def get_float(self, k, d=0.0):
            return d

    monkeypatch.setattr(sources, "config", DummyConfig())

    # Reset metrics
    if hasattr(sources, "reset_metrics"):
        sources.reset_metrics()

    # Simulate one retry then success
    calls = {"n": 0}

    def fake_http(url, timeout=10):
        calls["n"] += 1
        if calls["n"] == 1:
            raise TimeoutError("boom")
        return [
            {"title": "SWE", "location": "Remote", "company": "Co", "url": "http://x", "posted_date": "2026-01-09"},
            {"title": "Bad", "company": "Co2", "url": "http://y", "posted_date": "2026-01-09"},
        ]

    monkeypatch.setattr(sources, "_http_get_json", fake_http)
    monkeypatch.setattr(sources, "RateLimiter", lambda rpm=60, on_sleep=None: types.SimpleNamespace(acquire=lambda: None))

    # with_retry that triggers one on_retry callback path
    def fake_with_retry(f, **kwargs):
        try:
            return f()
        except Exception:
            # Simulate on_retry callback
            if "on_retry" in kwargs and kwargs["on_retry"]:
                kwargs["on_retry"](1, 0.01, RuntimeError("boom"))
            return f()

    monkeypatch.setattr(sources, "with_retry", fake_with_retry)

    caplog.set_level("INFO")
    jobs = sources.fetch_linkedin_jobs()
    assert len(jobs) == 2

    # Metrics updated
    m = sources.get_metrics().to_dict()
    assert m["retries_attempted"] >= 1
    # One malformed entry due to missing location
    assert m["malformed_entries"].get("linkedin", 0) >= 1

    # Structured logs emitted (look for event keys)
    msgs = [r.getMessage() for r in caplog.records]
    assert any('"event":"scraper_error"' in s or '"event":"scraper_retry_error"' in s for s in msgs)


def test_summary_artifact_created(monkeypatch, tmp_path):
    # Configure orchestrator with minimal filters and paths
    class DummyConfig:
        def initialize(self):
            return None

        def get(self, key, default=None):
            if key == "SYSTEM_OUTPUT_DIRECTORY":
                return str(tmp_path)
            return default

        def get_list(self, key, default=None):
            if key == "JOB_FILTER_KEYWORDS":
                return ["engineer"]
            if key == "JOB_FILTER_LOCATIONS":
                return ["remote"]
            if key == "JOB_FILTER_EXCLUDE_KEYWORDS":
                return []
            return default or []

        def get_bool(self, key, default=False):
            return False

    monkeypatch.setattr(orchestrator, "config", DummyConfig())

    # Fixed ts
    class FixedDT:
        @staticmethod
        def now(tz):  # tz unused in fake
            class T:
                def strftime(self, fmt):
                    return "20260109_050607"

                def isoformat(self):
                    return "2026-01-09T05:06:07+00:00"
            return T()

    monkeypatch.setattr(orchestrator, "datetime", FixedDT)

    # Provide jobs to export (already filtered by keywords/locations)
    monkeypatch.setattr(orchestrator, "discover_jobs", lambda: [
        {"title": "Engineer - Remote", "location": "Remote", "company": "A", "source": "x", "url": "http://a", "posted_date": "2026-01-09"}
    ])

    orchestrator.main([])

    # Check CSV and summary exist
    csv_path = tmp_path / "jobs_discovered_20260109_050607.csv"
    summary_path = tmp_path / "jobs_discovered_20260109_050607.summary.json"
    assert csv_path.exists()
    assert summary_path.exists()

    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert "counts" in data and data["counts"]["exported"] == 1
    assert "enabled_sources" in data
