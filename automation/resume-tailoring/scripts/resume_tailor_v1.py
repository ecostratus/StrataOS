"""
Resume Tailoring v1
Placeholder for resume tailoring automation script.

This script will:
- Load master resume
- Load job posting
- Generate tailored resume using AI prompts
- Export formatted resume

See prompt-spec.md for full specification.
"""

import os
import sys
import json
import argparse
import time
import logging
from datetime import datetime
from typing import Any

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config
from automation.common.prompt_renderer import render_prompt
from automation.common.logging import log_event
from automation.common.metrics import inc
from automation.common.import_helpers import load_module_from_path

logger = logging.getLogger(__name__)

TRACK_TEMPLATE_POLICY = {
    "track_a_risk_governance": {
        "label": "A - Risk & AI Governance",
        "base_template": "Resume A",
        "headline_positioning": "Director, AI & Technology Risk / Enterprise AI Governance / Responsible AI Architecture",
    },
    "track_b_platform_stabilization": {
        "label": "B - Platform Stabilization",
        "base_template": "Resume B",
        "headline_positioning": "Enterprise Platform Governance & Transformation Leader / CMDB-CSDM Strategy, Platform Health",
    },
    "track_c_ai_product_cpo": {
        "label": "C - AI Product/CPO Conversion",
        "base_template": "Resume C",
        "headline_positioning": "Chief Product Officer / AI Product & Platform Executive / Enterprise Transformation Leader",
    },
}

TRACK_TITLE_FAMILY_TERMS = {
    "track_a_risk_governance": (
        "ai governance",
        "responsible ai",
        "technology risk",
        "risk",
        "governance",
        "trust",
        "safety",
        "compliance",
    ),
    "track_b_platform_stabilization": (
        "platform",
        "cmdb",
        "csdm",
        "service management",
        "operations",
        "stabilization",
        "reliability",
        "itom",
    ),
    "track_c_ai_product_cpo": (
        "chief product",
        "cpo",
        "product",
        "product manager",
        "product management",
        "platform executive",
        "strategy",
    ),
}

TRACK_BASE_RESUME_FIELD = {
    "track_a_risk_governance": "base_resume_a",
    "track_b_platform_stabilization": "base_resume_b",
    "track_c_ai_product_cpo": "base_resume_c",
}

DEFAULT_GAP_FORMAT = "GAP: JD requires [X]. Not found in source materials. Resume generated without this claim."


def _generate_final_artifact(prompt_text: str, artifact_kind: str = "resume") -> dict[str, Any]:
    """Generate final content via shared generation module (framework-independent)."""
    try:
        from webapp.backend.generation import generate_artifact  # type: ignore
    except Exception as exc:
        return {
            "ok": False,
            "content": "",
            "error_code": "generator_import_failed",
            "error_message": str(exc),
        }

    try:
        result = generate_artifact(prompt_text, artifact_kind)  # type: ignore[arg-type]
        return {
            "ok": bool(getattr(result, "ok", False)),
            "content": str(getattr(result, "content", "") or ""),
            "error_code": str(getattr(result, "error_code", "") or ""),
            "error_message": str(getattr(result, "error_message", "") or ""),
        }
    except Exception as exc:
        return {
            "ok": False,
            "content": "",
            "error_code": "generation_exception",
            "error_message": str(exc),
        }


def _normalize_track_name(value: str | None) -> str:
    raw = str(value or "").strip().lower()
    aliases = {
        "a": "track_a_risk_governance",
        "track_a": "track_a_risk_governance",
        "risk": "track_a_risk_governance",
        "risk_governance": "track_a_risk_governance",
        "b": "track_b_platform_stabilization",
        "track_b": "track_b_platform_stabilization",
        "platform": "track_b_platform_stabilization",
        "platform_stabilization": "track_b_platform_stabilization",
        "c": "track_c_ai_product_cpo",
        "track_c": "track_c_ai_product_cpo",
        "ai_product": "track_c_ai_product_cpo",
        "cpo": "track_c_ai_product_cpo",
    }
    if raw in TRACK_TEMPLATE_POLICY:
        return raw
    return aliases.get(raw, "")


