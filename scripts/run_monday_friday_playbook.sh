#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DAY_INPUT="${1:-auto}"
NO_SOURCES="${STRATAOS_NO_SOURCES:-false}"
RESET_METRICS="${STRATAOS_RESET_METRICS:-false}"

if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

normalize_day() {
  echo "$1" | tr '[:upper:]' '[:lower:]'
}

resolve_day() {
  local input
  input="$(normalize_day "$1")"
  if [[ "$input" == "auto" ]]; then
    date +%A | tr '[:upper:]' '[:lower:]'
    return
  fi
  echo "$input"
}

DAY="$(resolve_day "$DAY_INPUT")"

run_monday() {
  "$PYTHON_BIN" automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output --enrich
}

run_tuesday() {
  local args
  args=(
    automation/common/run_prompts.py
    --outreach-context config/outreach_context.sample.json
    --outreach-output-dir output/outreach
    --resume-context config/resume_context.sample.json
    --resume-output-dir output/resume
  )
  if [[ "$NO_SOURCES" == "true" ]]; then
    args+=(--no-sources)
  fi
  "$PYTHON_BIN" "${args[@]}"
}

run_wednesday() {
  "$PYTHON_BIN" -m pytest -q --tb=short
}

run_thursday() {
  "$PYTHON_BIN" automation/common/metrics_cli.py --summary
}

run_friday() {
  "$PYTHON_BIN" scripts/ci/check_docs.py
  "$PYTHON_BIN" automation/common/metrics_cli.py --summary
  if [[ "$RESET_METRICS" == "true" ]]; then
    "$PYTHON_BIN" automation/common/metrics_cli.py --reset
  fi
}

run_week() {
  run_monday
  run_tuesday
  run_wednesday
  run_thursday
  run_friday
}

case "$DAY" in
  monday)
    run_monday
    ;;
  tuesday)
    run_tuesday
    ;;
  wednesday)
    run_wednesday
    ;;
  thursday)
    run_thursday
    ;;
  friday)
    run_friday
    ;;
  week)
    run_week
    ;;
  *)
    echo "Unsupported day: $DAY"
    echo "Usage: scripts/run_monday_friday_playbook.sh [auto|monday|tuesday|wednesday|thursday|friday|week]"
    exit 2
    ;;
esac
