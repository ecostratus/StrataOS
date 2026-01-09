"""
Tests for configuration validation of job discovery scrapers.
"""
from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from config_validation import validate_job_discovery_config  # type: ignore


def test_validation_missing_urls_when_enabled():
    class Cfg:
        def get_bool(self, k, d=False):
            return True if k in ("LINKEDIN_ENABLED", "INDEED_ENABLED") else d

        def get(self, k, d=None):
            return ""  # missing URLs

        def get_int(self, k, d=0):
            return d

        def get_float(self, k, d=0.0):
            return d

    ok, errs = validate_job_discovery_config(Cfg())
    assert not ok
    assert any("LINKEDIN_API_URL" in e for e in errs)
    assert any("INDEED_API_URL" in e for e in errs)


def test_validation_numeric_bounds():
    class Cfg:
        def get_bool(self, k, d=False):
            return False

        def get(self, k, d=None):
            return d

        def get_int(self, k, d=0):
            if k == "SCRAPER_RPM":
                return 0
            if k == "SCRAPER_MAX_RETRIES":
                return 11
            if k == "SCRAPER_JITTER_MS":
                return -1
            return d

        def get_float(self, k, d=0.0):
            if k == "SCRAPER_BACKOFF_BASE":
                return 2.0
            if k == "SCRAPER_BACKOFF_MAX":
                return 1.0
            return d

    ok, errs = validate_job_discovery_config(Cfg())
    assert not ok
    assert any("SCRAPER_RPM" in e for e in errs)
    assert any("SCRAPER_MAX_RETRIES" in e for e in errs)
    assert any("Backoff" in e for e in errs)
    assert any("JITTER" in e.upper() for e in errs)


def test_validation_ok_when_disabled_and_defaults_ok():
    class Cfg:
        def get_bool(self, k, d=False):
            return False

        def get(self, k, d=None):
            return d

        def get_int(self, k, d=0):
            return d

        def get_float(self, k, d=0.0):
            return d

    ok, errs = validate_job_discovery_config(Cfg())
    assert ok
    assert errs == []
