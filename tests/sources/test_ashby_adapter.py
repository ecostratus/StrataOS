import importlib.util
import pathlib

ASHBY_PATH = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts' / 'source_ashby_adapter.py'
ASHBY_SPEC = importlib.util.spec_from_file_location("source_ashby_adapter", str(ASHBY_PATH))
ASHBY_MODULE = importlib.util.module_from_spec(ASHBY_SPEC)
assert ASHBY_SPEC and ASHBY_SPEC.loader
ASHBY_SPEC.loader.exec_module(ASHBY_MODULE)  # type: ignore

fetch_ashby_jobs = ASHBY_MODULE.fetch_ashby_jobs


def test_disabled_returns_empty():
    cfg = {"ASHBY_ENABLED": False}
    assert fetch_ashby_jobs(cfg) == []


def test_mapping_and_dedup_determinism():
    cfg = {"ASHBY_ENABLED": True, "ASHBY_API_URL": "https://api.ashbyhq.com/jobs", "ASHBY_API_KEY": "test"}
    raw = [
        {"title": "Software Engineer", "companyName": "Acme", "location": "Remote", "jobUrl": "https://ashbyhq.com/acme/jobs/1"},
        {"title": "Software Engineer", "jobUrl": "https://ashbyhq.com/acme/jobs/1"},  # duplicate
        {"title": "Data Engineer", "jobUrl": "https://ashbyhq.com/acme/jobs/2", "publishedAt": "2026-01-09"},
        {"title": "", "jobUrl": "https://ashbyhq.com/acme/jobs/3"},
    ]

    ASHBY_MODULE.raw_jobs = raw  # type: ignore
    out1 = fetch_ashby_jobs(cfg)
    out2 = fetch_ashby_jobs(cfg)

    assert out1 == out2  # deterministic repeat runs

    assert all(set(x.keys()) >= {"job_id", "title", "company", "location", "url", "source", "posted_at"} for x in out1)
    job_ids = [x["job_id"] for x in out1]
    assert len(job_ids) == len(set(job_ids))


def test_missing_fields_are_skipped():
    cfg = {"ASHBY_ENABLED": True, "ASHBY_API_URL": "x", "ASHBY_API_KEY": "y"}
    ASHBY_MODULE.raw_jobs = [{"jobUrl": "https://ashbyhq.com/jobs/1"}, {"title": "Dev", "companyName": "", "jobUrl": ""}]  # type: ignore
    out = fetch_ashby_jobs(cfg)
    assert isinstance(out, list) and all("job_id" in x for x in out)


def test_multi_source_id_compatibility_with_lever():
    # Ashby job
    cfg_ash = {"ASHBY_ENABLED": True, "ASHBY_API_URL": "x", "ASHBY_API_KEY": "y"}
    ASHBY_MODULE.raw_jobs = [{"title": "Software Engineer", "companyName": "Acme", "jobUrl": "https://example.com/jobs/42"}]  # type: ignore
    ash_out = fetch_ashby_jobs(cfg_ash)
    assert ash_out and isinstance(ash_out[0]["job_id"], str)

    # Lever job with same canonical fields
    LEVER_PATH = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts' / 'source_lever_adapter.py'
    LEVER_SPEC = importlib.util.spec_from_file_location("source_lever_adapter", str(LEVER_PATH))
    LEVER_MODULE = importlib.util.module_from_spec(LEVER_SPEC)
    assert LEVER_SPEC and LEVER_SPEC.loader
    LEVER_SPEC.loader.exec_module(LEVER_MODULE)  # type: ignore

    LEVER_MODULE.raw_jobs = [{"text": "Software Engineer", "company": "Acme", "hostedUrl": "https://example.com/jobs/42"}]  # type: ignore
    lever_out = LEVER_MODULE.fetch_lever_jobs({"LEVER_ENABLED": True})

    # Canonical title|company|url should yield identical IDs across sources
    assert ash_out[0]["job_id"] == lever_out[0]["job_id"]