def _infer_track_from_title(title: str) -> tuple[str, str]:
    title_l = str(title or "").lower()
    best_track = ""
    best_hits = -1
    for track, terms in TRACK_TITLE_FAMILY_TERMS.items():
        hits = sum(1 for term in terms if term in title_l)
        if hits > best_hits:
            best_hits = hits
            best_track = track
    if best_track and best_hits > 0:
        return best_track, f"title-family match ({best_hits} term hit(s))"
    return "track_b_platform_stabilization", "default fallback (no title-family match)"


def _looks_like_placeholder_text(value: str) -> bool:
    txt = str(value or "").strip().lower()
    if not txt:
        return False
    markers = (
        "placeholder",
        "not repeated",
        "pull from",
        "earlier document",
        "in this conversation",
        "not included",
        "full text pulled",
    )
    return any(marker in txt for marker in markers)


def _select_track_via_discovery_logic(job: dict) -> tuple[str, str, bool]:
    """Use discovery pipeline selectors to avoid duplicating precedence logic here."""
    mod = load_module_from_path("automation/job-discovery/scripts/job_discovery_v1.py", "job_discovery_v1")
    if not mod:
        return "", "", False

    build_profile_tracks = getattr(mod, "_build_profile_tracks", None)
    select_profile_track = getattr(mod, "_select_profile_track", None)
    if not callable(build_profile_tracks) or not callable(select_profile_track):
        return "", "", False

    try:
        filters_cfg = config.get("JOB_DISCOVERY_FILTERS", {}) if hasattr(config, "get") else {}
    except Exception:
        filters_cfg = {}
    if not isinstance(filters_cfg, dict):
        return "", "", False

    profile_tracks, _ = build_profile_tracks(filters_cfg)
    if not profile_tracks:
        return "", "", True

    title = str(job.get("title", "") or "")
    combined_text = " ".join(
        str(job.get(key, "") or "")
        for key in (
            "description",
            "summary",
            "content",
            "search_text",
            "domain_tags",
            "skills",
        )
    )

    selected, _hits, label = select_profile_track(title, combined_text, profile_tracks)
    if not selected:
        return "", "", True
    track_name = _normalize_track_name(str(selected.get("name", "") or ""))
    if not track_name:
        return "", "", True
    detail = f"discovery fallback ({label or track_name})"
    return track_name, detail, True


def _normalize_user_context(user_ctx: dict) -> dict:
    """Accept both flat resume context and nested tracks payload shapes."""
    if not isinstance(user_ctx, dict):
        return {}
    normalized = dict(user_ctx)

    tracks = user_ctx.get("tracks")
    if isinstance(tracks, dict):
        track_map = {
            "A": "base_resume_a",
            "B": "base_resume_b",
            "C": "base_resume_c",
        }
        for src_key, dest_key in track_map.items():
            payload = tracks.get(src_key)
            if isinstance(payload, dict):
                resume_text = str(payload.get("resume_text", "") or "").strip()
                if resume_text and not str(normalized.get(dest_key, "") or "").strip():
                    normalized[dest_key] = resume_text

    linkedin_payload = user_ctx.get("linkedin_history")
    if isinstance(linkedin_payload, dict):
        source_key = ""
        raw_value = ""
        for candidate_key in ("text", "full_text", "note"):
            candidate = str(linkedin_payload.get(candidate_key, "") or "").strip()
            if candidate:
                source_key = candidate_key
                raw_value = candidate
                break
        if source_key == "note" and _looks_like_placeholder_text(raw_value):
            logger.warning("Ignoring linkedin_history.note placeholder text; provide full LinkedIn history text instead")
            raw_value = ""
        if raw_value and not str(normalized.get("linkedin_profile", "") or "").strip():
            normalized["linkedin_profile"] = raw_value

    return normalized


