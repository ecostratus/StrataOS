"""
Error-handling tests for job discovery orchestrator.
"""

import os
import sys
import pytest

# Ensure scripts dir import path
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import job_discovery_v1 as orchestrator  # type: ignore
import sources  # type: ignore


def test_discover_jobs_handles_source_exception(monkeypatch, caplog):
    class DummyConfig:
        def get_bool(self, key, default=False):
            if key == "LINKEDIN_ENABLED":
                return True
            if key == "INDEED_ENABLED":
                return True
            return default

    def boom():
        raise TimeoutError("simulated timeout")

    monkeypatch.setattr(orchestrator, "config", DummyConfig())
    monkeypatch.setattr(sources, "fetch_linkedin_jobs", boom)
    # The other source returns malformed and valid entries
    monkeypatch.setattr(
        sources,
        "fetch_indeed_jobs",
        lambda: [
            {"title": "Bad"},  # malformed
            {
                "title": "Software Engineer",
                "location": "Remote",
                "company": "ValidCo",
                "source": "indeed",
                "url": "http://example.com",
                "posted_date": "2026-01-09",
            },
        ],
    )

    caplog.set_level("INFO")
    jobs = orchestrator.discover_jobs()
    # Should not raise
    assert isinstance(jobs, list)
    # Should contain only the valid entry
    assert len(jobs) == 1
    assert jobs[0]["company"] == "ValidCo"
    # Error logged for failing source
    assert any("failed" in rec.getMessage() for rec in caplog.records)


def test_discover_jobs_handles_empty_results(monkeypatch, caplog):
    class DummyConfig:
        def get_bool(self, key, default=False):
            return True  # enable both

    monkeypatch.setattr(orchestrator, "config", DummyConfig())
    monkeypatch.setattr(sources, "fetch_linkedin_jobs", lambda: [])
    monkeypatch.setattr(sources, "fetch_indeed_jobs", lambda: [])

    caplog.set_level("INFO")
    jobs = orchestrator.discover_jobs()
    assert isinstance(jobs, list)
    assert len(jobs) == 1  # falls back to sample


def test_discover_jobs_handles_non_list_return(monkeypatch, caplog):
    class DummyConfig:
        def get_bool(self, key, default=False):
            return True

    monkeypatch.setattr(orchestrator, "config", DummyConfig())
    # Return a dict instead of list to simulate incorrect source output
    monkeypatch.setattr(sources, "fetch_linkedin_jobs", lambda: {"oops": True})
    # Provide one valid list from indeed
    monkeypatch.setattr(
        sources,
        "fetch_indeed_jobs",
        lambda: [
            {
                "title": "Backend Engineer",
                "location": "Remote",
                "company": "Indeed LLC",
                "source": "indeed",
                "url": "http://example.com/indeed",
                "posted_date": "2026-01-09",
            }
        ],
    )

    caplog.set_level("INFO")
    jobs = orchestrator.discover_jobs()
    assert isinstance(jobs, list)
    assert len(jobs) == 1
    assert jobs[0]["source"] == "indeed"
    # Should log non-list error for linkedin
    assert any("non-list" in rec.getMessage() for rec in caplog.records)
