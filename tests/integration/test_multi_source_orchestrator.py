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