def _resolve_track(job: dict, user_ctx: dict, explicit_track: str | None) -> tuple[str, str]:
    for candidate, reason in (
        (explicit_track, "cli override"),
        (job.get("profile_track"), "job profile_track"),
        (user_ctx.get("profile_track"), "context profile_track"),
    ):
        normalized = _normalize_track_name(str(candidate or ""))
        if normalized:
            return normalized, reason
    discovery_track, discovery_reason, selector_available = _select_track_via_discovery_logic(job)
    if discovery_track:
        return discovery_track, discovery_reason
    if not selector_available:
        logger.warning("discovery selector unavailable, using title-family fallback")
    return _infer_track_from_title(str(job.get("title", "") or ""))


def _build_inventory_block(user_ctx: dict) -> str:
    ordered_fields = [
        ("Resume A", "base_resume_a"),
        ("Resume B", "base_resume_b"),
        ("Resume C", "base_resume_c"),
        ("LinkedIn Profile", "linkedin_profile"),
        ("Operator Brief A", "operator_brief_a"),
        ("Operator Brief B", "operator_brief_b"),
        ("Operator Brief C", "operator_brief_c"),
    ]
    sections = []
    for label, field_name in ordered_fields:
        value = str(user_ctx.get(field_name, "") or "").strip()
        if value:
            sections.append(f"## {label}\n{value}")
    if not sections:
        fallback = str(user_ctx.get("master_resume", "") or "").strip()
        if fallback:
            sections.append(f"## Master Resume (fallback)\n{fallback}")
    return "\n\n".join(sections)


def _count_gap_lines(text: str) -> int:
    return sum(1 for line in str(text or "").splitlines() if line.strip().startswith("GAP:"))

