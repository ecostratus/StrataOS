from __future__ import annotations

import csv
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output"
LOG_PATH = ROOT / "logs" / "events.jsonl"
DB_PATH = Path(os.environ.get("STRATAOS_DB_PATH", str(ROOT / "data" / "jobs.db")))

DISCOVERY_SCRIPT = ROOT / "automation" / "job-discovery" / "scripts" / "job_discovery_v1.py"
RESUME_SCRIPT = ROOT / "automation" / "resume-tailoring" / "scripts" / "resume_tailor_v1.py"
OUTREACH_SCRIPT = ROOT / "automation" / "outreach" / "scripts" / "outreach_generator_v1.py"

DEFAULT_RESUME_CONTEXT = ROOT / "config" / "resume_context.sample.json"
DEFAULT_OUTREACH_CONTEXT = ROOT / "config" / "outreach_context.sample.json"

PYTHON_BIN = os.environ.get("STRATAOS_PYTHON", sys.executable)

SCORING_THRESHOLDS = {
	"exceptional": 0.8,
	"strong": 0.6,
	"moderate": 0.4,
}

BUCKET_COLORS = {
	"Exceptional": "#15803d",
	"Strong": "#0ea5e9",
	"Moderate": "#eab308",
	"Weak": "#ef4444",
}


def utc_now() -> str:
	return datetime.now(timezone.utc).isoformat()


def connect_db() -> sqlite3.Connection:
	DB_PATH.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	return conn


def init_db() -> None:
	conn = connect_db()
	try:
		conn.executescript(
			"""
			CREATE TABLE IF NOT EXISTS runs (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				run_type TEXT NOT NULL,
				status TEXT NOT NULL,
				started_at TEXT NOT NULL,
				finished_at TEXT,
				summary_path TEXT,
				discovered_csv_path TEXT,
				enriched_json_path TEXT,
				scored_csv_path TEXT,
				stdout TEXT,
				stderr TEXT
			);

			CREATE TABLE IF NOT EXISTS jobs (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				run_id INTEGER NOT NULL,
				title TEXT,
				company TEXT,
				location TEXT,
				source TEXT,
				url TEXT,
				posted_date TEXT,
				score REAL,
				bucket TEXT,
				raw_json TEXT,
				FOREIGN KEY(run_id) REFERENCES runs(id)
			);

			CREATE TABLE IF NOT EXISTS prompt_runs (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				prompt_type TEXT NOT NULL,
				created_at TEXT NOT NULL,
				job_id INTEGER,
				output_path TEXT,
				stdout TEXT,
				stderr TEXT,
				FOREIGN KEY(job_id) REFERENCES jobs(id)
			);
			"""
		)
		conn.commit()
	finally:
		conn.close()


def _run_subprocess(command: list[str]) -> subprocess.CompletedProcess[str]:
	return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def _latest_path(pattern: str) -> Path | None:
	paths = [Path(p) for p in glob.glob(pattern)]
	if not paths:
		return None
	return max(paths, key=lambda p: p.stat().st_mtime)


def _extract_saved_prompt_path(stdout: str) -> str | None:
	m = re.search(r"Saved:\s*(.+)", stdout)
	if not m:
		return None
	return m.group(1).strip()


def _read_json(path: Path) -> Any:
	with path.open("r", encoding="utf-8") as f:
		return json.load(f)


def _discover_artifacts() -> dict[str, Path | None]:
	return {
		"summary": _latest_path(str(OUTPUT_DIR / "jobs_discovered_*.summary.json")),
		"discovered_csv": _latest_path(str(OUTPUT_DIR / "jobs_discovered_*.csv")),
		"enriched_json": _latest_path(str(OUTPUT_DIR / "jobs_enriched_*.json")),
		"scored_csv": _latest_path(str(OUTPUT_DIR / "jobs_scored_*.csv")),
	}


def _to_float(value: Any) -> float | None:
	if value is None or value == "":
		return None
	try:
		return float(value)
	except Exception:
		return None


