"""Interview Prep Generator v1.

Renders an interview-prep prompt using context and optional job JSON,
then saves output for downstream generation.
"""

import argparse
import json
import os
import sys
from datetime import datetime

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from automation.common.logging import log_event
from automation.common.metrics import inc
from automation.common.prompt_renderer import render_prompt
from config.config_loader import config


def _load_json(path: str) -> dict:
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _context_from_job(job_json: dict) -> dict:
    role_tags = job_json.get("role_tags", [])
    if isinstance(role_tags, list):
        key_requirements = ", ".join(str(x) for x in role_tags if str(x).strip())
    else:
        key_requirements = ""

    return {
        "company_name": str(job_json.get("company", "") or ""),
        "industry": str(job_json.get("source", "") or ""),
        "company_size": str(job_json.get("company_size", "") or ""),
        "recent_news": str(job_json.get("recent_news", "") or ""),
        "job_title": str(job_json.get("title", "") or ""),
        "job_description": str(job_json.get("description", "") or ""),
        "key_requirements": key_requirements,
    }


def main() -> None:
    config.initialize()
    default_context_path = "./config/interview_context.sample.json"
    default_output_dir = os.path.join(config.get("SYSTEM_OUTPUT_DIRECTORY", "./output"), "interview")

    parser = argparse.ArgumentParser(description="Interview prep prompt renderer")
    parser.add_argument("--context", dest="context_path", default=default_context_path)
    parser.add_argument("--output-dir", dest="output_dir", default=default_output_dir)
    parser.add_argument("--job-json", dest="job_json", default="")
    parser.add_argument("--prompt", dest="prompt_path_override", default=None)
    parser.add_argument("--no-sources", dest="no_sources", action="store_true")
    args = parser.parse_args()

    context = _load_json(args.context_path)
    job_payload = _load_json(args.job_json)
    merged_context = dict(context)
    merged_context.update(_context_from_job(job_payload))

    prompt_path = args.prompt_path_override or os.path.join(
        _ROOT, "prompts", "interview", "interview_prep_prompt_v1.md"
    )
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            template_str = f.read()
    except Exception:
        template_str = "Prepare interview notes for {{company_name}} and {{job_title}}."

    prompt = render_prompt(template_str, merged_context)
    print("----- Interview Prep Prompt -----")
    print(prompt)

    try:
        os.makedirs(args.output_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(args.output_dir, f"interview_prompt_{ts}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"Saved: {out_path}")
        log_event(
            "interview",
            {
                "event": "prompt_rendered",
                "company": merged_context.get("company_name", ""),
                "job_title": merged_context.get("job_title", ""),
                "output_path": out_path,
            },
        )
        inc("interview_prompts_rendered")
    except Exception as exc:
        print(f"WARNING: could not save output: {exc}")


if __name__ == "__main__":
    main()