def main():
    """Main entry point for resume tailoring."""
    config.initialize()
    environment = config.get("SYSTEM_ENVIRONMENT", "development")
    resume_path = config.get("RESUME_MASTER_RESUME_PATH", "./resumes/master_resume.docx")
    backup_on_tailor = config.get_bool("RESUME_BACKUP_ON_TAILOR", True)
    excel_auto_backup = config.get_bool("EXCEL_AUTO_BACKUP", True)
    default_context_path = config.get("RESUME_USER_CONTEXT_PATH", "./config/resume_context.sample.json")
    default_output_dir = config.get("RESUME_OUTPUT_DIRECTORY", os.path.join(config.get("SYSTEM_OUTPUT_DIRECTORY", "./output"), "resume"))

    print("Resume tailoring v1 - Structure placeholder")
    print(
        f"Env: {environment} | Master Resume: {resume_path} | "
        f"BackupOnTailor: {backup_on_tailor} | ExcelAutoBackup: {excel_auto_backup}"
    )

    parser = argparse.ArgumentParser(description="Resume tailoring prompt renderer")
    parser.add_argument("--context", dest="context_path", default=default_context_path, help="Path to user context JSON")
    parser.add_argument("--output-dir", dest="output_dir", default=default_output_dir, help="Directory to save rendered prompt")
    parser.add_argument("--prompt", dest="prompt_path_override", default=None, help="Override prompt template path")
    parser.add_argument("--job-json", dest="job_json", default=None, help="Path to a specific job JSON file")
    parser.add_argument("--profile-track", dest="profile_track", default=None, help="Optional track override (A/B/C or track_* value)")
    parser.add_argument("--no-sources", dest="no_sources", action="store_true", help="Skip source fetch and use context only")
    parser.add_argument("--generate-artifact", dest="generate_artifact", action="store_true", help="Call shared LLM generator and save final resume artifact")
    parser.add_argument("--require-artifact", dest="require_artifact", action="store_true", help="Exit non-zero when --generate-artifact cannot produce output")
    args = parser.parse_args()

    # Resolve sources import only if not in no-sources mode
    fetch_all_sources = None
    if not args.no_sources:
        try:
            from automation.job_discovery.scripts.sources import fetch_all_sources  # type: ignore
        except Exception:
            import importlib.util
            _sp = os.path.join(_ROOT, 'automation', 'job-discovery', 'scripts', 'sources.py')
            spec = importlib.util.spec_from_file_location("job_discovery_sources", _sp)
            if spec and spec.loader:
                _mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(_mod)  # type: ignore
                fetch_all_sources = getattr(_mod, 'fetch_all_sources', None)  # type: ignore

    # Try orchestrator for real jobs; fallback to sample
    jobs = []
    try:
        if fetch_all_sources:
            cfg = {
                "LEVER_ENABLED": config.get_bool("LEVER_ENABLED", False),
                "GREENHOUSE_ENABLED": config.get_bool("GREENHOUSE_ENABLED", False),
                "ASHBY_ENABLED": config.get_bool("ASHBY_ENABLED", False),
                "INDEED_ENABLED": config.get_bool("INDEED_ENABLED", False),
                "ZIPRECRUITER_ENABLED": config.get_bool("ZIPRECRUITER_ENABLED", False),
                "GOOGLEJOBS_ENABLED": config.get_bool("GOOGLEJOBS_ENABLED", False),
                "GLASSDOOR_ENABLED": config.get_bool("GLASSDOOR_ENABLED", False),
                "CRAIGSLIST_ENABLED": config.get_bool("CRAIGSLIST_ENABLED", False),
                "GOREMOTE_ENABLED": config.get_bool("GOREMOTE_ENABLED", False),
                "ENRICHMENT_ENABLED": config.get_bool("ENRICHMENT_ENABLED", True),
            }
            jobs = fetch_all_sources(cfg)
    except Exception:
        jobs = []

    # Resolve enrichment two-stage import
    try:
        from automation.job_discovery.scripts.enrichment_transforms import enrich_job  # type: ignore
    except Exception:
        mod = load_module_from_path("automation/job-discovery/scripts/enrichment_transforms.py", "enrichment_transforms")
        if mod:
            enrich_job = getattr(mod, "enrich_job", lambda x: x)  # type: ignore
        else:
            def enrich_job(x):  # type: ignore
                return x

    if args.job_json:
        try:
            with open(args.job_json, "r", encoding="utf-8") as f:
                loaded_job = json.load(f)
            if isinstance(loaded_job, list) and loaded_job:
                job = loaded_job[0]
            elif isinstance(loaded_job, dict):
                job = loaded_job
            else:
                job = {}
            if job:
                jobs = [enrich_job(job)]
        except Exception:
            jobs = []

    if not jobs:
        job = {
            "job_id": "demo2",
            "title": "Lead Data Engineer (AWS, Kafka, Spark)",
            "company": "Example Corp",
            "location": "Remote",
            "url": "https://jobs.example/demo2",
            "source": "demo",
            "posted_at": "2026-01-10",
        }
        jobs = [enrich_job(job)]

    job = jobs[0]

    def build_resume_context(job: dict, user_ctx: dict) -> dict:
        selected_track, track_reason = _resolve_track(job, user_ctx, args.profile_track)
        policy = TRACK_TEMPLATE_POLICY[selected_track]
        selected_resume_field = TRACK_BASE_RESUME_FIELD[selected_track]
        selected_base_resume = str(
            user_ctx.get(selected_resume_field)
            or user_ctx.get("master_resume")
            or ""
        ).strip()
        ground_truth_inventory = _build_inventory_block(user_ctx)
        return {
            "company_name": job.get("company"),
            "job_title": job.get("title"),
            "job_description": "",
            # Enriched context
            "seniority": job.get("seniority"),
            "domain_tags": job.get("domain_tags", []),
            "stack": job.get("stack", []),
            "skills": job.get("skills", []),
            "tailoring_focus": ", ".join(job.get("domain_tags", [])),
            "profile_track": selected_track,
            "selected_track_label": policy["label"],
            "selected_base_template": policy["base_template"],
            "selected_headline_positioning": policy["headline_positioning"],
            "track_selection_reason": track_reason,
            "selected_base_resume": selected_base_resume,
            "ground_truth_inventory": ground_truth_inventory,
            "policy_gap_format": DEFAULT_GAP_FORMAT,
            # Backward compatible placeholder for legacy prompt content
            "master_resume": user_ctx.get("master_resume", "[Paste master resume content here]"),
        }

    # Load user context file and merge
    user_ctx = {}
    try:
        with open(args.context_path, "r", encoding="utf-8") as f:
            user_ctx = json.load(f)
            if not isinstance(user_ctx, dict):
                user_ctx = {}
    except Exception:
        user_ctx = {}

    user_ctx = _normalize_user_context(user_ctx)

    context = {**user_ctx, **build_resume_context(job, user_ctx)}

    prompt_path = args.prompt_path_override or os.path.join(_ROOT, "prompts", "resume", "resume_tailor_prompt_v1.md")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            template_str = f.read()
    except Exception:
        template_str = "Tailor resume for {{ job_title }} at {{ company_name }} focusing on {{ tailoring_focus }}."

    t0 = time.perf_counter()
    prompt = render_prompt(template_str, context)
    t1 = time.perf_counter()
    render_ms = int((t1 - t0) * 1000)
    gap_count = _count_gap_lines(prompt)
    print("----- Resume Tailoring Prompt -----")
    print(prompt)

    # Save to output with timestamp
    try:
        os.makedirs(args.output_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(args.output_dir, f"resume_prompt_{ts}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"Saved: {out_path}")
        log_event(
            "resume",
            {
                "event": "render_complete",
                "context_keys": sorted(list(context.keys())),
                "render_ms": render_ms,
                "selected_track": context.get("profile_track"),
                "selected_track_label": context.get("selected_track_label"),
                "selected_base_template": context.get("selected_base_template"),
                "gap_count": gap_count,
                "output_path": out_path,
            },
        )
        inc("resume", "renders")
    except Exception as e:
        print(f"Warning: could not save prompt: {e}")
        log_event(
            "resume",
            {
                "event": "render_error",
                "error": str(e),
                "render_ms": render_ms,
            },
        )
        inc("resume", "errors")

    if args.generate_artifact:
        generation = _generate_final_artifact(prompt, "resume")
        if generation.get("ok") and generation.get("content"):
            artifact_path = os.path.join(args.output_dir, f"resume_artifact_{ts}.txt")
            try:
                with open(artifact_path, "w", encoding="utf-8") as f:
                    f.write(str(generation.get("content", "")))
                print(f"Artifact Saved: {artifact_path}")
                log_event(
                    "resume",
                    {
                        "event": "generation_complete",
                        "artifact_path": artifact_path,
                        "artifact_chars": len(str(generation.get("content", ""))),
                    },
                )
                inc("resume", "artifact_generations")
            except Exception as exc:
                print(f"Warning: could not save generated artifact: {exc}")
                log_event(
                    "resume",
                    {
                        "event": "generation_save_error",
                        "error": str(exc),
                    },
                )
                inc("resume", "errors")
                if args.require_artifact:
                    sys.exit(3)
        else:
            err_code = str(generation.get("error_code", "generation_failed") or "generation_failed")
            err_message = str(generation.get("error_message", "The content could not be generated right now.") or "The content could not be generated right now.")
            print(f"Artifact Generation Failed [{err_code}]: {err_message}")
            log_event(
                "resume",
                {
                    "event": "generation_error",
                    "error_code": err_code,
                    "error_message": err_message,
                },
            )
            inc("resume", "errors")
            if args.require_artifact:
                sys.exit(2)

if __name__ == "__main__":
    main()
