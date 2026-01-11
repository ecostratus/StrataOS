import importlib.util
import pathlib
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


def test_orchestrator_dedup_and_ordering():
    if MODULE is None or not hasattr(MODULE, 'fetch_all_sources'):
        pytest.skip("fetch_all_sources orchestrator not present; skipping integration test")

    fetch_all_sources = getattr(MODULE, 'fetch_all_sources')

    # Import adapters to inject test jobs
    import importlib.util
    base = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts'

    # Lever injection
    lever_path = base / 'source_lever_adapter.py'
    spec_lever = importlib.util.spec_from_file_location("source_lever_adapter", str(lever_path))
    lever_mod = importlib.util.module_from_spec(spec_lever)
    assert spec_lever and spec_lever.loader
    spec_lever.loader.exec_module(lever_mod)  # type: ignore

    # Greenhouse injection
    gh_path = base / 'source_greenhouse_adapter.py'
    spec_gh = importlib.util.spec_from_file_location("source_greenhouse_adapter", str(gh_path))
    gh_mod = importlib.util.module_from_spec(spec_gh)
    assert spec_gh and spec_gh.loader
    spec_gh.loader.exec_module(gh_mod)  # type: ignore

    # Same canonical fields across sources -> same job_id
    lever_mod.raw_jobs = [  # type: ignore
        {"text": "Software Engineer", "company": "Acme", "categories": {"location": "Remote"}, "hostedUrl": "https://jobs.example/acme/1", "createdAt": "2026-01-09"}
    ]
    gh_mod.raw_jobs = [  # type: ignore
        {"title": "Software Engineer", "company": "Acme", "location": {"name": "Remote"}, "absolute_url": "https://jobs.example/acme/1", "updated_at": "2026-01-10"}
    ]

    cfg = {
        "LEVER_ENABLED": True,
        "LEVER_API_URL": "https://lever.test",
        "GREENHOUSE_ENABLED": True,
        "GREENHOUSE_API_URL": "https://gh.test",
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
