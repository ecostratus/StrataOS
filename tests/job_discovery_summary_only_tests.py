import os
import json
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "automation", "job-discovery", "scripts", "job_discovery_v1.py")
OUT_DIR = os.path.join(ROOT, "output")


def test_summary_only_creates_summary_not_csv(tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    # Run summary-only
    proc = subprocess.run(
        [sys.executable, SCRIPT, "--out-dir", str(out_dir), "--summary-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    # Ensure summary file exists
    summaries = sorted(out_dir.glob("*.summary.json"))
    assert summaries, "Summary JSON should be created"
    # Ensure no CSV created
    csvs = sorted(out_dir.glob("*.csv"))
    assert not csvs, "CSV should not be created in summary-only mode"
    # Validate summary content minimally
    with open(summaries[0], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "counts" in data and "enabled_sources" in data
