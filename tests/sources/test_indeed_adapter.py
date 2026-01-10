import importlib.util
import pathlib

INDEED_PATH = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts' / 'source_indeed_adapter.py'
INDEED_SPEC = importlib.util.spec_from_file_location("source_indeed_adapter", str(INDEED_PATH))
INDEED_MODULE = importlib.util.module_from_spec(INDEED_SPEC)
assert INDEED_SPEC and INDEED_SPEC.loader
INDEED_SPEC.loader.exec_module(INDEED_MODULE)  # type: ignore

fetch_indeed_jobs = INDEED_MODULE.fetch_indeed_jobs


def test_disabled_returns_empty():
    cfg = {"INDEED_ENABLED": False}
    assert fetch_indeed_jobs(cfg) == []


def test_mapping_and_dedup_determinism():
    cfg = {"INDEED_ENABLED": True, "INDEED_API_URL": "https://api.indeed.com/jobs", "INDEED_API_KEY": "test"}
    raw = [
        {"title": "Software Engineer", "company": "Acme", "location": "Remote", "url": "https://indeed.com/acme/jobs/1"},
        {"title": "Software Engineer", "url": "https://indeed.com/acme/jobs/1"},  # duplicate
        {"title": "Data Engineer", "url": "https://indeed.com/acme/jobs/2", "datePublished": "2026-01-09"},
        {"title": "", "url": "https://indeed.com/acme/jobs/3"},
    ]

    INDEED_MODULE.raw_jobs = raw  # type: ignore
    out1 = fetch_indeed_jobs(cfg)
    out2 = fetch_indeed_jobs(cfg)

    assert out1 == out2  # deterministic repeat runs

    assert all(set(x.keys()) >= {"job_id", "title", "company", "location", "url", "source", "posted_at"} for x in out1)
    job_ids = [x["job_id"] for x in out1]
    assert len(job_ids) == len(set(job_ids))


def test_missing_fields_are_skipped():
    cfg = {"INDEED_ENABLED": True, "INDEED_API_URL": "x", "INDEED_API_KEY": "y"}
    INDEED_MODULE.raw_jobs = [{"url": "https://indeed.com/jobs/1"}, {"title": "Dev", "company": "", "url": ""}]  # type: ignore
    out = fetch_indeed_jobs(cfg)
    assert isinstance(out, list) and all("job_id" in x for x in out)


def test_multi_source_id_compatibility_with_lever():
    # Indeed job
    cfg_ind = {"INDEED_ENABLED": True, "INDEED_API_URL": "x", "INDEED_API_KEY": "y"}
    INDEED_MODULE.raw_jobs = [{"title": "Software Engineer", "company": "Acme", "url": "https://example.com/jobs/42"}]  # type: ignore
    ind_out = fetch_indeed_jobs(cfg_ind)
    assert ind_out and isinstance(ind_out[0]["job_id"], str)

    # Lever job with same canonical fields
    LEVER_PATH = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts' / 'source_lever_adapter.py'
    LEVER_SPEC = importlib.util.spec_from_file_location("source_lever_adapter", str(LEVER_PATH))
    LEVER_MODULE = importlib.util.module_from_spec(LEVER_SPEC)
    assert LEVER_SPEC and LEVER_SPEC.loader
    LEVER_SPEC.loader.exec_module(LEVER_MODULE)  # type: ignore

    LEVER_MODULE.raw_jobs = [{"text": "Software Engineer", "company": "Acme", "hostedUrl": "https://example.com/jobs/42"}]  # type: ignore
    lever_out = LEVER_MODULE.fetch_lever_jobs({"LEVER_ENABLED": True})

    # Canonical title|company|url should yield identical IDs across sources
    assert ind_out[0]["job_id"] == lever_out[0]["job_id"]
