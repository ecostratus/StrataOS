"""
Consulting Offer Generator v1

Generates a consulting proposal prompt from a context file and renders it
using the prompt template, then saves the output for review.

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


def main():
    config.initialize()
    default_context_path = config.get(
        "CONSULTING_USER_CONTEXT_PATH", "./config/consulting_context.sample.json"
    )
    default_output_dir = config.get(
        "CONSULTING_OUTPUT_DIRECTORY",
        os.path.join(config.get("SYSTEM_OUTPUT_DIRECTORY", "./output"), "consulting"),
    )

    parser = argparse.ArgumentParser(description="Consulting offer prompt renderer")
    parser.add_argument("--context", dest="context_path", default=default_context_path)
    parser.add_argument("--output-dir", dest="output_dir", default=default_output_dir)
    parser.add_argument("--prompt", dest="prompt_path_override", default=None)
    args = parser.parse_args()

    context: dict = {}
    try:
        with open(args.context_path, "r", encoding="utf-8") as f:
            context = json.load(f)
            if not isinstance(context, dict):
                context = {}
    except Exception as exc:
        print(f"WARNING: could not load context from {args.context_path}: {exc}")

    prompt_path = args.prompt_path_override or os.path.join(
        _ROOT, "prompts", "consulting", "consulting_offer_prompt_v1.md"
    )
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            template_str = f.read()
    except Exception:
        template_str = "Create a consulting proposal for {{client_name}} regarding {{opportunity_description}}."

    t0 = time.perf_counter()
    prompt = render_prompt(template_str, context)
    render_ms = int((time.perf_counter() - t0) * 1000)

    print("----- Consulting Offer Prompt -----")
    print(prompt)

    try:
        os.makedirs(args.output_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(args.output_dir, f"consulting_prompt_{ts}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"Saved: {out_path}")
        log_event(
            "consulting",
            {
                "event": "prompt_rendered",
                "client": context.get("client_name", ""),
                "render_ms": render_ms,
                "output_path": out_path,
            },
        )
        inc("consulting_prompts_rendered")
    except Exception as exc:
        print(f"WARNING: could not save output: {exc}")


if __name__ == "__main__":
    main()

