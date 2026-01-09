"""
Tests for scraper utilities and config-driven scrapers.
No network calls; monkeypatch HTTP and sleep/time.
"""
from __future__ import annotations

import os
import sys
import types

# Path setup
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import scrape_utils  # type: ignore
import sources  # type: ignore


def test_with_retry_eventual_success(monkeypatch):
    attempts = {"n": 0}
    slept = []

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    result = scrape_utils.with_retry(flaky, max_retries=5, backoff_base=0.01, backoff_max=0.02, jitter_ms=0, sleep_fn=lambda s: slept.append(s))
    assert result == "ok"
    assert len(slept) >= 2  # slept at least for two failures


def test_rate_limiter_enforces_window(monkeypatch):
    # Controlled time function
    t = {"now": 1000.0}

    def now_fn():
        return t["now"]

    sleeps = []

    rl = scrape_utils.RateLimiter(rpm=2, now_fn=now_fn, sleep_fn=lambda s: sleeps.append(s))
    # First two acquisitions within the window should pass
    rl.acquire()
    rl.acquire()
    # Third should cause sleep until window reset
    rl.acquire()
    assert sleeps and sleeps[0] > 0


def test_linkedin_scraper_maps_items(monkeypatch):
    # Force use of API path by setting URL in config via monkeypatch
    class DummyConfig:
        def get(self, key, default=None):
            if key == "LINKEDIN_API_URL":
                return "http://fake.url"
            return default

        def get_int(self, key, default=0):
            return default

        def get_float(self, key, default=0.0):
            return default

    monkeypatch.setattr(sources, "config", DummyConfig())

    # Fake HTTP returning list of dicts
    monkeypatch.setattr(sources, "_http_get_json", lambda url, timeout=10: [
        {"title": "SWE", "location": "Remote", "company": "Co", "url": "http://x", "posted_date": "2026-01-09"},
        {"title": "NoLocation", "company": "Co2", "url": "http://y", "posted_date": "2026-01-09"},
    ])

    # Avoid actual sleeping
    monkeypatch.setattr(sources, "RateLimiter", lambda rpm=60: types.SimpleNamespace(acquire=lambda: None))
    monkeypatch.setattr(sources, "with_retry", lambda f, **kwargs: f())

    jobs = sources.fetch_linkedin_jobs()
    assert isinstance(jobs, list)
    assert len(jobs) == 2
    assert set(jobs[0].keys()) == {"title", "location", "company", "source", "url", "posted_date"}
    assert jobs[0]["source"] == "linkedin"


def test_indeed_scraper_fallback_on_failure(monkeypatch):
    class DummyConfig:
        def get(self, key, default=None):
            if key == "INDEED_API_URL":
                return "http://fake.url"
            return default

        def get_int(self, key, default=0):
            return default

        def get_float(self, key, default=0.0):
            return default

    monkeypatch.setattr(sources, "config", DummyConfig())

    # Simulate HTTP raising
    def boom(url, timeout=10):
        raise TimeoutError("timeout")

    monkeypatch.setattr(sources, "_http_get_json", boom)

    # with_retry returns None after retries
    def _with_retry(f, **kwargs):
        return None

    monkeypatch.setattr(sources, "with_retry", _with_retry)
    monkeypatch.setattr(sources, "RateLimiter", lambda rpm=60: types.SimpleNamespace(acquire=lambda: None))

    jobs = sources.fetch_indeed_jobs()
    assert isinstance(jobs, list)
    assert jobs == []
