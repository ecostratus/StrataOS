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
import time

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

from filters import normalize_terms, matches_filters, matches_tag_filters  # type: ignore
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

GREENHOUSE_TELEMETRY_DEFAULT_PATH = os.path.join(_ROOT, "logs", "greenhouse_week1_telemetry.jsonl")

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
    cfg_map: Dict[str, Any] = dict(config.to_dict()) if hasattr(config, "to_dict") else {}

    def _flag(key: str, default: bool = False) -> bool:
        if hasattr(config, "get_bool"):
            return bool(config.get_bool(key, bool(cfg_map.get(key, default))))
        return bool(cfg_map.get(key, default))

    modern_enable_keys = (
        "GREENHOUSE_ENABLED",
        "LEVER_ENABLED",
        "ASHBY_ENABLED",
        "ZIPRECRUITER_ENABLED",
        "GOOGLEJOBS_ENABLED",
        "GLASSDOOR_ENABLED",
        "CRAIGSLIST_ENABLED",
        "GOREMOTE_ENABLED",
    )

    for key in modern_enable_keys:
        cfg_map[key] = _flag(key, False)

    runtime_passthrough_keys = (
        "GREENHOUSE_API_URL",
        "GREENHOUSE_API_KEY",
        "LEVER_API_URL",
        "LEVER_API_KEY",
        "ASHBY_API_URL",
        "ASHBY_API_KEY",
        "INDEED_API_URL",
        "INDEED_API_KEY",
        "ZIPRECRUITER_API_URL",
        "ZIPRECRUITER_API_KEY",
        "GOOGLEJOBS_API_URL",
        "GOOGLEJOBS_API_KEY",
        "GLASSDOOR_API_URL",
        "GLASSDOOR_API_KEY",
        "CRAIGSLIST_API_URL",
        "GOREMOTE_API_URL",
    )
    if hasattr(config, "get"):
        for key in runtime_passthrough_keys:
            value = config.get(key, cfg_map.get(key))
            if value is not None:
                cfg_map[key] = value

    if hasattr(config, "get"):
        cfg_map["SOURCE_COMPLIANCE_POLICY_PATH"] = config.get(
            "SOURCE_COMPLIANCE_POLICY_PATH",
            cfg_map.get("SOURCE_COMPLIANCE_POLICY_PATH", "config/source_compliance_policy.json"),
        )

    use_modern_path = any(bool(cfg_map.get(k, False)) for k in modern_enable_keys)

    if use_modern_path and hasattr(sources, "fetch_all_sources"):
        try:
            canonical_jobs = sources.fetch_all_sources(cfg_map)
            jobs: List[Dict[str, str]] = []
            for item in canonical_jobs:
                posted_value = str(item.get("posted_at", "") or "")
                posted_date = posted_value[:10] if len(posted_value) >= 10 else datetime.now(UTC).strftime("%Y-%m-%d")
                jobs.append(
                    {
                        "title": str(item.get("title", "") or ""),
                        "location": str(item.get("location", "") or ""),
                        "company": str(item.get("company", "") or ""),
                        "source": str(item.get("source", "") or ""),
                        "url": str(item.get("url", "") or ""),
                        "posted_date": posted_date,
                    }
                )
            return jobs
        except Exception:
            logger.error("modern source aggregation failed", exc_info=True)
            return []

    jobs: List[Dict[str, str]] = []
    legacy_enabled_sources: List[str] = []
    if config.get_bool("LINKEDIN_ENABLED", False):
        legacy_enabled_sources.append("linkedin")
    if config.get_bool("INDEED_ENABLED", False):
        legacy_enabled_sources.append("indeed")

    if legacy_enabled_sources and hasattr(sources, "get_blocked_sources_by_policy"):
        blocked = sources.get_blocked_sources_by_policy(cfg_map, legacy_enabled_sources)
        if blocked:
            blocked_sorted = ", ".join(blocked)
            raise ValueError(f"Source compliance policy blocked enabled sources: {blocked_sorted}")

    if config.get_bool("LINKEDIN_ENABLED", False):
        jobs.extend(_safe_fetch("linkedin", sources.fetch_linkedin_jobs))
    if config.get_bool("INDEED_ENABLED", False):
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


