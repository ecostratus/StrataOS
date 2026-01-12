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
from datetime import datetime

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config
from automation.common.prompt_renderer import render_prompt
from automation.common.logging import log_event
from automation.common.metrics import inc
from automation.common.import_helpers import load_module_from_path

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
    parser.add_argument("--no-sources", dest="no_sources", action="store_true", help="Skip source fetch and use context only")
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

    def build_resume_context(job: dict) -> dict:
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
            # Base resume placeholder
            "master_resume": "[Paste master resume content here]",
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

    context = {**build_resume_context(job), **user_ctx}

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

if __name__ == "__main__":
    main()
