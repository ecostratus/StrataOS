import os
from pathlib import Path

import pytest

from automation.job-discovery.scripts import job_discovery_v1 as orchestrator


class FakeConfig:
    def __init__(self, out_dir: str, retention_enabled: bool = False, backend: str = "sqlite"):
        self._out_dir = out_dir
        self._retention_enabled = retention_enabled
        self._backend = backend

    def initialize(self):
        return None

    def get_bool(self, key, default=False):
        # Disable external sources to use fallback sample
        if key in ("LINKEDIN_ENABLED", "INDEED_ENABLED"):
            return False
        if key == "LOG_TO_FILE":
            return False
        if key == "LOG_SUPPRESS_STDOUT_IF_JSONL":
            return False
        return default

    def get_list(self, key, default=None):
        return default or []

    def get(self, key, default=None):
        if key == "SYSTEM_OUTPUT_DIRECTORY":
            return self._out_dir
        if key == "SYSTEM_ENVIRONMENT":
            return "test"
        if key == "SYSTEM_LOG_LEVEL":
            return "INFO"
        if key == "RETENTION":
            return {"enabled": self._retention_enabled, "days": 30, "keep_latest_n_runs": 3}
        if key == "STORAGE":
            return {"backend": self._backend}
        if key == "SCORING":
            return {"weights": {}, "thresholds": {"exceptional": 0.8, "strong": 0.6, "moderate": 0.4}}
        return default

    def to_dict(self):
        return {
            "SYSTEM_OUTPUT_DIRECTORY": self._out_dir,
            "RETENTION": {"enabled": self._retention_enabled, "days": 30, "keep_latest_n_runs": 3},
            "STORAGE": {"backend": self._backend},
        }


@pytest.fixture
def tmp_out_dir(tmp_path):
    d = tmp_path / "out"
    d.mkdir()
    return str(d)


def test_orchestrator_runs_with_schedule_and_summary_only(monkeypatch, tmp_out_dir):
    fake = FakeConfig(tmp_out_dir)
    monkeypatch.setattr(orchestrator, "config", fake)
    orchestrator.main(["--schedule", "--summary-only", "--out-dir", tmp_out_dir])


def test_orchestrator_runs_with_retention_enabled_sqlite(monkeypatch, tmp_out_dir):
    fake = FakeConfig(tmp_out_dir, retention_enabled=True, backend="sqlite")
    monkeypatch.setattr(orchestrator, "config", fake)
    orchestrator.main(["--schedule", "--out-dir", tmp_out_dir])
    # Summary file exists
    files = list(Path(tmp_out_dir).glob("*.summary.json"))
    assert files, "Summary JSON should be exported"


def test_orchestrator_runs_enrichment_and_scoring(monkeypatch, tmp_out_dir):
    fake = FakeConfig(tmp_out_dir)
    monkeypatch.setattr(orchestrator, "config", fake)
    orchestrator.main(["--enrich", "--out-dir", tmp_out_dir])
    # Enriched and scored artifacts should exist
    enriched = list(Path(tmp_out_dir).glob("jobs_enriched_*.json"))
    scored = list(Path(tmp_out_dir).glob("jobs_scored_*.csv"))
    assert enriched, "Enriched JSON should be exported"
    assert scored, "Scored CSV should be exported"