def _append_greenhouse_telemetry(
    cfg_map: Dict[str, Any],
    *,
    success: bool,
    latency_ms: float | None,
    empty_run_count: int,
    payload_anomalies: int,
    error: str | None = None,
) -> None:
    path_value = cfg_map.get("GREENHOUSE_TELEMETRY_PATH", GREENHOUSE_TELEMETRY_DEFAULT_PATH)
    telemetry_path = str(path_value or GREENHOUSE_TELEMETRY_DEFAULT_PATH)
    os.makedirs(os.path.dirname(telemetry_path) or ".", exist_ok=True)
    entry = {
        "logged_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": "greenhouse",
        "success": bool(success),
        "latency_ms": latency_ms,
        "empty_run_count": int(empty_run_count),
        "payload_anomalies": int(payload_anomalies),
        "error": error,
    }
    with open(telemetry_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _greenhouse_payload_anomalies(rows: List[Dict[str, str]]) -> int:
    for row in rows:
        if not row.get("title") or not row.get("url") or not row.get("posted_date"):
            return 1
    return 0


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Job discovery orchestrator")
    parser.add_argument("--out-dir", dest="out_dir", default=None, help="Override output directory")
    parser.add_argument("--summary-only", dest="summary_only", action="store_true", help="Run discovery without CSV export")
    parser.add_argument("--enrich", dest="enrich", action="store_true", help="Run enrichment + scoring and export artifacts")
    parser.add_argument("--schedule", dest="schedule", action="store_true", help="Enable scheduling gate (Phase 3B)")
    args = parser.parse_args(argv)

    # Uvicorn and parent shells can retain stale env values across hot reloads.
    # Reset discovery-related keys so this run uses the latest .env/json settings.
    for key in (
        "JOB_FILTER_KEYWORDS",
        "JOB_FILTER_LOCATIONS",
        "JOB_FILTER_EXCLUDE_KEYWORDS",
        "JOB_FILTER_MAX_AGE_DAYS",
        "JOB_FILTER_INCLUDE_ROLE_TAGS",
        "JOB_FILTER_EXCLUDE_ROLE_TAGS",
        "JOB_FILTER_INCLUDE_STACK_TAGS",
        "JOB_FILTER_EXCLUDE_STACK_TAGS",
    ):
        os.environ.pop(key, None)

    json_cfg = os.path.join(_ROOT, "config", "env.json")
    if not os.path.exists(json_cfg):
        json_cfg = os.path.join(_ROOT, "config", "env.sample.json")
    config.initialize(json_path=json_cfg)

    environment = config.get("SYSTEM_ENVIRONMENT", "development")
    log_level = config.get("SYSTEM_LOG_LEVEL", "INFO")
    out_dir = str(args.out_dir or config.get("SYSTEM_OUTPUT_DIRECTORY", "output"))

    # Filters from config
    keywords = normalize_terms(config.get_list("JOB_FILTER_KEYWORDS", ["software engineer", "developer"]) or [])
    locations = normalize_terms(config.get_list("JOB_FILTER_LOCATIONS", ["Remote"]) or [])
    exclude = normalize_terms(config.get_list("JOB_FILTER_EXCLUDE_KEYWORDS", ["volunteer"]) or [])
    include_role_tags = normalize_terms(config.get_list("JOB_FILTER_INCLUDE_ROLE_TAGS", []) or [])
    exclude_role_tags = normalize_terms(config.get_list("JOB_FILTER_EXCLUDE_ROLE_TAGS", []) or [])
    include_stack_tags = normalize_terms(config.get_list("JOB_FILTER_INCLUDE_STACK_TAGS", []) or [])
    exclude_stack_tags = normalize_terms(config.get_list("JOB_FILTER_EXCLUDE_STACK_TAGS", []) or [])
    has_tag_filters = any(
        [include_role_tags, exclude_role_tags, include_stack_tags, exclude_stack_tags]
    )

    print("Job discovery v1  starting")
    print(
        f"Env: {environment} | Log: {log_level} | "
        f"Keywords: {', '.join(keywords) or '-'} | Locations: {', '.join(locations) or '-'} | Exclude: {', '.join(exclude) or '-'}"
    )
    if has_tag_filters:
        print(
            "Tag filters enabled | "
            f"Include role: {', '.join(include_role_tags) or '-'} | "
            f"Exclude role: {', '.join(exclude_role_tags) or '-'} | "
            f"Include stack: {', '.join(include_stack_tags) or '-'} | "
            f"Exclude stack: {', '.join(exclude_stack_tags) or '-'}"
        )
        if not enrichment:
            logger.warning("Tag filters requested but enrichment module unavailable; skipping tag filter checks")

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
            cfg_map = config.to_dict()
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
    telemetry_enabled = bool(config.get_bool("GREENHOUSE_ENABLED", False))
    discovery_started = time.perf_counter()
    jobs: List[Dict[str, str]] = []
    matched: List[Dict[str, str]] = []
    discovery_error: str | None = None
    summary: Dict[str, Any] | None = None
    out_json: str | None = None
    out_csv = None
    enriched_json_path = None
    out_scored_csv = None
    try:
        jobs = discover_jobs()

        tag_filtered_out = 0
        for job in jobs:
            if matches_filters(job.get("title", ""), job.get("location", ""), keywords, locations, exclude):
                if has_tag_filters and enrichment:
                    feature_view = enrichment.extract_features(job, config.to_dict())
                    if not matches_tag_filters(
                        feature_view.get("role_tags", []),
                        feature_view.get("stack_tags", []),
                        include_role_tags,
                        exclude_role_tags,
                        include_stack_tags,
                        exclude_stack_tags,
                    ):
                        tag_filtered_out += 1
                        continue
                matched.append(job)

        print(f"Found {len(jobs)} jobs; {len(matched)} matched filters")
        # Single timestamp for CSV + summary for determinism
        ts = run_ts
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
                    cfg_scoring = config.to_dict().get("scoring", {})
                    if isinstance(cfg_scoring, dict):
                        weights = cfg_scoring.get("weights", {}) or weights
                        thresholds = cfg_scoring.get("thresholds", {}) or thresholds
                except Exception:
                    pass

                enriched_rows: List[Dict[str, Any]] = [enrichment.extract_features(j, config.to_dict()) for j in matched]
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
        "indeed": bool(config.get_bool("INDEED_ENABLED", False)),
        "greenhouse": bool(config.get_bool("GREENHOUSE_ENABLED", False)),
        "lever": bool(config.get_bool("LEVER_ENABLED", False)),
        "ashby": bool(config.get_bool("ASHBY_ENABLED", False)),
        "ziprecruiter": bool(config.get_bool("ZIPRECRUITER_ENABLED", False)),
        "google_jobs": bool(config.get_bool("GOOGLEJOBS_ENABLED", False)),
        "glassdoor": bool(config.get_bool("GLASSDOOR_ENABLED", False)),
        "craigslist": bool(config.get_bool("CRAIGSLIST_ENABLED", False)),
        "goremote": bool(config.get_bool("GOREMOTE_ENABLED", False)),
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

        if not per_source.get("jobs_fetched"):
            counts: Dict[str, int] = {}
            for job in jobs:
                src = str(job.get("source", "")).strip().lower() or "unknown"
                counts[src] = counts.get(src, 0) + 1
            per_source = {
                "jobs_fetched": counts,
                "malformed_entries": {},
                "retries_attempted": 0,
                "rate_limit_sleeps": 0,
                "scraper_failures": 0,
            }

        filtered_out = max(0, len(jobs) - len(matched))
        summary = {
            "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "enabled_sources": enabled_sources,
            "tag_filters": {
                "include_role_tags": include_role_tags,
                "exclude_role_tags": exclude_role_tags,
                "include_stack_tags": include_stack_tags,
                "exclude_stack_tags": exclude_stack_tags,
            },
            "counts": {
                "total_discovered": len(jobs),
                "filtered_out": filtered_out,
                "tag_filtered_out": tag_filtered_out,
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
    except Exception as exc:
        discovery_error = discovery_error or str(exc)
        raise
    finally:
        if telemetry_enabled:
            greenhouse_rows = [job for job in jobs if str(job.get("source", "")).strip().lower() == "greenhouse"]
            empty_run_count = 0
            if discovery_error is None and bool(config.get_bool("GREENHOUSE_ENABLED", False)) and not greenhouse_rows:
                empty_run_count = 1
            _append_greenhouse_telemetry(
                dict(config.to_dict()) if hasattr(config, "to_dict") else {},
                success=discovery_error is None,
                latency_ms=round((time.perf_counter() - discovery_started) * 1000, 2),
                empty_run_count=empty_run_count,
                payload_anomalies=_greenhouse_payload_anomalies(greenhouse_rows),
                error=discovery_error,
            )

    # Optional retention prune (Phase 3B)
    try:
        retention_cfg = {}
        try:
            retention_cfg = (config.to_dict().get("retention", {}) or {})
        except Exception:
            retention_cfg = {}
        enabled = bool(retention_cfg.get("enabled", False))
        if enabled:
            storage_cfg = (config.to_dict().get("storage", {}) or {})
            backend = str(storage_cfg.get("backend", "sqlite")).lower()
            if backend == "json":
                from automation.storage import json_store  # type: ignore

                _ = json_store.prune(config.to_dict())
            else:
                from automation.storage import sqlite_store  # type: ignore

                _ = sqlite_store.prune(config.to_dict())
    except Exception:
        logger.info("Retention prune skipped due to missing backend or config")


if __name__ == "__main__":
    main()
