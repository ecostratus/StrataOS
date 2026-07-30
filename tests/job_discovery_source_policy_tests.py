"""Tests for source compliance policy enforcement in fetch_all_sources."""

import os
import sys
import json
import types
from pathlib import Path

# Ensure repo root and scripts dir are importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "automation", "job-discovery", "scripts")
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import sources  # type: ignore
import job_discovery_v1 as orchestrator  # type: ignore


def test_policy_blocks_disallowed_enabled_source(tmp_path):
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "enforce": True,
                "allowed_sources": ["greenhouse"],
                "sources": {
                    "lever": {"allowed": False},
                    "greenhouse": {"allowed": True},
                },
            }
        ),
        encoding="utf-8",
    )

    cfg = {
        "SOURCE_COMPLIANCE_POLICY_PATH": str(policy_path),
        "LEVER_ENABLED": True,
        "GREENHOUSE_ENABLED": False,
    }

    try:
        sources.fetch_all_sources(cfg)
        assert False, "Expected policy enforcement to block lever"
    except ValueError as e:
        assert "blocked enabled sources" in str(e)
        assert "lever" in str(e)


def test_policy_allows_enabled_source(tmp_path, monkeypatch):
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "enforce": True,
                "allowed_sources": ["greenhouse"],
                "sources": {
                    "greenhouse": {"allowed": True},
                },
            }
        ),
        encoding="utf-8",
    )

    fake_module = types.SimpleNamespace(
        fetch_greenhouse_jobs=lambda _cfg: [
            {
                "job_id": "abc123",
                "title": "Software Engineer",
                "company": "Acme",
                "location": "Remote",
                "url": "https://boards.greenhouse.io/acme/jobs/1",
                "source": "greenhouse",
                "posted_at": "2026-07-20",
            }
        ]
    )
    monkeypatch.setattr(sources.importlib, "import_module", lambda _name: fake_module)

    cfg = {
        "SOURCE_COMPLIANCE_POLICY_PATH": str(policy_path),
        "GREENHOUSE_ENABLED": True,
        "GREENHOUSE_API_URL": "https://boards-api.greenhouse.io/v1/boards/acme/jobs",
    }

    out = sources.fetch_all_sources(cfg)
    assert isinstance(out, list)
    assert len(out) == 1
    assert out[0]["source"] == "greenhouse"


def test_policy_blocks_linkedin_when_enabled(tmp_path, monkeypatch):
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "enforce": True,
                "sources": {
                    "linkedin": {"allowed": False},
                    "greenhouse": {"allowed": True},
                },
            }
        ),
        encoding="utf-8",
    )

    class DummyConfig:
        def to_dict(self):
            return {
                "SOURCE_COMPLIANCE_POLICY_PATH": str(policy_path),
                "LINKEDIN_ENABLED": True,
                "INDEED_ENABLED": False,
            }

        def get_bool(self, key, default=False):
            return bool(self.to_dict().get(key, default))

        def get(self, key, default=None):
            return self.to_dict().get(key, default)

    monkeypatch.setattr(orchestrator, "config", DummyConfig())

    try:
        orchestrator.discover_jobs()
        assert False, "Expected policy enforcement to block linkedin"
    except ValueError as e:
        message = str(e)
        assert "blocked enabled sources" in message
        assert "linkedin" in message


def test_policy_blocks_indeed_when_enabled(tmp_path):
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "enforce": True,
                "sources": {
                    "indeed": {"allowed": False},
                    "greenhouse": {"allowed": True},
                },
            }
        ),
        encoding="utf-8",
    )

    cfg = {
        "SOURCE_COMPLIANCE_POLICY_PATH": str(policy_path),
        "INDEED_ENABLED": True,
    }

    try:
        sources.fetch_all_sources(cfg)
        assert False, "Expected policy enforcement to block indeed"
    except ValueError as e:
        message = str(e)
        assert "blocked enabled sources" in message
        assert "indeed" in message


def test_repo_default_policy_denies_linkedin_and_indeed():
    policy_path = Path(__file__).resolve().parents[1] / "config" / "source_compliance_policy.json"
    payload = json.loads(policy_path.read_text(encoding="utf-8"))

    assert payload.get("enforce") is True
    src = payload.get("sources", {})
    assert isinstance(src, dict)
    assert src.get("linkedin", {}).get("allowed") is False
    assert src.get("indeed", {}).get("allowed") is False


def test_orchestrator_uses_default_policy_path_for_legacy_sources(monkeypatch):
    class DummyConfig:
        def to_dict(self):
            # Intentionally omit SOURCE_COMPLIANCE_POLICY_PATH so orchestrator
            # uses its default of config/source_compliance_policy.json.
            return {
                "LINKEDIN_ENABLED": True,
                "INDEED_ENABLED": False,
            }

        def get_bool(self, key, default=False):
            return bool(self.to_dict().get(key, default))

        def get(self, key, default=None):
            return self.to_dict().get(key, default)

    monkeypatch.setattr(orchestrator, "config", DummyConfig())

    try:
        orchestrator.discover_jobs()
        assert False, "Expected default compliance policy to block linkedin"
    except ValueError as e:
        message = str(e)
        assert "blocked enabled sources" in message
        assert "linkedin" in message