def _load_jobs_from_artifacts(artifacts: dict[str, Path | None]) -> list[dict[str, Any]]:
	discovered_map: dict[str, dict[str, Any]] = {}
	scored_map: dict[str, dict[str, Any]] = {}
	enriched_map: dict[str, dict[str, Any]] = {}

	discovered = artifacts.get("discovered_csv")
	if discovered and discovered.exists():
		with discovered.open("r", encoding="utf-8", newline="") as f:
			for row in csv.DictReader(f):
				key = row.get("url") or f"{row.get('company','')}::{row.get('title','')}"
				discovered_map[key] = row

	scored = artifacts.get("scored_csv")
	if scored and scored.exists():
		with scored.open("r", encoding="utf-8", newline="") as f:
			for row in csv.DictReader(f):
				key = row.get("url") or f"{row.get('company','')}::{row.get('title','')}"
				scored_map[key] = row

	enriched = artifacts.get("enriched_json")
	if enriched and enriched.exists():
		loaded = _read_json(enriched)
		if isinstance(loaded, list):
			for row in loaded:
				if isinstance(row, dict):
					key = row.get("url") or f"{row.get('company','')}::{row.get('title','')}"
					enriched_map[key] = row

	keys = set(discovered_map.keys()) | set(scored_map.keys()) | set(enriched_map.keys())
	jobs: list[dict[str, Any]] = []
	for key in keys:
		base = discovered_map.get(key, {})
		scored_row = scored_map.get(key, {})
		enriched_row = enriched_map.get(key, {})
		merged = {
			"title": base.get("title") or scored_row.get("title") or enriched_row.get("title"),
			"company": base.get("company") or scored_row.get("company") or enriched_row.get("company"),
			"location": base.get("location") or scored_row.get("location") or enriched_row.get("location"),
			"source": base.get("source") or scored_row.get("source") or enriched_row.get("source"),
			"url": base.get("url") or scored_row.get("url") or enriched_row.get("url"),
			"posted_date": base.get("posted_date") or scored_row.get("posted_date") or enriched_row.get("posted_date"),
			"score": _to_float(scored_row.get("score")),
			"bucket": scored_row.get("bucket"),
			"raw_json": enriched_row or base or scored_row,
		}
		jobs.append(merged)
	return jobs


def _insert_run(run_type: str, status: str) -> int:
	conn = connect_db()
	try:
		cur = conn.execute(
			"INSERT INTO runs(run_type, status, started_at) VALUES(?,?,?)",
			(run_type, status, utc_now()),
		)
		conn.commit()
		return int(cur.lastrowid)
	finally:
		conn.close()


def _complete_run(run_id: int, status: str, artifacts: dict[str, Path | None], stdout: str, stderr: str) -> None:
	conn = connect_db()
	try:
		conn.execute(
			"""
			UPDATE runs
			SET status=?, finished_at=?, summary_path=?, discovered_csv_path=?, enriched_json_path=?, scored_csv_path=?, stdout=?, stderr=?
			WHERE id=?
			""",
			(
				status,
				utc_now(),
				str(artifacts.get("summary") or ""),
				str(artifacts.get("discovered_csv") or ""),
				str(artifacts.get("enriched_json") or ""),
				str(artifacts.get("scored_csv") or ""),
				stdout,
				stderr,
				run_id,
			),
		)
		conn.commit()
	finally:
		conn.close()


def _replace_jobs_for_run(run_id: int, jobs: list[dict[str, Any]]) -> int:
	conn = connect_db()
	try:
		conn.execute("DELETE FROM jobs WHERE run_id=?", (run_id,))
		for job in jobs:
			conn.execute(
				"""
				INSERT INTO jobs(run_id, title, company, location, source, url, posted_date, score, bucket, raw_json)
				VALUES(?,?,?,?,?,?,?,?,?,?)
				""",
				(
					run_id,
					job.get("title"),
					job.get("company"),
					job.get("location"),
					job.get("source"),
					job.get("url"),
					job.get("posted_date"),
					job.get("score"),
					job.get("bucket"),
					json.dumps(job.get("raw_json") or {}, ensure_ascii=False),
				),
			)
		conn.commit()
		return len(jobs)
	finally:
		conn.close()


def _get_job(job_id: int) -> dict[str, Any]:
	conn = connect_db()
	try:
		row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
		if not row:
			raise HTTPException(status_code=404, detail="Job not found")
		payload = dict(row)
		try:
			payload["raw_json"] = json.loads(payload.get("raw_json") or "{}")
		except Exception:
			payload["raw_json"] = {}
		return payload
	finally:
		conn.close()


class PromptRequest(BaseModel):
	job_id: int | None = None
	job_json: dict[str, Any] | None = None
	context_path: str | None = None
	no_sources: bool = True


app = FastAPI(title="StrataOS Control Center API", version="1.0.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
	init_db()


@app.get("/api/health")
def health() -> dict[str, Any]:
	return {"ok": True, "db": str(DB_PATH)}


@app.get("/api/metadata/scoring")
def scoring_metadata() -> dict[str, Any]:
	return {"thresholds": SCORING_THRESHOLDS, "bucketColors": BUCKET_COLORS}


@app.post("/api/runs/job-discovery")
def run_job_discovery() -> dict[str, Any]:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	run_id = _insert_run("job-discovery", "running")
	command = [
		PYTHON_BIN,
		str(DISCOVERY_SCRIPT),
		"--out-dir",
		str(OUTPUT_DIR),
		"--enrich",
	]
	proc = _run_subprocess(command)
	artifacts = _discover_artifacts()
	status = "success" if proc.returncode == 0 else "failed"
	_complete_run(run_id, status, artifacts, proc.stdout, proc.stderr)

	jobs = _load_jobs_from_artifacts(artifacts) if proc.returncode == 0 else []
	mirrored = _replace_jobs_for_run(run_id, jobs) if proc.returncode == 0 else 0
	if proc.returncode != 0:
		raise HTTPException(
			status_code=500,
			detail={"run_id": run_id, "stdout": proc.stdout, "stderr": proc.stderr},
		)

	return {"run_id": run_id, "status": status, "mirrored_jobs": mirrored}


@app.get("/api/runs")
def list_runs(limit: int = 30) -> list[dict[str, Any]]:
	conn = connect_db()
	try:
		rows = conn.execute(
			"SELECT id, run_type, status, started_at, finished_at FROM runs ORDER BY id DESC LIMIT ?",
			(limit,),
		).fetchall()
		return [dict(r) for r in rows]
	finally:
		conn.close()


@app.get("/api/jobs")
def list_jobs(limit: int = 100, run_id: int | None = None) -> list[dict[str, Any]]:
	conn = connect_db()
	try:
		if run_id is None:
			rows = conn.execute(
				"SELECT * FROM jobs ORDER BY id DESC LIMIT ?",
				(limit,),
			).fetchall()
		else:
			rows = conn.execute(
				"SELECT * FROM jobs WHERE run_id=? ORDER BY id DESC LIMIT ?",
				(run_id, limit),
			).fetchall()
		payload = []
		for row in rows:
			item = dict(row)
			try:
				item["raw_json"] = json.loads(item.get("raw_json") or "{}")
			except Exception:
				item["raw_json"] = {}
			payload.append(item)
		return payload
	finally:
		conn.close()


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int) -> dict[str, Any]:
	return _get_job(job_id)


