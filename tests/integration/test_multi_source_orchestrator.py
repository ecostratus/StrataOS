import importlib.util
import pathlib
import types
import pytest

# Try to import a potential orchestrator module
SRC_PATH = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts' / 'sources.py'
SPEC = importlib.util.spec_from_file_location("sources", str(SRC_PATH))
MODULE = importlib.util.module_from_spec(SPEC) if SPEC and SPEC.loader else None
if SPEC and SPEC.loader:
    SPEC.loader.exec_module(MODULE)  # type: ignore


def test_orchestrator_fetch_all_sources_presence():
    if MODULE is None or not hasattr(MODULE, 'fetch_all_sources'):
        pytest.skip("fetch_all_sources orchestrator not present; skipping integration test")

    # If present, perform a deterministic run check with minimal config
    fetch_all_sources = getattr(MODULE, 'fetch_all_sources')
    cfg = {
        "LEVER_ENABLED": True,
        "GREENHOUSE_ENABLED": True,
    }
    # Attempt two runs; expect deterministic equality and de-duplication
    a = fetch_all_sources(cfg)
    b = fetch_all_sources(cfg)
    assert a == b
    assert isinstance(a, list)
    # Optional: if adapter injected jobs collide, length should reflect de-duplication


def test_orchestrator_dedup_and_ordering(monkeypatch):
    if MODULE is None or not hasattr(MODULE, 'fetch_all_sources'):
        pytest.skip("fetch_all_sources orchestrator not present; skipping integration test")

    fetch_all_sources = getattr(MODULE, 'fetch_all_sources')

    def _lever_jobs(_cfg):
        return [{
            "job_id": "same-id",
            "title": "Software Engineer",
            "company": "Acme",
            "location": "Remote",
            "url": "https://jobs.example/acme/1",
            "source": "lever",
            "posted_at": "2026-01-09",
            "description": "",
        }]

    def _greenhouse_jobs(_cfg):
        return [{
            "job_id": "same-id",
            "title": "Software Engineer",
            "company": "Acme",
            "location": "Remote",
            "url": "https://jobs.example/acme/1",
            "source": "greenhouse",
            "posted_at": "2026-01-10",
            "description": "",
        }]

    original_import_module = MODULE.importlib.import_module

    def _fake_import_module(name: str, package=None):
        if name.endswith("source_lever_adapter"):
            return types.SimpleNamespace(fetch_lever_jobs=_lever_jobs)
        if name.endswith("source_greenhouse_adapter"):
            return types.SimpleNamespace(fetch_greenhouse_jobs=_greenhouse_jobs)
        return original_import_module(name, package)

    monkeypatch.setattr(MODULE.importlib, "import_module", _fake_import_module)

    cfg = {
        "LEVER_ENABLED": True,
        "GREENHOUSE_ENABLED": True,
    }

    out = fetch_all_sources(cfg)
    # Dedup: only one result despite two sources
    assert isinstance(out, list)
    assert len(out) == 1
    assert out[0]["title"].lower() == "software engineer"
    assert out[0]["company"].lower() == "acme"
    assert out[0]["url"] == "https://jobs.example/acme/1"

    # Deterministic ordering: single element is trivially ordered; repeat runs equal
    out2 = fetch_all_sources(cfg)
    assert out == out2

    # Gating: disable greenhouse -> still one (from lever)
    cfg2 = dict(cfg)
    cfg2["GREENHOUSE_ENABLED"] = False
    out3 = fetch_all_sources(cfg2)
    assert len(out3) == 1
