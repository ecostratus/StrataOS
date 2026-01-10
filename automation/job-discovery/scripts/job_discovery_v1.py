"""
Job Discovery Orchestrator v1

Loads configuration, calls per-source fetchers, applies filtering, and exports
discovered jobs. Designed to be extended to real scrapers per scraper-spec.
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime
try:  # Python 3.11+
    from datetime import UTC  # type: ignore
except Exception:  # Python <3.11
    from datetime import timezone as _tz  # type: ignore
    UTC = _tz.utc  # type: ignore
from typing import Dict, List, Callable, Any, Optional
import argparse
import logging
import json

# Ensure repo root on path to import config and filters
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config  # type: ignore

# Add scripts dir to path to import modules despite hyphen in folder name
_SCRIPTS_DIR = os.path.join(_ROOT, "automation", "job-discovery", "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

# Add enrichment scripts dir for Phase 3A pipeline
_ENRICHMENT_SCRIPTS_DIR = os.path.join(_ROOT, "automation", "enrichment", "scripts")
if _ENRICHMENT_SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _ENRICHMENT_SCRIPTS_DIR)

# Add scheduling dir for Phase 3B scheduling helpers
_SCHEDULING_DIR = os.path.join(_ROOT, "automation", "scheduling")
if _SCHEDULING_DIR not in sys.path:
    sys.path.insert(0, _SCHEDULING_DIR)

from filters import normalize_terms, matches_filters  # type: ignore
import sources  # type: ignore
from logging_utils import set_jsonl_sink, set_suppress_stdout_if_jsonl  # type: ignore
from summary_utils import pretty_print_summary  # type: ignore
try:
    import enrichment  # type: ignore
    import scoring  # type: ignore
except Exception:
    enrichment = None  # type: ignore
    scoring = None  # type: ignore
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

REQUIRED_KEYS = {"title", "location", "company", "source", "url", "posted_date"}


def _validate_job(job: Dict[str, Any]) -> bool:
    if not isinstance(job, dict):
        return False
    if not REQUIRED_KEYS.issubset(job.keys()):
        return False
    # ensure string-like values
    for k in REQUIRED_KEYS:
        v = job.get(k)
        if v is None:
            return False
        # Allow non-string values but coerce later; for now require str-like
        if not isinstance(v, (str, int, float)):
            return False
    return True


def _safe_fetch(name: str, func: Callable[[], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    try:
        res = func()
        if not isinstance(res, list):
            logger.error("source '%s' returned non-list result", name)
            return []
        valid = [j for j in res if _validate_job(j)]
        invalid = len(res) - len(valid)
        if invalid:
            logger.warning("source '%s' returned %d invalid jobs", name, invalid)
        return valid
    except Exception:
        logger.error("source '%s' failed", name, exc_info=True)
        return []


def discover_jobs() -> List[Dict[str, str]]:
    """Collect jobs from enabled sources. Each job has keys:
    title, location, company, source, url, posted_date (YYYY-MM-DD).
    """
    jobs: List[Dict[str, str]] = []
    if config.get_bool("LINKEDIN_ENABLED", False):
        jobs.extend(_safe_fetch("linkedin", sources.fetch_linkedin_jobs))
    if config.get_bool("INDEED_ENABLED", True):
        jobs.extend(_safe_fetch("indeed", sources.fetch_indeed_jobs))
    if not jobs:
        # Fallback minimal placeholder (kept for bootstrapping)
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        jobs = [
            {
                "title": "Senior Software Engineer - Remote",
                "location": "Remote",
                "company": "Acme Corp",
                "source": "sample",
                "url": "https://example.com/jobs/1",
                "posted_date": today,
            }
        ]
    return jobs


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def export_to_csv(rows: List[Dict[str, str]], out_dir: str) -> str:
    ensure_dir(out_dir)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"jobs_discovered_{ts}.csv")
    fieldnames = [
        "title",
        "location",
        "company",
        "source",
        "url",
        "posted_date",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    return path


def export_to_csv_with_ts(rows: List[Dict[str, str]], out_dir: str, ts: str) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"jobs_discovered_{ts}.csv")
    fieldnames = [
        "title",
        "location",
        "company",
        "source",
        "url",
        "posted_date",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    return path


def export_summary(out_dir: str, ts: str, summary: Dict[str, Any]) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"jobs_discovered_{ts}.summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, separators=(",", ":"))
    return path


def export_enriched_json_with_ts(rows: List[Dict[str, Any]], out_dir: str, ts: str) -> str:
    """Export enriched job records as compact JSON array with deterministic filename."""
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"jobs_enriched_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
    return path


def export_scored_csv_with_ts(rows: List[Dict[str, Any]], out_dir: str, ts: str) -> str:
    """Export scored job records to CSV including original fields and scoring columns."""
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"jobs_scored_{ts}.csv")
    fieldnames = [
        "title",
        "location",
        "company",
        "source",
        "url",
        "posted_date",
        "score",
        "bucket",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    return path


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Job discovery orchestrator")
    parser.add_argument("--out-dir", dest="out_dir", default=None, help="Override output directory")
    parser.add_argument("--summary-only", dest="summary_only", action="store_true", help="Run discovery without CSV export")
    parser.add_argument("--enrich", dest="enrich", action="store_true", help="Run enrichment + scoring and export artifacts")
    parser.add_argument("--schedule", dest="schedule", action="store_true", help="Enable scheduling gate (Phase 3B)")
    args = parser.parse_args(argv)

    config.initialize()

    environment = config.get("SYSTEM_ENVIRONMENT", "development")
    log_level = config.get("SYSTEM_LOG_LEVEL", "INFO")
    out_dir = str(args.out_dir or config.get("SYSTEM_OUTPUT_DIRECTORY", "output"))

    # Filters from config
    keywords = normalize_terms(config.get_list("JOB_FILTER_KEYWORDS", ["software engineer", "developer"]) or [])
    locations = normalize_terms(config.get_list("JOB_FILTER_LOCATIONS", ["Remote"]) or [])
    exclude = normalize_terms(config.get_list("JOB_FILTER_EXCLUDE_KEYWORDS", ["volunteer"]) or [])

    print("Job discovery v1 — starting")
    print(
        f"Env: {environment} | Log: {log_level} | "
        f"Keywords: {', '.join(keywords) or '-'} | Locations: {', '.join(locations) or '-'} | Exclude: {', '.join(exclude) or '-'}"
    )

    # Reset per-run source metrics
    if hasattr(sources, "reset_metrics"):
        sources.reset_metrics()

    # Prepare optional JSONL logging sink
    # Single timestamp used across artifacts for determinism in tests
    run_ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    if config.get_bool("LOG_TO_FILE", False):
        set_jsonl_sink(os.path.join(out_dir, f"run-{run_ts}.jsonl"))
        # Optional suppression of stdout logs when JSONL is enabled
        suppress = config.get_bool("LOG_SUPPRESS_STDOUT_IF_JSONL", False)
        set_suppress_stdout_if_jsonl(bool(suppress))

    # Optional scheduling gate (Phase 3B)
    if getattr(args, "schedule", False):
        try:
            import scheduler  # type: ignore

            now_utc = datetime.now(UTC)
            last_run_ts = None  # TODO: load from storage backend when available
            cfg_map = config.to_dict() if hasattr(config, "to_dict") else {}
            try:
                should = scheduler.should_run(now_utc, last_run_ts, cfg_map)  # type: ignore[attr-defined]
            except NotImplementedError:
                should = True  # defer gating until implemented
            if not should:
                print("--schedule enabled: not time to run; exiting early")
                return
        except Exception:
            # Scheduling unavailable; proceed without gating
            logger.info("Scheduling helpers unavailable; proceeding without schedule gating")

    # Fetch and filter
    jobs = discover_jobs()
    matched: List[Dict[str, str]] = []
    for job in jobs:
        if matches_filters(job.get("title", ""), job.get("location", ""), keywords, locations, exclude):
            matched.append(job)

    print(f"Found {len(jobs)} jobs; {len(matched)} matched filters")
    # Single timestamp for CSV + summary for determinism
    ts = run_ts
    out_csv = None
    enriched_json_path = None
    out_scored_csv = None
    if not args.summary_only:
        out_csv = export_to_csv_with_ts(matched, out_dir, ts)

    # Optional enrichment + scoring pipeline (Phase 3A)
    if args.enrich and not args.summary_only:
        if enrichment and scoring:
            # Build config slices for enrichment/scoring (defaults if missing)
            # Enrichment uses config within extract_features; scoring uses weights/thresholds
            weights = {}
            thresholds = {
                "exceptional": 0.8,
                "strong": 0.6,
                "moderate": 0.4,
            }
            # Attempt to read weights/thresholds from config if available
            try:
                cfg_scoring = config.get("SCORING", {})
                if isinstance(cfg_scoring, dict):
                    weights = cfg_scoring.get("weights", {}) or weights
                    thresholds = cfg_scoring.get("thresholds", {}) or thresholds
            except Exception:
                pass

            enriched_rows: List[Dict[str, Any]] = [enrichment.extract_features(j, config.to_dict() if hasattr(config, "to_dict") else {}) for j in matched]
            enriched_json_path = export_enriched_json_with_ts(enriched_rows, out_dir, ts)

            scored_rows: List[Dict[str, Any]] = []
            for e in enriched_rows:
                s = scoring.score_job(e, weights, thresholds)
                combined = dict(e)
                combined.update({"score": s.get("score", 0.0), "bucket": s.get("bucket", "Weak")})
                scored_rows.append(combined)
            out_scored_csv = export_scored_csv_with_ts(scored_rows, out_dir, ts)
        else:
            logger.warning("Enrichment/scoring modules not available; skipping --enrich pipeline.")

    # Build summary artifact
    enabled_sources = {
        "linkedin": bool(config.get_bool("LINKEDIN_ENABLED", False)),
        "indeed": bool(config.get_bool("INDEED_ENABLED", True)),
    }
    per_source = {}
    if hasattr(sources, "get_metrics"):
        m = sources.get_metrics().to_dict()
        per_source = {
            "jobs_fetched": m.get("jobs_fetched", {}),
            "malformed_entries": m.get("malformed_entries", {}),
            "retries_attempted": m.get("retries_attempted", 0),
            "rate_limit_sleeps": m.get("rate_limit_sleeps", 0),
            "scraper_failures": m.get("scraper_failures", 0),
        }

    filtered_out = max(0, len(jobs) - len(matched))
    summary = {
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "enabled_sources": enabled_sources,
        "counts": {
            "total_discovered": len(jobs),
            "filtered_out": filtered_out,
            "exported": len(matched),
        },
        "per_source": per_source,
    }
    out_json = export_summary(out_dir, ts, summary)
    # Optionally pretty-print a short summary after export
    print(pretty_print_summary(summary))
    if not args.summary_only and out_csv:
        print(f"Exported matched jobs to: {out_csv}")
    if enriched_json_path:
        print(f"Exported enriched jobs to: {enriched_json_path}")
    if out_scored_csv:
        print(f"Exported scored jobs to: {out_scored_csv}")
    print(f"Summary: {out_json}")

    # Optional retention prune (Phase 3B)
    try:
        retention_cfg = {}
        try:
            retention_cfg = (config.get("RETENTION", {}) or {})
        except Exception:
            retention_cfg = {}
        enabled = bool(retention_cfg.get("enabled", False))
        if enabled:
            storage_cfg = (config.get("STORAGE", {}) or {})
            backend = str(storage_cfg.get("backend", "sqlite")).lower()
            if backend == "json":
                from automation.storage import json_store  # type: ignore

                _ = json_store.prune(config.to_dict() if hasattr(config, "to_dict") else {})
            else:
                from automation.storage import sqlite_store  # type: ignore

                _ = sqlite_store.prune(config.to_dict() if hasattr(config, "to_dict") else {})
    except Exception:
        logger.info("Retention prune skipped due to missing backend or config")


if __name__ == "__main__":
    main()