def _create_prompt(prompt_type: str, request: PromptRequest) -> dict[str, Any]:
	if prompt_type not in {"resume", "outreach"}:
		raise HTTPException(status_code=400, detail="Unsupported prompt type")

	if prompt_type == "resume":
		script_path = RESUME_SCRIPT
		default_context = DEFAULT_RESUME_CONTEXT
		output_dir = OUTPUT_DIR / "resume"
	else:
		script_path = OUTREACH_SCRIPT
		default_context = DEFAULT_OUTREACH_CONTEXT
		output_dir = OUTPUT_DIR / "outreach"

	job_payload: dict[str, Any] | None = request.job_json
	if request.job_id is not None:
		job_payload = _get_job(request.job_id).get("raw_json") or {}
	if not job_payload:
		raise HTTPException(status_code=400, detail="Provide job_id or job_json")

	output_dir.mkdir(parents=True, exist_ok=True)
	context_path = Path(request.context_path) if request.context_path else default_context

	with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
		json.dump(job_payload, tmp, ensure_ascii=False)
		tmp_job_path = tmp.name

	command = [
		PYTHON_BIN,
		str(script_path),
		"--context",
		str(context_path),
		"--output-dir",
		str(output_dir),
		"--job-json",
		tmp_job_path,
	]
	if request.no_sources:
		command.append("--no-sources")

	proc = _run_subprocess(command)
	try:
		os.unlink(tmp_job_path)
	except Exception:
		pass

	saved_path = _extract_saved_prompt_path(proc.stdout)
	prompt_text = ""
	if saved_path and Path(saved_path).exists():
		prompt_text = Path(saved_path).read_text(encoding="utf-8")

	conn = connect_db()
	try:
		cur = conn.execute(
			"INSERT INTO prompt_runs(prompt_type, created_at, job_id, output_path, stdout, stderr) VALUES(?,?,?,?,?,?)",
			(
				prompt_type,
				utc_now(),
				request.job_id,
				saved_path,
				proc.stdout,
				proc.stderr,
			),
		)
		conn.commit()
		prompt_run_id = int(cur.lastrowid)
	finally:
		conn.close()

	if proc.returncode != 0:
		raise HTTPException(
			status_code=500,
			detail={"prompt_run_id": prompt_run_id, "stdout": proc.stdout, "stderr": proc.stderr},
		)

	return {
		"prompt_run_id": prompt_run_id,
		"prompt_type": prompt_type,
		"output_path": saved_path,
		"prompt_text": prompt_text,
	}


@app.post("/api/prompts/resume")
def create_resume_prompt(request: PromptRequest) -> dict[str, Any]:
	return _create_prompt("resume", request)


@app.post("/api/prompts/outreach")
def create_outreach_prompt(request: PromptRequest) -> dict[str, Any]:
	return _create_prompt("outreach", request)


@app.get("/api/activity")
def get_activity(limit: int = Query(default=100, ge=1, le=1000)) -> list[dict[str, Any]]:
	if not LOG_PATH.exists():
		return []
	lines = LOG_PATH.read_text(encoding="utf-8").splitlines()[-limit:]
	events: list[dict[str, Any]] = []
	for line in lines:
		try:
			parsed = json.loads(line)
			if isinstance(parsed, dict):
				events.append(parsed)
		except Exception:
			continue
	return events


frontend_dist = ROOT / "webapp" / "frontend" / "dist"
if frontend_dist.exists():
	assets_dir = frontend_dist / "assets"
	if assets_dir.exists():
		app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

	@app.get("/")
	def serve_frontend() -> FileResponse:
		return FileResponse(str(frontend_dist / "index.html"))

	@app.get("/{full_path:path}")
	def serve_frontend_spa(full_path: str) -> FileResponse:
		if full_path.startswith("api/"):
			raise HTTPException(status_code=404, detail="Not found")
		return FileResponse(str(frontend_dist / "index.html"))


