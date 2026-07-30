"""Tests for Greenhouse telemetry side effects from the real discovery command."""

import os
import sys
import json
from pathlib import Path

# Ensure repo root and scripts dir are importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import job_discovery_v1 as orchestrator  # type: ignore


def test_main_appends_greenhouse_telemetry_side_effect(monkeypatch, tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    telemetry_path = tmp_path / "greenhouse_week1_telemetry.jsonl"

    class DummyConfig:
        def initialize(self, json_path=None):
            return None

        def to_dict(self):
            return {
                "GREENHOUSE_ENABLED": True,
                "GREENHOUSE_TELEMETRY_PATH": str(telemetry_path),
                "SYSTEM_OUTPUT_DIRECTORY": str(out_dir),
            }

        def get_bool(self, key, default=False):
            if key == "GREENHOUSE_ENABLED":
                return True
            if key == "LOG_TO_FILE":
                return False
            if key == "LOG_SUPPRESS_STDOUT_IF_JSONL":
                return False
            return default

        def get(self, key, default=None):
            return self.to_dict().get(key, default)

        def get_list(self, key, default=None, sep=","):
            defaults = {
                "JOB_FILTER_KEYWORDS": ["software engineer"],
                "JOB_FILTER_LOCATIONS": ["Remote"],
                "JOB_FILTER_EXCLUDE_KEYWORDS": [],
            }
            return defaults.get(key, default)

        def get_int(self, key, default=None):
            return default

        def get_float(self, key, default=None):
            return default

    monkeypatch.setattr(orchestrator, "config", DummyConfig())
    monkeypatch.setattr(orchestrator.sources, "fetch_all_sources", lambda _cfg: [
        {
            "job_id": "abc123",
            "title": "Software Engineer",
            "company": "Acme",
            "location": "Remote",
            "url": "https://boards.greenhouse.io/acme/jobs/1",
            "source": "greenhouse",
            "posted_at": "2026-07-20T11:11:11+00:00",
        }
    ])

    orchestrator.main(["--out-dir", str(out_dir), "--summary-only"])

    assert telemetry_path.exists()
    lines = telemetry_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["source"] == "greenhouse"
    assert payload["success"] is True
    assert isinstance(payload["latency_ms"], (int, float))
    assert payload["empty_run_count"] == 0
    assert payload["payload_anomalies"] == 0
    assert payload["error"] is None


def test_main_appends_greenhouse_telemetry_on_failure(monkeypatch, tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    telemetry_path = tmp_path / "greenhouse_week1_telemetry.jsonl"

    class DummyConfig:
        def initialize(self, json_path=None):
            return None

        def to_dict(self):
            return {
                "GREENHOUSE_ENABLED": True,
                "GREENHOUSE_TELEMETRY_PATH": str(telemetry_path),
                "SYSTEM_OUTPUT_DIRECTORY": str(out_dir),
            }

        def get_bool(self, key, default=False):
            if key == "GREENHOUSE_ENABLED":
                return True
            if key == "LOG_TO_FILE":
                return False
            if key == "LOG_SUPPRESS_STDOUT_IF_JSONL":
                return False
            return default

        def get(self, key, default=None):
            return self.to_dict().get(key, default)

        def get_list(self, key, default=None, sep=","):
            defaults = {
                "JOB_FILTER_KEYWORDS": ["software engineer"],
                "JOB_FILTER_LOCATIONS": ["Remote"],
                "JOB_FILTER_EXCLUDE_KEYWORDS": [],
            }
            return defaults.get(key, default)

        def get_int(self, key, default=None):
            return default

        def get_float(self, key, default=None):
            return default

    monkeypatch.setattr(orchestrator, "config", DummyConfig())
    monkeypatch.setattr(orchestrator, "discover_jobs", lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    try:
        orchestrator.main(["--out-dir", str(out_dir), "--summary-only"])
        assert False, "Expected main to raise"
    except RuntimeError as exc:
        assert str(exc) == "boom"

    assert telemetry_path.exists()
    lines = telemetry_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["source"] == "greenhouse"
    assert payload["success"] is False
    assert isinstance(payload["latency_ms"], (int, float))
    assert payload["empty_run_count"] == 0
    assert payload["payload_anomalies"] == 0
    assert payload["error"] == "boom"
