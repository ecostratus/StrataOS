"""
Sampled integration harness for resume-tailoring runs against real exported jobs.

Purpose:
- Run the current resume tailoring pipeline over a stratified sample by track.
- Capture selected track, GAP line count, and output artifacts.
- Calibrate claim verifier behavior for false-positive/false-negative risk.

Usage:
    python3 automation/resume-tailoring/scripts/run_resume_integration_sample.py \
        --context config/resume_context_jnaphen.json \
        --max-per-track 4
"""

from __future__ import annotations

import argparse
import csv
import glob
import importlib.util
import json
import os
import random
import re
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = ROOT / "output" / "resume" / "integration-sample"


def _load_claim_verifier_module():
    script_path = ROOT / "automation" / "resume-tailoring" / "scripts" / "verify_resume_claims.py"
    spec = importlib.util.spec_from_file_location("verify_resume_claims", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load verify_resume_claims.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _normalize_track_label_to_key(label: str) -> str:
    value = (label or "").strip().lower()
    if value.startswith("a"):
        return "track_a_risk_governance"
    if value.startswith("b"):
        return "track_b_platform_stabilization"
    if value.startswith("c"):
        return "track_c_ai_product_cpo"
    return ""


def _select_source_csv(csv_path: str | None) -> Path:
    if csv_path:
        p = Path(csv_path)
        if not p.exists():
            raise FileNotFoundError(f"CSV not found: {p}")
        return p

    files = sorted(glob.glob(str(ROOT / "output" / "jobs_discovered_*.csv")))
    if not files:
        raise FileNotFoundError("No jobs_discovered CSV files found under output/")

    best_path = None
    best_rows = -1
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8", newline="") as f:
                row_count = sum(1 for _ in f) - 1
        except Exception:
            continue
        if row_count > best_rows:
            best_rows = row_count
            best_path = fp
    if not best_path:
        raise RuntimeError("Unable to select jobs CSV")
    return Path(best_path)


def _load_rows(path: Path) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _sample_rows(rows: List[Dict[str, str]], max_per_track: int, seed: int) -> List[Dict[str, str]]:
    groups: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        label = row.get("profile_track", "") or "untracked"
        groups.setdefault(label, []).append(row)

    rng = random.Random(seed)
    sampled: List[Dict[str, str]] = []
    for label in sorted(groups.keys()):
        bucket = groups[label]
        rng.shuffle(bucket)
        sampled.extend(bucket[:max_per_track])
    return sampled


def _count_gap_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip().startswith("GAP:"))


def _extract_selected_track(text: str) -> str:
    m = re.search(r"Selected Track:\s*(.+)", text)
    return m.group(1).strip() if m else ""


def _extract_saved_path(stdout_text: str) -> str:
    m = re.search(r"Saved:\s*(.+)", stdout_text)
    return m.group(1).strip() if m else ""


def _extract_artifact_path(stdout_text: str) -> str:
    m = re.search(r"Artifact Saved:\s*(.+)", stdout_text)
    return m.group(1).strip() if m else ""


def _extract_artifact_generation_error(stdout_text: str) -> tuple[str, str]:
    m = re.search(r"Artifact Generation Failed \[([^\]]+)\]:\s*(.+)", stdout_text)
    if not m:
        return "", ""
    return m.group(1).strip(), m.group(2).strip()


def _detect_artifact_type(saved_path: str, output_text: str) -> str:
    base = Path(saved_path).name.lower() if saved_path else ""
    text_head = output_text[:1000].lower()

    if base.startswith("resume_prompt_"):
        return "prompt_template"
    if base.startswith("resume_artifact_"):
        return "tailored_resume_output"
    if base.startswith("tailored_resume_") or base.startswith("generated_resume_"):
        return "tailored_resume_output"
    if "resume tailoring prompt v1" in text_head and "non-negotiable policy" in text_head:
        return "prompt_template"
    if "professional summary" in output_text and "professional experience" in output_text:
        return "tailored_resume_output"
    return "unknown"


