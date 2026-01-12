from __future__ import annotations

from pathlib import Path

from automation.common.import_helpers import load_module_from_path


def test_dynamic_import_sources_module():
    """
    Ensure sources.py can be loaded via path-based import and exposes fetch_all_sources.
    """
    mod = load_module_from_path(
        "automation/job-discovery/scripts/sources.py",
        "job_discovery_sources",
    )
    assert hasattr(mod, "fetch_all_sources")


def test_dynamic_import_scrape_utils_module():
    """
    Ensure scrape_utils.py can be loaded dynamically and exposes RateLimiter and with_retry.
    """
    mod = load_module_from_path(
        "automation/job-discovery/scripts/scrape_utils.py",
        "job_discovery_scrape_utils",
    )
    assert hasattr(mod, "RateLimiter")
    assert hasattr(mod, "with_retry")


def test_dynamic_import_filters_module():
    """
    Ensure filters.py can be loaded dynamically and exposes filter_jobs.
    """
    mod = load_module_from_path(
        "automation/job-discovery/scripts/filters.py",
        "job_discovery_filters",
    )
    assert hasattr(mod, "filter_jobs")


def test_dynamic_adapter_loading():
    """
    Ensure each adapter module can be loaded via path-based import and exposes at least one fetch_* function.
    """
    adapters_dir = Path("automation/job-discovery/scripts")
    for path in adapters_dir.glob("source_*_adapter.py"):
        adapter = path.name.removeprefix("source_").removesuffix("_adapter.py")
        module_name = f"job_discovery_source_{adapter}_adapter"
        mod = load_module_from_path(
            f"automation/job-discovery/scripts/{path.name}",
            module_name,
        )
        has_fetch = any(
            callable(getattr(mod, name)) and name.startswith("fetch_")
            for name in dir(mod)
        )
        assert has_fetch


def test_run_prompts_full_sources_smoke(tmp_path):
    """
    Smoke test: ensure run_prompts.py can be invoked in a way that uses sources.fetch_all_sources
    without requiring PYTHONPATH. We avoid monkeypatching by relying on config flags returning
    empty and letting scripts fallback to sample jobs.
    """
    run_prompts_mod = load_module_from_path(
        "automation/common/run_prompts.py",
        "automation_common_run_prompts",
    )
    # Use sample contexts and outputs under tmp_path to avoid collisions
    outreach_ctx = "config/outreach_context.sample.json"
    resume_ctx = "config/resume_context.sample.json"
    outreach_outdir = tmp_path / "outreach"
    resume_outdir = tmp_path / "resume"
    outreach_outdir.mkdir(parents=True, exist_ok=True)
    resume_outdir.mkdir(parents=True, exist_ok=True)

    rc = run_prompts_mod.run(
        outreach_ctx=str(outreach_ctx),
        outreach_outdir=str(outreach_outdir),
        resume_ctx=str(resume_ctx),
        resume_outdir=str(resume_outdir),
        outreach_prompt=None,
        resume_prompt=None,
        no_sources=False,
    )
    assert rc == 0
