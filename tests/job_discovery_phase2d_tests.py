"""
Phase 2D tests: JSONL log emission and real payload mapping.
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


def test_logs_emitted_to_jsonl(monkeypatch, tmp_path):
    # Enable log-to-file and fixed timestamp
    class DummyConfig:
        def initialize(self):
            return None

        def get(self, k, d=None):
            if k == "SYSTEM_OUTPUT_DIRECTORY":
                return str(tmp_path)
            return d

        def get_bool(self, k, d=False):
            if k == "LOG_TO_FILE":
                return True
            return d

        def get_list(self, k, d=None):
            return d or []

    monkeypatch.setattr(orchestrator, "config", DummyConfig())

    class FixedDT:
        @staticmethod
        def now(tz):
            class T:
                def strftime(self, fmt):
                    return "20260109_111213"

                def isoformat(self):
                    return "2026-01-09T11:12:13+00:00"
            return T()

    monkeypatch.setattr(orchestrator, "datetime", FixedDT)

    # Cause scrapers to emit structured logs by returning malformed entry
    monkeypatch.setattr(orchestrator, "discover_jobs", lambda: [
        {"title": "Engineer", "location": "Remote", "company": "Co", "source": "x", "url": "http://x", "posted_date": "2026-01-09"}
    ])

    orchestrator.main([])

    sink = tmp_path / "run-20260109_111213.jsonl"
    assert sink.exists()
    lines = sink.read_text(encoding="utf-8").strip().splitlines()
    # Ensure JSON lines parse and contain known keys
    for line in lines:
        obj = json.loads(line)
        assert "ts" in obj and "event" in obj and "level" in obj


def test_real_json_mapping_and_metrics(monkeypatch):
    # Force LinkedIn to use API path and provide token
    class DummyConfig:
        def get(self, k, d=None):
            if k == "LINKEDIN_API_URL":
                return "http://fake.linkedin"
            if k == "LINKEDIN_API_TOKEN":
                return "token"
            return d

        def get_int(self, k, d=0):
            return d

        def get_float(self, k, d=0.0):
            return d

    monkeypatch.setattr(sources, "config", DummyConfig())

    # Reset metrics
    if hasattr(sources, "reset_metrics"):
        sources.reset_metrics()

    # Provide mixed payload
    monkeypatch.setattr(sources, "_http_get_json", lambda url, timeout=10, headers=None: [
        {"title": "SWE", "location": "REMOTE", "company": "Co", "url": "http://x", "posted_date": "2026-01-09T00:00:00Z"},
        {"title": "Bad", "company": "Co2", "url": "http://y", "posted_date": "2026-01-09"},
    ])
    monkeypatch.setattr(sources, "RateLimiter", lambda rpm=60, on_sleep=None: types.SimpleNamespace(acquire=lambda: None))
    monkeypatch.setattr(sources, "with_retry", lambda f, **kwargs: f())

    jobs = sources.fetch_linkedin_jobs()
    assert isinstance(jobs, list) and len(jobs) == 2
    assert jobs[0]["posted_date"] == "2026-01-09"  # normalized

    m = sources.get_metrics().to_dict()
    assert m["jobs_fetched"].get("linkedin", 0) == 2
    assert m["malformed_entries"].get("linkedin", 0) >= 1
