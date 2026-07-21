#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/webapp/frontend"
BACKEND_REQ="$ROOT_DIR/webapp/backend/requirements.txt"

DEV_MODE="false"
if [[ "${1:-}" == "--dev" ]]; then
  DEV_MODE="true"
fi

if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

echo "Using Python: $PYTHON_BIN"
"$PYTHON_BIN" -m pip install -q -r "$BACKEND_REQ"

if [[ "$DEV_MODE" == "true" ]]; then
  echo "Starting control center in dev mode"
  if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    (cd "$FRONTEND_DIR" && npm install)
  fi

  cleanup() {
    if [[ -n "${BACKEND_PID:-}" ]]; then kill "$BACKEND_PID" >/dev/null 2>&1 || true; fi
    if [[ -n "${FRONTEND_PID:-}" ]]; then kill "$FRONTEND_PID" >/dev/null 2>&1 || true; fi
  }
  trap cleanup EXIT INT TERM

  (
    cd "$ROOT_DIR"
    "$PYTHON_BIN" -m uvicorn webapp.backend.app:app --host 127.0.0.1 --port 8811 --reload
  ) &
  BACKEND_PID=$!

  (
    cd "$FRONTEND_DIR"
    npm run dev -- --host 127.0.0.1 --port 5173
  ) &
  FRONTEND_PID=$!

  echo "Backend: http://127.0.0.1:8811"
  echo "Frontend (dev): http://127.0.0.1:5173"
  wait
else
  echo "Starting control center in single-port mode"
  if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    (cd "$FRONTEND_DIR" && npm install)
  fi

  if [[ ! -d "$FRONTEND_DIR/dist" ]]; then
    echo "Building frontend assets..."
    (cd "$FRONTEND_DIR" && npm run build)
  fi

  cd "$ROOT_DIR"
  exec "$PYTHON_BIN" -m uvicorn webapp.backend.app:app --host 127.0.0.1 --port 8811
fi
