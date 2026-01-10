import importlib.util
import pathlib

MODULE_PATH = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts' / 'source_lever_adapter.py'
spec = importlib.util.spec_from_file_location("source_lever_adapter", str(MODULE_PATH))
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore

fetch_lever_jobs = module.fetch_lever_jobs


def test_disabled_returns_empty():
    cfg = {"LEVER_ENABLED": False}
    assert fetch_lever_jobs(cfg) == []


def test_mapping_and_dedup_determinism():
    cfg = {"LEVER_ENABLED": True, "LEVER_API_URL": "https://api.lever.co/postings/company"}
    raw = [
        {"text": "Software Engineer", "company": "Acme", "categories": {"location": "Remote"}, "hostedUrl": "https://lever.co/acme/jobs/1"},
        {"title": "Software Engineer", "hostedUrl": "https://lever.co/acme/jobs/1"},  # duplicate
        {"text": "Data Engineer", "hostedUrl": "https://lever.co/acme/jobs/2", "createdAt": "2026-01-09"},
        {"text": "", "hostedUrl": "https://lever.co/acme/jobs/3"},
    ]

    # Inject raw jobs into adapter by monkeypatching module symbol
    module.raw_jobs = raw  # type: ignore
    out1 = fetch_lever_jobs(cfg)
    out2 = fetch_lever_jobs(cfg)

    # Deterministic repeat runs
    assert out1 == out2

    # Fields set and dedup applied
    assert all(set(x.keys()) >= {"job_id", "title", "company", "location", "url", "source", "posted_at"} for x in out1)
    job_ids = [x["job_id"] for x in out1]
    assert len(job_ids) == len(set(job_ids))


def test_missing_fields_are_skipped():
    cfg = {"LEVER_ENABLED": True}
    module.raw_jobs = [{"hostedUrl": "https://lever/jobs/1"}, {"text": "Dev", "company": "", "hostedUrl": ""}]  # type: ignore
    out = fetch_lever_jobs(cfg)
    assert isinstance(out, list) and all("job_id" in x for x in out)
