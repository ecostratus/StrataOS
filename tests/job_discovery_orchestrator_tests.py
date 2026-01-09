"""
Unit tests for the job discovery orchestrator and CSV export.
"""

import os
import sys
import csv
from tempfile import TemporaryDirectory

# Ensure repo root and scripts dir are importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import job_discovery_v1 as orchestrator  # type: ignore
import sources  # type: ignore


def test_discover_jobs_returns_expected_shape(monkeypatch):
    # Force both sources enabled via monkeypatching config getters
    class DummyConfig:
        def get_bool(self, key, default=False):
            if key in ("LINKEDIN_ENABLED", "INDEED_ENABLED"):
                return True
            return default

    monkeypatch.setattr(orchestrator, "config", DummyConfig())

    jobs = orchestrator.discover_jobs()
    assert isinstance(jobs, list)
    assert len(jobs) >= 1
    sample = jobs[0]
    for k in ("title", "location", "company", "source", "url", "posted_date"):
        assert k in sample


def test_export_to_csv_writes_file_and_rows():
    rows = [
        {
            "title": "Senior Software Engineer - Remote",
            "location": "Remote",
            "company": "Acme Corp",
            "source": "sample",
            "url": "https://example.com/jobs/1",
            "posted_date": "2026-01-09",
        },
        {
            "title": "Data Analyst",
            "location": "New York, NY",
            "company": "DataWorks",
            "source": "sample",
            "url": "https://example.com/jobs/3",
            "posted_date": "2026-01-09",
        },
    ]
    with TemporaryDirectory() as tmp:
        out_path = orchestrator.export_to_csv(rows, tmp)
        assert os.path.exists(out_path)
        # Validate headers and row count
        with open(out_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            lines = list(reader)
            assert lines[0] == ["title", "location", "company", "source", "url", "posted_date"]
            # header + 2 rows
            assert len(lines) == 3
