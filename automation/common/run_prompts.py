"""
Combined runner for Phase 3E: generates outreach and resume prompts.

Invokes individual scripts with CLI flags and saves rendered outputs
into their respective output folders.
"""

from __future__ import annotations

import os
import sys
import argparse
import subprocess
import time
from automation.common.metrics import get_summary

# Ensure repo root on path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.config_loader import config  # type: ignore


def _default_paths():
    config.initialize()
    outreach_ctx = config.get("OUTREACH_USER_CONTEXT_PATH", os.path.join(_ROOT, "config", "outreach_context.sample.json"))
    outreach_outdir = config.get("OUTREACH_OUTPUT_DIRECTORY", os.path.join(config.get("SYSTEM_OUTPUT_DIRECTORY", os.path.join(_ROOT, "output")), "outreach"))
    resume_ctx = config.get("RESUME_USER_CONTEXT_PATH", os.path.join(_ROOT, "config", "resume_context.sample.json"))
    resume_outdir = config.get("RESUME_OUTPUT_DIRECTORY", os.path.join(config.get("SYSTEM_OUTPUT_DIRECTORY", os.path.join(_ROOT, "output")), "resume"))
    return outreach_ctx, outreach_outdir, resume_ctx, resume_outdir


def run(outreach_ctx: str, outreach_outdir: str, resume_ctx: str, resume_outdir: str, outreach_prompt: str | None, resume_prompt: str | None, no_sources: bool) -> int:
    outreach_script = os.path.join(_ROOT, "automation", "outreach", "scripts", "outreach_generator_v1.py")
    resume_script = os.path.join(_ROOT, "automation", "resume-tailoring", "scripts", "resume_tailor_v1.py")

    # Build commands
    outreach_cmd = [sys.executable, outreach_script, "--context", outreach_ctx, "--output-dir", outreach_outdir]
    resume_cmd = [sys.executable, resume_script, "--context", resume_ctx, "--output-dir", resume_outdir]
    if outreach_prompt:
        outreach_cmd += ["--prompt", outreach_prompt]
    if resume_prompt:
        resume_cmd += ["--prompt", resume_prompt]
    if no_sources:
        outreach_cmd.append("--no-sources")
        resume_cmd.append("--no-sources")

    print("Running outreach prompt generation...")
    t0 = time.perf_counter()
    r1 = subprocess.run(outreach_cmd)
    t1 = time.perf_counter()
    if r1.returncode != 0:
        print(f"Outreach script failed with code {r1.returncode}")
        return r1.returncode

    print("Running resume prompt generation...")
    r2 = subprocess.run(resume_cmd)
    t2 = time.perf_counter()
    if r2.returncode != 0:
        print(f"Resume script failed with code {r2.returncode}")
        return r2.returncode

    print(
        f"Both prompts generated and saved. Timing: outreach={int((t1-t0)*1000)}ms, resume={int((t2-t1)*1000)}ms"
    )
    try:
        summary = get_summary()
        print(f"Metrics summary: {summary}")
    except Exception:
        pass
    return 0


def main() -> int:
    outreach_ctx, outreach_outdir, resume_ctx, resume_outdir = _default_paths()

    parser = argparse.ArgumentParser(description="Combined runner for outreach and resume prompt rendering")
    parser.add_argument("--outreach-context", default=outreach_ctx, help="Path to outreach user context JSON")
    parser.add_argument("--outreach-output-dir", default=outreach_outdir, help="Directory to save outreach prompt")
    parser.add_argument("--resume-context", default=resume_ctx, help="Path to resume user context JSON")
    parser.add_argument("--resume-output-dir", default=resume_outdir, help="Directory to save resume prompt")
    parser.add_argument("--outreach-prompt", default=None, help="Override outreach template path")
    parser.add_argument("--resume-prompt", default=None, help="Override resume template path")
    parser.add_argument("--no-sources", action="store_true", help="Skip job discovery and use sample inputs")
    args = parser.parse_args()

    return run(
        outreach_ctx=args.outreach_context,
        outreach_outdir=args.outreach_output_dir,
        resume_ctx=args.resume_context,
        resume_outdir=args.resume_output_dir,
        outreach_prompt=args.outreach_prompt,
        resume_prompt=args.resume_prompt,
        no_sources=args.no_sources,
    )


if __name__ == "__main__":
    sys.exit(main())
