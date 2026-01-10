"""
Mapping tests using JSON fixtures.
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

import sources  # type: ignore

_FIXTURES = os.path.join(_REPO_ROOT, "tests", "fixtures")


def _load_fixture(name: str):
    p = os.path.join(_FIXTURES, name)
    return json.loads(open(p, "r", encoding="utf-8").read())


def test_linkedin_fixture_mapping(monkeypatch):
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
    monkeypatch.setattr(sources, "RateLimiter", lambda rpm=60, on_sleep=None: types.SimpleNamespace(acquire=lambda: None))
    monkeypatch.setattr(sources, "with_retry", lambda f, **kwargs: f())

    data = _load_fixture("linkedin_payload.json")
    monkeypatch.setattr(sources, "_http_get_json", lambda url, timeout=10, headers=None: data)

    # Reset metrics
    sources.reset_metrics()
    jobs = sources.fetch_linkedin_jobs()
    assert isinstance(jobs, list) and len(jobs) == 2
    assert jobs[0]["posted_date"] == "2026-01-09"
    m = sources.get_metrics().to_dict()
    assert m["jobs_fetched"].get("linkedin", 0) == 2
    assert m["malformed_entries"].get("linkedin", 0) >= 1


def test_indeed_fixture_mapping(monkeypatch):
    class DummyConfig:
        def get(self, k, d=None):
            if k == "INDEED_API_URL":
                return "http://fake.indeed"
            return d

        def get_int(self, k, d=0):
            return d

        def get_float(self, k, d=0.0):
            return d

    monkeypatch.setattr(sources, "config", DummyConfig())
    monkeypatch.setattr(sources, "RateLimiter", lambda rpm=60, on_sleep=None: types.SimpleNamespace(acquire=lambda: None))
    monkeypatch.setattr(sources, "with_retry", lambda f, **kwargs: f())

    data = _load_fixture("indeed_payload.json")
    monkeypatch.setattr(sources, "_http_get_json", lambda url, timeout=10, headers=None: data)

    sources.reset_metrics()
    jobs = sources.fetch_indeed_jobs()
    assert isinstance(jobs, list) and len(jobs) == 2
    assert jobs[1]["posted_date"] == "2026-01-07"
    assert jobs[1]["location"] == "Remote"


def test_malformed_fixture_counts(monkeypatch):
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
    monkeypatch.setattr(sources, "RateLimiter", lambda rpm=60, on_sleep=None: types.SimpleNamespace(acquire=lambda: None))
    monkeypatch.setattr(sources, "with_retry", lambda f, **kwargs: f())

    data = _load_fixture("malformed_payload.json")
    monkeypatch.setattr(sources, "_http_get_json", lambda url, timeout=10, headers=None: data)

    sources.reset_metrics()
    jobs = sources.fetch_linkedin_jobs()
    assert isinstance(jobs, list) and len(jobs) == 2
    m = sources.get_metrics().to_dict()
    assert m["malformed_entries"].get("linkedin", 0) >= 1
