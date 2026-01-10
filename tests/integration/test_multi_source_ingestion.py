import importlib.util
import pathlib

# Dynamic imports due to hyphen in folder name
BASE = pathlib.Path(__file__).resolve().parents[2]

# New source adapter
nsa_path = BASE / 'automation' / 'job-discovery' / 'scripts' / 'new_source_adapter.py'
spec_nsa = importlib.util.spec_from_file_location("new_source_adapter", str(nsa_path))
mod_nsa = importlib.util.module_from_spec(spec_nsa)
assert spec_nsa and spec_nsa.loader
spec_nsa.loader.exec_module(mod_nsa)  # type: ignore

# Lever adapter
lev_path = BASE / 'automation' / 'job-discovery' / 'scripts' / 'source_lever_adapter.py'
spec_lev = importlib.util.spec_from_file_location("source_lever_adapter", str(lev_path))
mod_lev = importlib.util.module_from_spec(spec_lev)
assert spec_lev and spec_lev.loader
spec_lev.loader.exec_module(mod_lev)  # type: ignore


def test_multi_source_determinism_and_dedup():
    cfg = {"NEW_SOURCE_ENABLED": True, "LEVER_ENABLED": True}
    items_new = [
        {"title": "Engineer", "company": "Acme", "url": "https://acme/jobs/1"},
        {"title": "Engineer", "company": "Acme", "url": "https://acme/jobs/1"},
    ]
    mod_nsa_items = items_new
    out_new = mod_nsa.adapt_new_source(mod_nsa_items, cfg)

    mod_lev.raw_jobs = [  # type: ignore
        {"text": "Engineer", "company": "Acme", "hostedUrl": "https://acme/jobs/1"},
        {"text": "Engineer", "company": "Acme", "hostedUrl": "https://acme/jobs/1"},
    ]
    out_lev = mod_lev.fetch_lever_jobs(cfg)

    combined = out_new + out_lev
    # Deterministic combined ordering by job_id when sorted
    combined_sorted = sorted(combined, key=lambda x: x["job_id"])
    assert combined_sorted == sorted(combined_sorted, key=lambda x: x["job_id"])  # idempotent sort

    # De-dup across sources by job_id
    job_ids = [x["job_id"] for x in combined_sorted]
    assert len(job_ids) == len(set(job_ids))