def _extract_tailored_resume_section(output_text: str) -> str:
    # Enforce a section contract for verifier input; do not verify whole artifacts.
    match = re.search(
        r"###\s*1\.\s*Tailored Resume Content\s*(.*?)(?=\n###\s*2\.\s*Keyword Analysis|\Z)",
        output_text,
        re.IGNORECASE | re.DOTALL,
    )
    return (match.group(1) if match else "").strip()


def _build_unresolved_calibration() -> Dict[str, Any]:
    return {
        "status": "unresolved",
        "reason": (
            "Prior false-positive-like/false-negative-like observations came from contaminated "
            "prompt-template artifacts and are not a valid baseline."
        ),
        "prior_contaminated_observation": {
            "false_positive_like_count": 1,
            "false_negative_like_count": 1,
        },
        "use_prior_as_baseline": False,
        "fresh_hand_label_required": True,
    }


def _run_resume_tailor(job: Dict[str, str], context_path: Path, output_dir: Path, run_tag: str) -> Dict[str, Any]:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    job_path = output_dir / f"job_{ts}.json"
    sample_out_dir = output_dir / f"sample_{run_tag}"
    sample_out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "location": job.get("location", ""),
        "url": job.get("url", ""),
        "source": job.get("source", ""),
        "profile_track": _normalize_track_label_to_key(job.get("profile_track", "")),
    }
    with open(job_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    cmd = [
        sys.executable,
        str(ROOT / "automation" / "resume-tailoring" / "scripts" / "resume_tailor_v1.py"),
        "--context",
        str(context_path),
        "--output-dir",
        str(sample_out_dir),
        "--job-json",
        str(job_path),
        "--no-sources",
        "--generate-artifact",
    ]
    cmd_env = dict(os.environ)
    for key in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        cmd_env.pop(key, None)

    run = subprocess.run(cmd, capture_output=True, text=True, env=cmd_env)
    stdout_text = run.stdout or ""
    saved_path = _extract_saved_path(stdout_text)
    artifact_path = _extract_artifact_path(stdout_text)
    artifact_error_code, artifact_error_message = _extract_artifact_generation_error(stdout_text)

    prompt_text = ""
    if saved_path and Path(saved_path).exists():
        prompt_text = Path(saved_path).read_text(encoding="utf-8")

    artifact_text = ""
    if artifact_path and Path(artifact_path).exists():
        artifact_text = Path(artifact_path).read_text(encoding="utf-8")

    return {
        "exit_code": run.returncode,
        "stdout": stdout_text,
        "stderr": run.stderr or "",
        "saved_path": saved_path,
        "artifact_path": artifact_path,
        "artifact_generation_error_code": artifact_error_code,
        "artifact_generation_error_message": artifact_error_message,
        "selected_track_text": _extract_selected_track(prompt_text),
        "gap_count": _count_gap_lines(prompt_text),
        "prompt_text": prompt_text,
        "artifact_text": artifact_text,
    }


def _calibrate_claim_verifier(claims_verifier: Any, source_text: str) -> Dict[str, Any]:
    # Labeled calibration set to estimate verifier FP/FN behavior.
    cases = [
        {
            "name": "true_pass",
            "expect": "pass",
            "output": "## Skills\n- ServiceNow, AWS\n\n## Experience\n- Improved incident response by 45%.",
        },
        {
            "name": "semantic_rephrase_should_pass",
            "expect": "pass_semantic",
            "output": "## Skills\n- AI operations tooling\n\n## Experience\n- Improved incident response by 45%.",
        },
        {
            "name": "token_reuse_wrong_context_should_fail",
            "expect": "fail_semantic",
            "output": "## Skills\n- ServiceNow\n\n## Experience\n- Reduced employee attrition by 45%.",
        },
        {
            "name": "clear_fabrication",
            "expect": "fail",
            "output": "## Skills\n- Splunk ITSI\n\n## Experience\n- Reduced incidents by 60%.",
        },
    ]

    results: List[Dict[str, Any]] = []
    for case in cases:
        report = claims_verifier.verify_claims(source_text, case["output"])
        results.append(
            {
                "name": case["name"],
                "expect": case["expect"],
                "actual_passed": bool(report.get("passed")),
                "unsupported_skill_claims": report.get("unsupported_skill_claims", []),
                "unsupported_metric_claims": report.get("unsupported_metric_claims", []),
            }
        )

    fp = 0
    fn = 0
    for item in results:
        expect = item["expect"]
        passed = item["actual_passed"]
        if expect in {"pass", "pass_semantic"} and not passed:
            fp += 1
        if expect in {"fail", "fail_semantic"} and passed:
            fn += 1

    return {
        "cases": results,
        "false_positive_like_count": fp,
        "false_negative_like_count": fn,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=None, help="Optional explicit jobs_discovered CSV path")
    parser.add_argument("--context", default=str(ROOT / "config" / "resume_context_jnaphen.json"))
    parser.add_argument("--max-per-track", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = _select_source_csv(args.csv)
    rows = _load_rows(csv_path)
    sampled = _sample_rows(rows, args.max_per_track, args.seed)

    verifier_module = _load_claim_verifier_module()
    source_text = verifier_module.load_source_text(args.context)
    calibration = _build_unresolved_calibration()

    run_items: List[Dict[str, Any]] = []
    for idx, row in enumerate(sampled, start=1):
        result = _run_resume_tailor(row, Path(args.context), OUTPUT_DIR, str(idx))

        verifier_output_path = result.get("artifact_path") or result.get("saved_path") or ""
        output_text = result.get("artifact_text", "") or result.get("prompt_text", "")
        artifact_type = _detect_artifact_type(verifier_output_path, output_text)
        verifier_contract = "tailored_resume_section_v1"
        verifier_input_text = ""
        verifier_ran = False
        verifier_skip_reason = ""

        if artifact_type != "tailored_resume_output":
            verifier_skip_reason = (
                "artifact_type_not_supported_for_claim_verification"
            )
        else:
            verifier_input_text = _extract_tailored_resume_section(output_text)
            if not verifier_input_text:
                verifier_contract = "full_generated_artifact_v1"
                verifier_input_text = output_text.strip()
            if verifier_input_text:
                verifier_ran = True
            else:
                verifier_skip_reason = "missing_tailored_resume_section"

        claim_report: Dict[str, Any] = {
            "passed": False,
            "skills_checked": 0,
            "metrics_checked": 0,
            "unsupported_skill_claims": [],
            "unsupported_metric_claims": [],
        }
        if verifier_ran:
            claim_report = verifier_module.verify_claims(source_text, verifier_input_text)

        run_items.append(
            {
                "sample_index": idx,
                "title": row.get("title", ""),
                "company": row.get("company", ""),
                "source_profile_track": row.get("profile_track", ""),
                "source_profile_signal_hits": row.get("profile_signal_hits", ""),
                "resume_tailor_exit_code": result["exit_code"],
                "selected_track_text": result["selected_track_text"],
                "gap_count": result["gap_count"],
                "verifier_artifact_type": artifact_type,
                "verifier_contract": verifier_contract,
                "verifier_ran": verifier_ran,
                "verifier_skip_reason": verifier_skip_reason,
                "verifier_input_chars": len(verifier_input_text),
                "claim_verifier_passed": bool(claim_report.get("passed")) if verifier_ran else None,
                "unsupported_skill_claims": claim_report.get("unsupported_skill_claims", []),
                "unsupported_metric_claims": claim_report.get("unsupported_metric_claims", []),
                "skills_checked": int(claim_report.get("skills_checked", 0)),
                "metrics_checked": int(claim_report.get("metrics_checked", 0)),
                "manual_review_status": "unresolved_fresh_hand_label_required",
                "manual_review_label": "",
                "manual_review_notes": "",
                "saved_path": result["saved_path"],
                "artifact_path": result.get("artifact_path", ""),
                "artifact_generation_error_code": result.get("artifact_generation_error_code", ""),
                "artifact_generation_error_message": result.get("artifact_generation_error_message", ""),
                "stderr": result["stderr"],
            }
        )

    report = {
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "csv_source": str(csv_path),
        "total_rows_in_csv": len(rows),
        "sampled_count": len(sampled),
        "max_per_track": args.max_per_track,
        "seed": args.seed,
        "calibration": calibration,
        "runs": run_items,
    }

    out_path = OUTPUT_DIR / f"resume_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Report: {out_path}")


if __name__ == "__main__":
    main()