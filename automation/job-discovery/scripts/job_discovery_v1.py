"""
Job Discovery Orchestrator v1

Loads configuration, calls per-source fetchers, applies filtering, and exports
discovered jobs. Designed to be extended to real scrapers per scraper-spec.
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
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
SKIP_LIVE_FETCH_FIXTURES = (
    Path(_ROOT) / "tests" / "fixtures" / "job_discovery" / "track_ac_boundary_fixture.json",
    Path(_ROOT) / "tests" / "fixtures" / "job_discovery" / "track_b_precedence_fixture.json",
    Path(_ROOT) / "tests" / "fixtures" / "job_discovery" / "real_world_track_mix_fixture.json",
)

REQUIRED_KEYS = {"title", "location", "company", "source", "url", "posted_date"}

_PROFILE_TRACK_TITLE_FAMILY_TERMS = {
    "track_a_risk_governance": (
        "governance",
        "risk",
        "compliance",
        "audit",
        "trust",
        "privacy",
        "grc",
        "policy",
        "responsible ai",
        "ai governance",
    ),
    "track_b_platform_stabilization": (
        "technical program manager",
        "technical program management",
        "program manager",
        "program management",
        "tpm",
        "technical solutions operations",
        "platform operations",
        "reliability",
        "site reliability",
        "sre",
        "infrastructure",
        "operations",
    ),
    "track_c_ai_product_cpo": (
        "product manager",
        "product management",
        "group product manager",
        "principal product manager",
        "senior product manager",
        "director product management",
        "chief product",
        "cpo",
    ),
}

_PROFILE_TRACK_PRECEDENCE = {
    "track_a_risk_governance": 3,
    "track_c_ai_product_cpo": 2,
    "track_b_platform_stabilization": 1,
}


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


def _build_profile_tracks(filters_cfg: Dict[str, Any]) -> tuple[List[Dict[str, Any]], List[str]]:
    title_terms = normalize_terms(filters_cfg.get("title_terms", []) or [])
    raw_profile_tracks = filters_cfg.get("profile_tracks", []) or []
    profile_tracks: List[Dict[str, Any]] = []
    if isinstance(raw_profile_tracks, list):
        for idx, item in enumerate(raw_profile_tracks):
            if not isinstance(item, dict):
                continue
            track_name = str(item.get("name", "") or "").strip() or f"track_{idx + 1}"
            track_label = str(item.get("label", "") or "").strip() or track_name
            track_signals = normalize_terms(item.get("signals", []) or [])
            track_title_terms = normalize_terms(item.get("title_terms", []) or [])
            track_title_qualifiers = normalize_terms(item.get("title_qualifiers", []) or [])
            track_title_required_terms = normalize_terms(item.get("title_required_terms", []) or [])
            try:
                track_min_hits = int(item.get("min_hits", 1) or 1)
            except Exception:
                track_min_hits = 1
            if track_signals or track_title_terms or track_title_qualifiers or track_title_required_terms:
                profile_tracks.append(
                    {
                        "name": track_name,
                        "label": track_label,
                        "signals": track_signals,
                        "title_terms": track_title_terms,
                        "title_qualifiers": track_title_qualifiers,
                        "title_required_terms": track_title_required_terms,
                        "min_hits": max(1, track_min_hits),
                    }
                )
                title_terms.extend(term for term in track_title_terms if term not in title_terms)
    return profile_tracks, title_terms


def _select_profile_track(
    title: str,
    combined_text: str,
    profile_tracks: List[Dict[str, Any]],
) -> tuple[Dict[str, Any] | None, int, str]:
    title_text = str(title or "").lower()
    combined = str(combined_text or "").lower()
    best_track: Dict[str, Any] | None = None
    best_score: tuple[int, int, int, int] = (-1, -1, -1, -1)
    for index, track in enumerate(profile_tracks):
        qualifiers = track.get("title_qualifiers", []) or []
        if qualifiers and not any(q in title_text for q in qualifiers):
            continue
        required_terms = track.get("title_required_terms", []) or []
        if required_terms and not any(term in title_text for term in required_terms):
            continue
        signal_hits = sum(1 for sig in track["signals"] if sig and sig in combined)
        track_name = str(track.get("name", "") or "")
        family_terms = _PROFILE_TRACK_TITLE_FAMILY_TERMS.get(track_name, ())
        family_hits = sum(1 for term in family_terms if term and term in title_text)
        family_rank = _PROFILE_TRACK_PRECEDENCE.get(track_name, 0) if family_hits else 0
        if family_hits == 0 and signal_hits < track["min_hits"]:
            continue
        candidate_score = (family_rank, family_hits, signal_hits, -index)
        if candidate_score > best_score:
            best_score = candidate_score
            best_track = track
    if best_track is None:
        return None, 0, ""
    return best_track, best_score[2], str(best_track.get("label", "") or "")


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

    skip_live_fetch = bool(config.get_bool("SKIP_LIVE_FETCH", False)) if hasattr(config, "get_bool") else False

    if use_modern_path and hasattr(sources, "fetch_all_sources"):
        try:
            if skip_live_fetch:
                canonical_jobs = _load_skip_live_fetch_jobs()
                print(f"Skip-live-fetch mode enabled | Loaded {len(canonical_jobs)} fixture jobs")
            else:
                canonical_jobs = sources.fetch_all_sources(cfg_map)
            jobs: List[Dict[str, str]] = []
            for item in canonical_jobs:
                posted_value = str(item.get("posted_at", "") or "")
                posted_date = posted_value[:10] if len(posted_value) >= 10 else datetime.now(UTC).strftime("%Y-%m-%d")
                search_text = " ".join(
                    part
                    for part in [
                        str(item.get("description", "") or ""),
                        str(item.get("content", "") or ""),
                        str(item.get("summary", "") or ""),
                        str(item.get("team", "") or ""),
                        str(item.get("department", "") or ""),
                    ]
                    if part
                )
                jobs.append(
                    {
                        "title": str(item.get("title", "") or ""),
                        "location": str(item.get("location", "") or ""),
                        "company": str(item.get("company", "") or ""),
                        "source": str(item.get("source", "") or ""),
                        "url": str(item.get("url", "") or ""),
                        "posted_date": posted_date,
                        "search_text": search_text,
                        "fixture_expected_match": item.get("fixture_expected_match", None),
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
    optional_fieldnames = ["profile_track", "profile_signal_hits"]
    fieldnames.extend([name for name in optional_fieldnames if any(name in r for r in rows)])
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
    optional_fieldnames = ["profile_track", "profile_signal_hits"]
    fieldnames.extend([name for name in optional_fieldnames if any(name in r for r in rows)])
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


def _load_skip_live_fetch_jobs() -> List[Dict[str, str]]:
    jobs: List[Dict[str, str]] = []
    for fixture_path in SKIP_LIVE_FETCH_FIXTURES:
        if not fixture_path.exists():
            continue
        try:
            payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        except Exception:
            logger.warning("skip-live-fetch fixture could not be read", extra={"path": str(fixture_path)}, exc_info=True)
            continue
        if not isinstance(payload, list):
            continue
        for item in payload:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "") or "").strip()
            company = str(item.get("company", "") or "").strip()
            source = str(item.get("source", "") or "fixture").strip() or "fixture"
            url = str(item.get("url", "") or "").strip()
            search_text = str(item.get("search_text", "") or "").strip()
            if not title or not url:
                continue
            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": "Remote",
                    "source": source,
                    "url": url,
                    "posted_date": datetime.now(UTC).strftime("%Y-%m-%d"),
                    "description": search_text,
                    "fixture_expected_match": bool(item.get("expected_should_match", True)),
                }
            )
    return jobs


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Job discovery orchestrator")
    parser.add_argument("--out-dir", dest="out_dir", default=None, help="Override output directory")
    parser.add_argument("--summary-only", dest="summary_only", action="store_true", help="Run discovery without CSV export")
    parser.add_argument("--enrich", dest="enrich", action="store_true", help="Run enrichment + scoring and export artifacts")
    parser.add_argument("--schedule", dest="schedule", action="store_true", help="Enable scheduling gate (Phase 3B)")
    parser.add_argument("--skip-live-fetch", dest="skip_live_fetch", action="store_true", help="Use deterministic fixtures instead of live source fetches")
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
    if args.skip_live_fetch:
        os.environ["SKIP_LIVE_FETCH"] = "true"

    json_cfg = os.path.join(_ROOT, "config", "env.json")
    if not os.path.exists(json_cfg):
        json_cfg = os.path.join(_ROOT, "config", "env.sample.json")
    config.initialize(json_path=json_cfg)

    environment = config.get("SYSTEM_ENVIRONMENT", "development")
    log_level = config.get("SYSTEM_LOG_LEVEL", "INFO")
    out_dir = str(args.out_dir or config.get("SYSTEM_OUTPUT_DIRECTORY", "output"))
    cfg_root = config.to_dict()

    def _cfg_bool(key: str) -> bool:
        value = cfg_root.get(key, None)
        if isinstance(value, bool):
            return value
        if value is not None:
            return bool(value)
        return bool(config.get_bool(key, False))

    # Filters from config
    keywords = normalize_terms(config.get_list("JOB_FILTER_KEYWORDS", ["software engineer", "developer"]) or [])
    locations = normalize_terms(config.get_list("JOB_FILTER_LOCATIONS", ["Remote"]) or [])
    exclude = normalize_terms(config.get_list("JOB_FILTER_EXCLUDE_KEYWORDS", ["volunteer"]) or [])
    include_role_tags = normalize_terms(config.get_list("JOB_FILTER_INCLUDE_ROLE_TAGS", []) or [])
    exclude_role_tags = normalize_terms(config.get_list("JOB_FILTER_EXCLUDE_ROLE_TAGS", []) or [])
    include_stack_tags = normalize_terms(config.get_list("JOB_FILTER_INCLUDE_STACK_TAGS", []) or [])
    exclude_stack_tags = normalize_terms(config.get_list("JOB_FILTER_EXCLUDE_STACK_TAGS", []) or [])
    filters_cfg = cfg_root.get("job_discovery", {}).get("filters", {})
    title_exclude = normalize_terms(filters_cfg.get("title_exclude_keywords", []) or [])
    title_terms = normalize_terms(filters_cfg.get("title_terms", []) or [])
    profile_signals = normalize_terms(filters_cfg.get("profile_signals", []) or [])
    try:
        profile_signals_min = int(filters_cfg.get("profile_signals_min", 0) or 0)
    except Exception:
        profile_signals_min = 0
    raw_profile_tracks = filters_cfg.get("profile_tracks", []) or []
    profile_tracks: List[Dict[str, Any]] = []
    if isinstance(raw_profile_tracks, list):
        for idx, item in enumerate(raw_profile_tracks):
            if not isinstance(item, dict):
                continue
            track_name = str(item.get("name", "") or "").strip() or f"track_{idx + 1}"
            track_label = str(item.get("label", "") or "").strip() or track_name
            track_signals = normalize_terms(item.get("signals", []) or [])
            track_title_terms = normalize_terms(item.get("title_terms", []) or [])
            track_title_qualifiers = normalize_terms(item.get("title_qualifiers", []) or [])
            track_title_required_terms = normalize_terms(item.get("title_required_terms", []) or [])
            try:
                track_min_hits = int(item.get("min_hits", 1) or 1)
            except Exception:
                track_min_hits = 1
            if track_signals or track_title_terms or track_title_qualifiers or track_title_required_terms:
                profile_tracks.append(
                    {
                        "name": track_name,
                        "label": track_label,
                        "signals": track_signals,
                        "title_terms": track_title_terms,
                        "title_qualifiers": track_title_qualifiers,
                        "title_required_terms": track_title_required_terms,
                        "min_hits": max(1, track_min_hits),
                    }
                )
                title_terms.extend(term for term in track_title_terms if term not in title_terms)
    has_tag_filters = any(
        [include_role_tags, exclude_role_tags, include_stack_tags, exclude_stack_tags]
    )

    print("Job discovery v1  starting")
    print(
        f"Env: {environment} | Log: {log_level} | "
        f"Keywords: {', '.join(keywords) or '-'} | Title terms: {', '.join(title_terms) or '-'} | Locations: {', '.join(locations) or '-'} | Exclude: {', '.join(exclude) or '-'} | Title exclude: {', '.join(title_exclude) or '-'}"
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
    if profile_tracks:
        for track in profile_tracks:
            print(
                "Profile track enabled | "
                f"{track['label']} | "
                f"Min hits: {track['min_hits']} | "
                f"Signals: {', '.join(track['signals'])} | "
                f"Title terms: {', '.join(track.get('title_terms', [])) or '-'} | "
                f"Title qualifiers: {', '.join(track.get('title_qualifiers', [])) or '-'} | "
                f"Title required: {', '.join(track.get('title_required_terms', [])) or '-'}"
            )
    elif profile_signals and profile_signals_min > 0:
        print(
            "Profile signals enabled | "
            f"Min hits: {profile_signals_min} | "
            f"Signals: {', '.join(profile_signals)}"
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
    telemetry_enabled = _cfg_bool("GREENHOUSE_ENABLED")
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
        profile_filtered_out = 0
        track_match_counts: Dict[str, int] = {track["name"]: 0 for track in profile_tracks}
        for job in jobs:
            if matches_filters(
                job.get("title", ""),
                job.get("location", ""),
                keywords,
                locations,
                exclude,
                job.get("search_text", ""),
                title_terms,
                title_exclude,
            ):
                combined = " ".join(
                    [
                        str(job.get("title", "") or ""),
                        str(job.get("search_text", "") or ""),
                    ]
                ).lower()
                selected_track_name = ""
                selected_track_hits = 0
                selected_track_label = ""
                if profile_tracks:
                    best_track, best_hits, selected_track_label = _select_profile_track(
                        job.get("title", ""),
                        combined,
                        profile_tracks,
                    )
                    if best_track is None:
                        profile_filtered_out += 1
                        continue
                    selected_track_name = str(best_track["name"])
                    selected_track_hits = best_hits
                    track_match_counts[selected_track_name] = track_match_counts.get(selected_track_name, 0) + 1
                elif profile_signals and profile_signals_min > 0:
                    signal_hits = sum(1 for sig in profile_signals if sig and sig in combined)
                    if signal_hits < profile_signals_min:
                        profile_filtered_out += 1
                        continue
                    selected_track_hits = signal_hits
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
                matched_job = dict(job)
                if selected_track_label:
                    matched_job["profile_track"] = selected_track_label
                if selected_track_hits:
                    matched_job["profile_signal_hits"] = str(selected_track_hits)
                matched.append(matched_job)

        fixture_expectations: Dict[str, bool] = {}
        for job in jobs:
            raw_expected = job.get("fixture_expected_match", None)
            if raw_expected is None:
                continue
            expected = True
            if isinstance(raw_expected, bool):
                expected = raw_expected
            else:
                expected = str(raw_expected).strip().lower() not in {"false", "0", "no"}
            fixture_expectations[str(job.get("url", ""))] = expected

        print(f"Found {len(jobs)} jobs; {len(matched)} matched filters")
        if fixture_expectations:
            matched_urls = {str(row.get("url", "")) for row in matched}
            expected_true = {url for url, should_match in fixture_expectations.items() if should_match}
            expected_false = {url for url, should_match in fixture_expectations.items() if not should_match}
            false_negatives = sorted(expected_true - matched_urls)
            false_positives = sorted(expected_false & matched_urls)
            print(
                "Fixture expectations | "
                f"expected_match={len(expected_true)} | "
                f"expected_no_match={len(expected_false)} | "
                f"false_negatives={len(false_negatives)} | "
                f"false_positives={len(false_positives)}"
            )
            for url in false_negatives[:5]:
                print(f"  false_negative: {url}")
            for url in false_positives[:5]:
                print(f"  false_positive: {url}")
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
        "linkedin": _cfg_bool("LINKEDIN_ENABLED"),
        "indeed": _cfg_bool("INDEED_ENABLED"),
        "greenhouse": _cfg_bool("GREENHOUSE_ENABLED"),
        "lever": _cfg_bool("LEVER_ENABLED"),
        "ashby": _cfg_bool("ASHBY_ENABLED"),
        "ziprecruiter": _cfg_bool("ZIPRECRUITER_ENABLED"),
        "google_jobs": _cfg_bool("GOOGLEJOBS_ENABLED"),
        "glassdoor": _cfg_bool("GLASSDOOR_ENABLED"),
        "craigslist": _cfg_bool("CRAIGSLIST_ENABLED"),
        "goremote": _cfg_bool("GOREMOTE_ENABLED"),
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
                "profile_filtered_out": profile_filtered_out,
                "exported": len(matched),
            },
            "profile_tracks": [
                {
                    "name": track["name"],
                    "label": track["label"],
                    "min_hits": track["min_hits"],
                    "matched": track_match_counts.get(track["name"], 0),
                }
                for track in profile_tracks
            ],
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
            if discovery_error is None and _cfg_bool("GREENHOUSE_ENABLED") and not greenhouse_rows:
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
