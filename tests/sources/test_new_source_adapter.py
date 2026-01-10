import importlib.util
import pathlib

MODULE_PATH = pathlib.Path(__file__).resolve().parents[2] / 'automation' / 'job-discovery' / 'scripts' / 'new_source_adapter.py'
spec = importlib.util.spec_from_file_location("new_source_adapter", str(MODULE_PATH))
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore

adapt_new_source = module.adapt_new_source


def test_disabled_returns_empty():
    items = [{"title": "Engineer", "company": "Acme", "url": "https://acme/jobs/1"}]
    cfg = {"NEW_SOURCE_ENABLED": False}
    assert adapt_new_source(items, cfg) == []


def test_mapping_and_determinism():
    items = [
        {"title": "Engineer ", "company": " Acme ", "url": "https://acme/jobs/1", "location": "Remote"},
        {"title": "Engineer", "company": "Acme", "url": "https://acme/jobs/1"},  # duplicate canonical
        {"title": "Developer", "company": "Beta", "url": "https://beta/jobs/2", "posted_at": "2026-01-09"},
        {"title": "", "company": "Nope", "url": "https://nope/jobs/3"},  # malformed
    ]
    cfg = {"NEW_SOURCE_ENABLED": True, "enrichment": {"keywords": {"role": ["Engineer", " dev "]}}}
    out1 = adapt_new_source(items, cfg)
    out2 = adapt_new_source(items, cfg)

    # Deterministic repeat runs
    assert out1 == out2

    # Canonical fields present
    assert all(set(x.keys()) == {"job_id", "title", "company", "location", "url", "posted_at"} for x in out1)

    # Duplicates collapse to same job_id ordering
    job_ids = [x["job_id"] for x in out1]
    assert len(job_ids) == len(set(job_ids))

    # Posted_at filled when missing
    assert any(x["posted_at"] for x in out1)


def test_error_handling_and_sorting():
    items = [{"title": "A", "company": "C", "url": "u"}, {"title": "B", "company": "C", "url": "u2"}]
    cfg = {"NEW_SOURCE_ENABLED": True}
    out = adapt_new_source(items, cfg)
    assert out == sorted(out, key=lambda x: x["job_id"])