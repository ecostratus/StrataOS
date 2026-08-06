"""Weekly Review Generator v1.

Renders a weekly review/governance prompt from context and saves output
for downstream generation.
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


def main() -> None:
    config.initialize()
    default_context_path = "./config/weekly_review_context.sample.json"
    default_output_dir = os.path.join(config.get("SYSTEM_OUTPUT_DIRECTORY", "./output"), "review")

    parser = argparse.ArgumentParser(description="Weekly review prompt renderer")
    parser.add_argument("--context", dest="context_path", default=default_context_path)
    parser.add_argument("--output-dir", dest="output_dir", default=default_output_dir)
    parser.add_argument("--prompt", dest="prompt_path_override", default=None)
    args = parser.parse_args()

    context = _load_json(args.context_path)

    prompt_path = args.prompt_path_override or os.path.join(
        _ROOT, "prompts", "review", "weekly_review_prompt_v1.md"
    )
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            template_str = f.read()
    except Exception:
        template_str = "Run a weekly review for week ending {{week_ending_date}}."

    prompt = render_prompt(template_str, context)
    print("----- Weekly Review Prompt -----")
    print(prompt)

    try:
        os.makedirs(args.output_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(args.output_dir, f"weekly_review_prompt_{ts}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"Saved: {out_path}")
        log_event(
            "review",
            {
                "event": "prompt_rendered",
                "week_ending_date": context.get("week_ending_date", ""),
                "output_path": out_path,
            },
        )
        inc("weekly_review_prompts_rendered")
    except Exception as exc:
        print(f"WARNING: could not save output: {exc}")


if __name__ == "__main__":
    main()
