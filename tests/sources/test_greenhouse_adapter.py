import importlib.util
import pathlib

GH_PATH = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts' / 'source_greenhouse_adapter.py'
GH_SPEC = importlib.util.spec_from_file_location("source_greenhouse_adapter", str(GH_PATH))
GH_MODULE = importlib.util.module_from_spec(GH_SPEC)
assert GH_SPEC and GH_SPEC.loader
GH_SPEC.loader.exec_module(GH_MODULE)  # type: ignore

fetch_greenhouse_jobs = GH_MODULE.fetch_greenhouse_jobs


def test_disabled_returns_empty():
    cfg = {"GREENHOUSE_ENABLED": False}
    assert fetch_greenhouse_jobs(cfg) == []


def test_mapping_and_dedup_determinism():
    cfg = {"GREENHOUSE_ENABLED": True, "GREENHOUSE_API_URL": "https://api.greenhouse.io/v1/boards/<company>/jobs"}
    raw = [
        {"title": "Software Engineer", "company": "Acme", "location": {"name": "Remote"}, "absolute_url": "https://boards.greenhouse.io/acme/jobs/1"},
        {"title": "Software Engineer", "absolute_url": "https://boards.greenhouse.io/acme/jobs/1"},  # duplicate
        {"title": "Data Engineer", "absolute_url": "https://boards.greenhouse.io/acme/jobs/2", "created_at": "2026-01-09"},
        {"title": "", "absolute_url": "https://boards.greenhouse.io/acme/jobs/3"},
    ]

    GH_MODULE.raw_jobs = raw  # type: ignore
    out1 = fetch_greenhouse_jobs(cfg)
    out2 = fetch_greenhouse_jobs(cfg)

    assert out1 == out2  # deterministic repeat runs

    assert all(set(x.keys()) >= {"job_id", "title", "company", "location", "url", "source", "posted_at"} for x in out1)
    job_ids = [x["job_id"] for x in out1]
    assert len(job_ids) == len(set(job_ids))


def test_missing_fields_are_skipped():
    cfg = {"GREENHOUSE_ENABLED": True}
    GH_MODULE.raw_jobs = [{"absolute_url": "https://boards.greenhouse.io/jobs/1"}, {"title": "Dev", "company": "", "absolute_url": ""}]  # type: ignore
    out = fetch_greenhouse_jobs(cfg)
    assert isinstance(out, list) and all("job_id" in x for x in out)


def test_multi_source_id_compatibility_with_lever():
    # Greenhouse job
    cfg_gh = {"GREENHOUSE_ENABLED": True}
    GH_MODULE.raw_jobs = [{"title": "Software Engineer", "company": "Acme", "location": {"name": "Remote"}, "absolute_url": "https://example.com/jobs/42"}]  # type: ignore
    gh_out = fetch_greenhouse_jobs(cfg_gh)
    assert gh_out and isinstance(gh_out[0]["job_id"], str)

    # Lever job with same canonical fields
    LEVER_PATH = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts' / 'source_lever_adapter.py'
    LEVER_SPEC = importlib.util.spec_from_file_location("source_lever_adapter", str(LEVER_PATH))
    LEVER_MODULE = importlib.util.module_from_spec(LEVER_SPEC)
    assert LEVER_SPEC and LEVER_SPEC.loader
    LEVER_SPEC.loader.exec_module(LEVER_MODULE)  # type: ignore

    LEVER_MODULE.raw_jobs = [{"text": "Software Engineer", "company": "Acme", "hostedUrl": "https://example.com/jobs/42"}]  # type: ignore
    lever_out = LEVER_MODULE.fetch_lever_jobs({"LEVER_ENABLED": True})

    # Canonical title|company|url should yield identical IDs across sources
    assert gh_out[0]["job_id"] == lever_out[0]["job_id"]
