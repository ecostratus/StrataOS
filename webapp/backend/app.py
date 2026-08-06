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
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from collections.abc import Iterable

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config.config_loader import config
from automation.common.import_helpers import load_module_from_path
from automation.common.logging import log_event

from . import generation as generation_module
from .generation import generate_artifact
from .schemas import (
	ArtifactResult,
	JobStatusUpdateRequest,
	PromptArtifact,
	PromptError,
	PromptGenerationResponse,
	PromptRequest,
	SearchRequest,
	SearchResponse,
	SetupOpenAIKeyRequest,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output"
LOG_PATH = ROOT / "logs" / "events.jsonl"
DB_PATH = Path(os.environ.get("STRATAOS_DB_PATH", str(ROOT / "data" / "jobs.db")))
CONFIG_DIR = ROOT / "config"
ENV_SAMPLE_PATH = CONFIG_DIR / "env.sample.json"
ENV_JSON_PATH = CONFIG_DIR / "env.json"
OPENAI_KEY_PLACEHOLDER = "YOUR_OPENAI_API_KEY_HERE"

DISCOVERY_SCRIPT = ROOT / "automation" / "job-discovery" / "scripts" / "job_discovery_v1.py"
RESUME_SCRIPT = ROOT / "automation" / "resume-tailoring" / "scripts" / "resume_tailor_v1.py"
OUTREACH_SCRIPT = ROOT / "automation" / "outreach" / "scripts" / "outreach_generator_v1.py"
CONSULTING_SCRIPT = ROOT / "automation" / "consulting-funnel" / "scripts" / "consulting_offer_v1.py"
INTERVIEW_SCRIPT = ROOT / "automation" / "interview-prep" / "scripts" / "interview_prep_v1.py"
WEEKLY_REVIEW_SCRIPT = ROOT / "automation" / "weekly-review" / "scripts" / "weekly_review_v1.py"

DEFAULT_RESUME_CONTEXT = ROOT / "config" / "resume_context.sample.json"
DEFAULT_OUTREACH_CONTEXT = ROOT / "config" / "outreach_context.sample.json"
DEFAULT_CONSULTING_CONTEXT = ROOT / "config" / "consulting_context.sample.json"
DEFAULT_INTERVIEW_CONTEXT = ROOT / "config" / "interview_context.sample.json"
DEFAULT_WEEKLY_REVIEW_CONTEXT = ROOT / "config" / "weekly_review_context.sample.json"
LOCAL_RESUME_CONTEXT = ROOT / "config" / "resume_context.local.json"

VERIFY_RESUME_OUTPUT = load_module_from_path(
	"automation/resume-tailoring/scripts/verify_resume_output.py",
	"verify_resume_output",
)

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

JOB_STATUS_VALUES = ("discovered", "applied", "interviewing", "offer", "rejected")
DEFAULT_JOB_STATUS = "discovered"
BUCKET_ORDER = ("Weak", "Moderate", "Strong", "Exceptional")

JOBS_MIGRATION_COLUMNS: dict[str, str] = {
	"status": f"TEXT NOT NULL DEFAULT '{DEFAULT_JOB_STATUS}'",
	"country_code": "TEXT",
	"state_region": "TEXT",
	"city": "TEXT",
	"salary_min": "REAL",
	"salary_max": "REAL",
	"salary_currency": "TEXT",
	"job_type": "TEXT",
	"work_type": "TEXT",
	"company_normalized": "TEXT",
	"title_normalized": "TEXT",
	"posted_at_utc": "TEXT",
	"search_document": "TEXT",
}

JOBS_INDEXES: dict[str, str] = {
	"idx_jobs_posted_at_utc": "CREATE INDEX IF NOT EXISTS idx_jobs_posted_at_utc ON jobs(posted_at_utc)",
	"idx_jobs_location": "CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(country_code, state_region, city)",
	"idx_jobs_job_type_work_type": "CREATE INDEX IF NOT EXISTS idx_jobs_job_type_work_type ON jobs(job_type, work_type)",
	"idx_jobs_company_normalized": "CREATE INDEX IF NOT EXISTS idx_jobs_company_normalized ON jobs(company_normalized)",
	"idx_jobs_title_normalized": "CREATE INDEX IF NOT EXISTS idx_jobs_title_normalized ON jobs(title_normalized)",
}


def utc_now() -> str:
	return datetime.now(timezone.utc).isoformat()


def connect_db() -> sqlite3.Connection:
	DB_PATH.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	return conn


def _existing_job_columns(conn: sqlite3.Connection) -> set[str]:
	rows = conn.execute("PRAGMA table_info(jobs)").fetchall()
	return {str(r["name"]) for r in rows}


def _ensure_jobs_schema(conn: sqlite3.Connection) -> None:
	existing = _existing_job_columns(conn)
	for column, sql_type in JOBS_MIGRATION_COLUMNS.items():
		if column in existing:
			continue
		conn.execute(f"ALTER TABLE jobs ADD COLUMN {column} {sql_type}")


def _ensure_jobs_indexes(conn: sqlite3.Connection) -> None:
	for stmt in JOBS_INDEXES.values():
		conn.execute(stmt)


def _jobs_index_status(conn: sqlite3.Connection) -> dict[str, bool]:
	rows = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='jobs'").fetchall()
	present = {str(r["name"]) for r in rows}
	return {name: (name in present) for name in JOBS_INDEXES}


def _normalize_value(value: Any) -> str:
	if value is None:
		return ""
	return " ".join(str(value).strip().lower().split())


def _resolve_resume_context_path() -> Path:
	configured = Path(str(config.get("RESUME_USER_CONTEXT_PATH", str(DEFAULT_RESUME_CONTEXT))) or str(DEFAULT_RESUME_CONTEXT))
	if configured.exists() and configured != DEFAULT_RESUME_CONTEXT:
		return configured

	if LOCAL_RESUME_CONTEXT.exists():
		return LOCAL_RESUME_CONTEXT

	if configured.exists():
		return configured

	return DEFAULT_RESUME_CONTEXT


def _to_number(value: Any) -> float | None:
	if value is None or value == "":
		return None
	try:
		return float(value)
	except Exception:
		return None


def _first_present(mapping: dict[str, Any], keys: Iterable[str]) -> Any:
	for key in keys:
		if key in mapping and mapping.get(key) not in (None, ""):
			return mapping.get(key)
	return None


def _derive_location_parts(location: str) -> tuple[str | None, str | None, str | None]:
	parts = [p.strip() for p in location.split(",") if p.strip()]
	if len(parts) >= 3:
		return parts[-1], parts[-2], ", ".join(parts[:-2])
	if len(parts) == 2:
		return None, parts[-1], parts[0]
	if len(parts) == 1:
		return None, None, parts[0]
	return None, None, None


def _derive_search_fields(job: dict[str, Any]) -> dict[str, Any]:
	raw = job.get("raw_json") if isinstance(job.get("raw_json"), dict) else {}
	title = str(job.get("title") or "")
	company = str(job.get("company") or "")
	location = str(job.get("location") or "")
	source = str(job.get("source") or "")
	posted_date = str(job.get("posted_date") or "")

	country_code = _first_present(raw, ("country_code", "country", "countryCode"))
	state_region = _first_present(raw, ("state_region", "state", "region"))
	city = _first_present(raw, ("city",))
	if not any((country_code, state_region, city)):
		derived_country, derived_state, derived_city = _derive_location_parts(location)
		country_code = country_code or derived_country
		state_region = state_region or derived_state
		city = city or derived_city

	salary_min = _to_number(_first_present(raw, ("salary_min", "salaryMin", "min_salary")))
	salary_max = _to_number(_first_present(raw, ("salary_max", "salaryMax", "max_salary")))
	salary_currency = _first_present(raw, ("salary_currency", "salaryCurrency", "currency"))
	job_type = _first_present(raw, ("job_type", "employment_type", "employmentType"))
	work_type = _first_present(raw, ("work_type", "workType"))
	if work_type is None:
		loc_norm = location.lower()
		if "remote" in loc_norm:
			work_type = "remote"
		elif "hybrid" in loc_norm:
			work_type = "hybrid"
		elif "onsite" in loc_norm or "on-site" in loc_norm or "on site" in loc_norm:
			work_type = "onsite"

	posted_at_utc = _first_present(raw, ("posted_at_utc", "postedAtUtc", "posted_at"))
	if not posted_at_utc and posted_date:
		posted_at_utc = f"{posted_date}T00:00:00+00:00"

	search_document = " | ".join([
		title,
		company,
		location,
		source,
		str(_first_present(raw, ("description", "summary", "snippet")) or ""),
	])

	return {
		"country_code": country_code,
		"state_region": state_region,
		"city": city,
		"salary_min": salary_min,
		"salary_max": salary_max,
		"salary_currency": salary_currency,
		"job_type": job_type,
		"work_type": work_type,
		"company_normalized": _normalize_value(company),
		"title_normalized": _normalize_value(title),
		"posted_at_utc": posted_at_utc,
		"search_document": search_document,
	}


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
				status TEXT NOT NULL DEFAULT 'discovered',
				title TEXT,
				company TEXT,
				location TEXT,
				source TEXT,
				url TEXT,
				posted_date TEXT,
				score REAL,
				bucket TEXT,
				country_code TEXT,
				state_region TEXT,
				city TEXT,
				salary_min REAL,
				salary_max REAL,
				salary_currency TEXT,
				job_type TEXT,
				work_type TEXT,
				company_normalized TEXT,
				title_normalized TEXT,
				posted_at_utc TEXT,
				search_document TEXT,
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
		_ensure_jobs_schema(conn)
		_ensure_jobs_indexes(conn)
		# Startup guard: index creation should be idempotent and complete.
		index_status = _jobs_index_status(conn)
		if not all(index_status.values()):
			raise RuntimeError(f"Jobs search indexes missing after initialization: {index_status}")
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


def _validate_resume_source_map(artifact_text: str) -> tuple[bool, str]:
	text = str(artifact_text or "")
	if not text.strip():
		return False, "resume artifact is empty"

	lines = text.splitlines()
	source_map_start = None
	section1_start = None
	section2_start = None

	for idx, line in enumerate(lines):
		line_l = line.strip().lower()
		if source_map_start is None and re.search(r"(^|\s)0\.5\.?\s+source map\b", line_l):
			source_map_start = idx
		if section1_start is None and line_l.startswith("### 1."):
			section1_start = idx
		if section2_start is None and line_l.startswith("### 2."):
			section2_start = idx

	if source_map_start is None:
		return False, "missing Source Map section"
	if section1_start is None:
		return False, "missing Section 1 tailored content"

	mapping_lines = 0
	for line in lines[source_map_start:section1_start]:
		if "-> sourced from" in line.lower():
			mapping_lines += 1

	if mapping_lines == 0:
		return False, "source map contains no mapping lines"

	section1_end = section2_start if section2_start is not None else len(lines)
	bullet_lines = [line for line in lines[section1_start:section1_end] if line.strip().startswith("-")]
	if bullet_lines and mapping_lines < len(bullet_lines):
		return False, f"source map coverage mismatch (mappings={mapping_lines}, bullets={len(bullet_lines)})"

	return True, ""


def _validate_resume_output_guardrails(artifact_text: str) -> tuple[bool, str]:
	text = str(artifact_text or "")
	if not text.strip():
		return False, "resume artifact is empty"

	forbidden_patterns = (
		r"(?i)match score estimate\s*:",
		r"(?i)\b\d{1,3}%\s+match\b",
	)
	for pattern in forbidden_patterns:
		if re.search(pattern, text):
			return False, "contains unsupported ATS scoring"

	return True, ""


def _validate_resume_prose_claims(prompt_text: str, context_path: Path, artifact_text: str) -> tuple[bool, str]:
	verifier = VERIFY_RESUME_OUTPUT
	if verifier is None:
		return True, ""

	load_source_text = getattr(verifier, "load_source_text", None)
	find_violations = getattr(verifier, "find_resume_prose_claim_violations", None)
	if not callable(load_source_text) or not callable(find_violations):
		return True, ""

	try:
		source_text = load_source_text(str(context_path))
	except Exception:
		source_text = ""
	violations = find_violations(source_text, artifact_text or "", prompt_text)
	if violations:
		return False, "; ".join(violations[:5])
	return True, ""


def _resume_prose_validation_mode() -> str:
	"""Return runtime mode for prose-claim validation.

	Modes:
	- enforce: block artifact when prose claim violations are found
	- report: log violations but allow artifact (default MVP mode)
	- off: skip prose claim validation entirely
	"""
	raw = str(config.get("RESUME_PROSE_VALIDATION_MODE", "report") or "report").strip().lower()
	if raw in {"enforce", "report", "off"}:
		return raw
	return "report"


def _build_resume_source_map_repair_prompt(prompt_text: str, source_map_reason: str) -> str:
	return (
		"The previous resume draft failed source-map validation because: "
		f"{source_map_reason}. Rewrite the full resume from scratch and include a valid "
		"### 0.5. Source Map (required)" " section before Section 1. "
		"Every bullet in Section 1 must have exactly one mapping line in the Source Map. "
		"Do not omit the Source Map section, do not rename it, and do not return notes about the failure.\n\n"
		f"{prompt_text}"
	)


def _emit_resume_generation_event(event: str, prompt_run_id: int, **payload: Any) -> None:
	log_event(
		"resume",
		{
			"event": event,
			"prompt_run_id": prompt_run_id,
			**payload,
		},
		log_file=str(LOG_PATH),
	)


def _read_json(path: Path) -> Any:
	with path.open("r", encoding="utf-8") as f:
		return json.load(f)


def _read_json_object(path: Path) -> dict[str, Any]:
	if not path.exists():
		return {}
	try:
		loaded = _read_json(path)
		if isinstance(loaded, dict):
			return loaded
	except Exception:
		return {}
	return {}


def _write_json_object(path: Path, payload: dict[str, Any]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8") as f:
		json.dump(payload, f, ensure_ascii=False, indent=2)
		f.write("\n")


def _get_nested_value(source: dict[str, Any], parts: list[str], default: Any = None) -> Any:
	current: Any = source
	for part in parts:
		if isinstance(current, dict) and part in current:
			current = current[part]
		else:
			return default
	return current


def _set_nested_value(target: dict[str, Any], parts: list[str], value: Any) -> None:
	if not parts:
		return
	current: dict[str, Any] = target
	for part in parts[:-1]:
		next_value = current.get(part)
		if not isinstance(next_value, dict):
			next_value = {}
			current[part] = next_value
		current = next_value
	current[parts[-1]] = value


def _normalize_text(value: Any) -> str:
	if value is None:
		return ""
	return str(value).strip()


def _is_openai_configured(provider: str, api_key: str) -> bool:
	return provider == "openai" and bool(api_key) and api_key != OPENAI_KEY_PLACEHOLDER


def _build_setup_status() -> dict[str, Any]:
	has_env_json = ENV_JSON_PATH.exists()
	active_path = ENV_JSON_PATH if has_env_json else ENV_SAMPLE_PATH
	config_doc = _read_json_object(active_path)
	provider = _normalize_text(_get_nested_value(config_doc, ["ai_services", "provider"], "")).lower()
	api_key = _normalize_text(_get_nested_value(config_doc, ["ai_services", "openai", "api_key"], ""))
	configured = has_env_json and _is_openai_configured(provider, api_key)
	return {
		"configured": configured,
		"has_env_json": has_env_json,
		"provider": provider or None,
	}


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
			derived = _derive_search_fields(job)
			conn.execute(
				"""
				INSERT INTO jobs(
					run_id, status, title, company, location, source, url, posted_date, score, bucket,
					country_code, state_region, city, salary_min, salary_max, salary_currency,
					job_type, work_type, company_normalized, title_normalized, posted_at_utc,
					search_document, raw_json
				)
				VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
				""",
				(
					run_id,
					job.get("status") or DEFAULT_JOB_STATUS,
					job.get("title"),
					job.get("company"),
					job.get("location"),
					job.get("source"),
					job.get("url"),
					job.get("posted_date"),
					job.get("score"),
					job.get("bucket"),
					derived.get("country_code"),
					derived.get("state_region"),
					derived.get("city"),
					derived.get("salary_min"),
					derived.get("salary_max"),
					derived.get("salary_currency"),
					derived.get("job_type"),
					derived.get("work_type"),
					derived.get("company_normalized"),
					derived.get("title_normalized"),
					derived.get("posted_at_utc"),
					derived.get("search_document"),
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


def _normalize_items(items: list[str]) -> list[str]:
	normalized = [_normalize_value(item) for item in items]
	return [item for item in normalized if item]


def _build_search_applied_filters(payload: SearchRequest, page: int, page_size: int) -> dict[str, object]:
	return {
		"query": _normalize_value(payload.query),
		"keywords_exclude": _normalize_items(payload.keywords_exclude),
		"companies_include": _normalize_items(payload.companies_include),
		"companies_exclude": _normalize_items(payload.companies_exclude),
		"location": {
			"country": _normalize_value(payload.location.country),
			"state_region": _normalize_value(payload.location.state_region),
			"city": _normalize_value(payload.location.city),
		},
		"salary": {
			"min": payload.salary.min,
			"max": payload.salary.max,
			"currency": _normalize_value(payload.salary.currency),
		},
		"job_type": _normalize_items(payload.job_type),
		"work_type": _normalize_items(payload.work_type),
		"posted_within_days": payload.posted_within_days,
		"include_low_relevance": payload.include_low_relevance,
		"require_role_tags": payload.require_role_tags,
		"min_bucket": payload.min_bucket,
		"sort": payload.sort,
		"page": page,
		"page_size": page_size,
	}


def _normalize_bucket_threshold(value: str | None, default: str = "Moderate") -> str:
	raw = (value or default).strip().lower()
	mapping = {
		"weak": "Weak",
		"moderate": "Moderate",
		"strong": "Strong",
		"exceptional": "Exceptional",
	}
	normalized = mapping.get(raw)
	if not normalized:
		raise HTTPException(status_code=400, detail=f"Unsupported bucket threshold: {value}")
	return normalized


def _append_default_relevance_where(
	where: list[str],
	params: list[Any],
	*,
	include_low_relevance: bool,
	require_role_tags: bool,
	min_bucket: str,
) -> None:
	if include_low_relevance:
		return

	if require_role_tags:
		where.append("COALESCE(json_array_length(json_extract(raw_json, '$.role_tags')), 0) > 0")

	normalized_bucket = _normalize_bucket_threshold(min_bucket)
	min_index = BUCKET_ORDER.index(normalized_bucket)
	allowed_buckets = BUCKET_ORDER[min_index:]
	if allowed_buckets and len(allowed_buckets) < len(BUCKET_ORDER):
		placeholders = ",".join("?" for _ in allowed_buckets)
		where.append(f"COALESCE(bucket, '') IN ({placeholders})")
		params.extend(allowed_buckets)


def _build_jobs_search_where(payload: SearchRequest) -> tuple[list[str], list[Any]]:
	where: list[str] = ["1=1"]
	params: list[Any] = []
	_append_default_relevance_where(
		where,
		params,
		include_low_relevance=payload.include_low_relevance,
		require_role_tags=payload.require_role_tags,
		min_bucket=payload.min_bucket,
	)

	query_terms = _normalize_value(payload.query).split()
	for term in query_terms:
		like = f"%{term}%"
		where.append(
			"(" \
			"LOWER(COALESCE(search_document, '')) LIKE ? " \
			"OR LOWER(COALESCE(title, '')) LIKE ? " \
			"OR LOWER(COALESCE(company, '')) LIKE ?" \
			")"
		)
		params.extend([like, like, like])

	for term in _normalize_items(payload.keywords_exclude):
		where.append("LOWER(COALESCE(search_document, '')) NOT LIKE ?")
		params.append(f"%{term}%")

	companies_include = _normalize_items(payload.companies_include)
	if companies_include:
		placeholders = ",".join("?" for _ in companies_include)
		where.append(f"LOWER(COALESCE(company_normalized, company, '')) IN ({placeholders})")
		params.extend(companies_include)

	companies_exclude = _normalize_items(payload.companies_exclude)
	if companies_exclude:
		placeholders = ",".join("?" for _ in companies_exclude)
		where.append(f"LOWER(COALESCE(company_normalized, company, '')) NOT IN ({placeholders})")
		params.extend(companies_exclude)

	country = _normalize_value(payload.location.country)
	if country:
		where.append("LOWER(COALESCE(country_code, '')) = ?")
		params.append(country)

	state_region = _normalize_value(payload.location.state_region)
	if state_region:
		where.append("LOWER(COALESCE(state_region, '')) = ?")
		params.append(state_region)

	city = _normalize_value(payload.location.city)
	if city:
		where.append("LOWER(COALESCE(city, '')) = ?")
		params.append(city)

	if payload.salary.min is not None:
		where.append("COALESCE(salary_max, salary_min) >= ?")
		params.append(payload.salary.min)

	if payload.salary.max is not None:
		where.append("COALESCE(salary_min, salary_max) <= ?")
		params.append(payload.salary.max)

	currency = _normalize_value(payload.salary.currency)
	if currency:
		where.append("LOWER(COALESCE(salary_currency, '')) = ?")
		params.append(currency)

	job_type = _normalize_items(payload.job_type)
	if job_type:
		placeholders = ",".join("?" for _ in job_type)
		where.append(f"LOWER(COALESCE(job_type, '')) IN ({placeholders})")
		params.extend(job_type)

	work_type = _normalize_items(payload.work_type)
	if work_type:
		placeholders = ",".join("?" for _ in work_type)
		where.append(f"LOWER(COALESCE(work_type, '')) IN ({placeholders})")
		params.extend(work_type)

	if payload.posted_within_days is not None and payload.posted_within_days > 0:
		where.append("julianday('now') - julianday(COALESCE(posted_at_utc, posted_date)) <= ?")
		params.append(payload.posted_within_days)

	return where, params


def _jobs_sort_clause(sort_mode: str) -> str:
	if sort_mode == "posted_date":
		return "COALESCE(posted_at_utc, posted_date) DESC, id DESC"
	if sort_mode == "salary_desc":
		return "(salary_max IS NULL) ASC, salary_max DESC, id DESC"
	if sort_mode == "salary_asc":
		return "(salary_min IS NULL) ASC, salary_min ASC, id DESC"
	if sort_mode == "company_asc":
		return "LOWER(COALESCE(company, '')) ASC, id DESC"
	return "COALESCE(score, 0) DESC, COALESCE(posted_at_utc, posted_date) DESC, id DESC"


def _decode_jobs_rows(rows: list[sqlite3.Row]) -> list[dict[str, object]]:
	items: list[dict[str, object]] = []
	for row in rows:
		item: dict[str, object] = dict(row)
		try:
			item["raw_json"] = json.loads(str(item.get("raw_json") or "{}"))
		except Exception:
			item["raw_json"] = {}
		items.append(item)
	return items
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


@app.get("/api/setup/status")
def setup_status() -> dict[str, Any]:
	return _build_setup_status()


@app.post("/api/setup/openai-key")
def save_openai_key(request: SetupOpenAIKeyRequest) -> dict[str, Any]:
	api_key = _normalize_text(request.api_key)
	if not api_key:
		raise HTTPException(status_code=400, detail="Please provide an OpenAI API key.")
	if api_key == OPENAI_KEY_PLACEHOLDER:
		raise HTTPException(status_code=400, detail="Please provide a real OpenAI API key.")

	if ENV_JSON_PATH.exists():
		target_doc = _read_json_object(ENV_JSON_PATH)
	else:
		target_doc = _read_json_object(ENV_SAMPLE_PATH)

	_set_nested_value(target_doc, ["ai_services", "provider"], "openai")
	_set_nested_value(target_doc, ["ai_services", "openai", "api_key"], api_key)
	_write_json_object(ENV_JSON_PATH, target_doc)

	generation_module.config.initialize(
		env_path=str(ROOT / ".env"),
		json_path=str(ENV_JSON_PATH),
	)

	return {
		"saved": True,
		"configured": _build_setup_status().get("configured", False),
	}


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
def list_jobs(
	limit: int = 100,
	run_id: int | None = None,
	status: str | None = None,
	include_low_relevance: bool = False,
	require_role_tags: bool = True,
	min_bucket: str = Query(default="Moderate"),
) -> list[dict[str, Any]]:
	status_filter = _normalize_value(status)
	if status_filter and status_filter not in JOB_STATUS_VALUES:
		raise HTTPException(status_code=400, detail=f"Unsupported status: {status}")
	normalized_min_bucket = _normalize_bucket_threshold(min_bucket)

	conn = connect_db()
	try:
		where: list[str] = ["1=1"]
		params: list[Any] = []
		if run_id is not None:
			where.append("run_id=?")
			params.append(run_id)
		if status_filter:
			where.append("status=?")
			params.append(status_filter)
		_append_default_relevance_where(
			where,
			params,
			include_low_relevance=include_low_relevance,
			require_role_tags=require_role_tags,
			min_bucket=normalized_min_bucket,
		)
		where_sql = " AND ".join(where)
		rows = conn.execute(
			f"SELECT * FROM jobs WHERE {where_sql} ORDER BY id DESC LIMIT ?",
			[*params, limit],
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


@app.get("/api/jobs/statuses")
def list_job_statuses() -> dict[str, list[str]]:
	return {"items": list(JOB_STATUS_VALUES)}


@app.patch("/api/jobs/{job_id}/status")
def update_job_status(job_id: int, request: JobStatusUpdateRequest) -> dict[str, Any]:
	next_status = _normalize_value(request.status)
	if next_status not in JOB_STATUS_VALUES:
		raise HTTPException(status_code=400, detail=f"Unsupported status: {request.status}")

	conn = connect_db()
	try:
		updated = conn.execute(
			"UPDATE jobs SET status=? WHERE id=?",
			(next_status, job_id),
		)
		if updated.rowcount == 0:
			raise HTTPException(status_code=404, detail="Job not found")
		conn.commit()
	finally:
		conn.close()

	return _get_job(job_id)


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int) -> dict[str, Any]:
	return _get_job(job_id)


@app.post("/api/jobs/search", response_model=SearchResponse)
def search_jobs(request: SearchRequest) -> SearchResponse:
	page = max(1, request.page)
	page_size = max(1, min(250, request.page_size))
	offset = (page - 1) * page_size

	where_parts, params = _build_jobs_search_where(request)
	where_sql = " AND ".join(where_parts)
	sort_sql = _jobs_sort_clause(request.sort)

	started = time.perf_counter()
	conn = connect_db()
	try:
		total_row = conn.execute(
			f"SELECT COUNT(*) AS total FROM jobs WHERE {where_sql}",
			params,
		).fetchone()
		total = int(total_row["total"]) if total_row else 0

		rows = conn.execute(
			f"SELECT * FROM jobs WHERE {where_sql} ORDER BY {sort_sql} LIMIT ? OFFSET ?",
			[*params, page_size, offset],
		).fetchall()
	finally:
		conn.close()

	query_ms = int((time.perf_counter() - started) * 1000)
	return SearchResponse(
		items=_decode_jobs_rows(rows),
		page=page,
		page_size=page_size,
		total=total,
		applied_filters=_build_search_applied_filters(request, page, page_size),
		diagnostics={"query_ms": query_ms, "sort_mode": request.sort},
	)


def _create_prompt(prompt_type: str, request: PromptRequest) -> PromptGenerationResponse:
	if prompt_type not in {"resume", "outreach", "consulting", "interview", "weekly_review"}:
		raise HTTPException(status_code=400, detail="Unsupported prompt type")

	if prompt_type == "resume":
		script_path = RESUME_SCRIPT
		default_context = _resolve_resume_context_path()
		output_dir = OUTPUT_DIR / "resume"
	elif prompt_type == "interview":
		script_path = INTERVIEW_SCRIPT
		default_context = DEFAULT_INTERVIEW_CONTEXT
		output_dir = OUTPUT_DIR / "interview"
	elif prompt_type == "consulting":
		script_path = CONSULTING_SCRIPT
		default_context = DEFAULT_CONSULTING_CONTEXT
		output_dir = OUTPUT_DIR / "consulting"
	elif prompt_type == "weekly_review":
		script_path = WEEKLY_REVIEW_SCRIPT
		default_context = DEFAULT_WEEKLY_REVIEW_CONTEXT
		output_dir = OUTPUT_DIR / "review"
	else:
		script_path = OUTREACH_SCRIPT
		default_context = DEFAULT_OUTREACH_CONTEXT
		output_dir = OUTPUT_DIR / "outreach"

	# Context-only prompts do not require job_json.
	context_only_prompt_types = {"consulting", "weekly_review"}

	job_payload: dict[str, Any] | None = request.job_json
	if prompt_type not in context_only_prompt_types:
		if request.job_id is not None:
			job_payload = _get_job(request.job_id).get("raw_json") or {}
		if not job_payload:
			raise HTTPException(status_code=400, detail="Provide job_id or job_json")

	output_dir.mkdir(parents=True, exist_ok=True)
	context_path = Path(request.context_path) if request.context_path else default_context

	# Context-only prompts use context_path only; other prompts also pass a job JSON file.
	if prompt_type in context_only_prompt_types:
		command = [
			PYTHON_BIN,
			str(script_path),
			"--context",
			str(context_path),
			"--output-dir",
			str(output_dir),
		]
		tmp_job_path = None
	else:
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
	if tmp_job_path:
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
		if prompt_type == "resume" and proc.returncode == 4:
			_emit_resume_generation_event(
				"input_validation_failed",
				prompt_run_id,
				reason="invalid_input",
			)
			return PromptGenerationResponse(
				status="error",
				prompt_run_id=prompt_run_id,
				prompt_type=prompt_type,
				generation_path=None,
				artifact=None,
				prompt_text=prompt_text,
				output_path=saved_path,
				error=PromptError(
					message="Resume input validation failed. Populate source inventory and job description, then retry.",
					code="input_validation_failed",
				),
			)
		return PromptGenerationResponse(
			status="error",
			prompt_run_id=prompt_run_id,
			prompt_type=prompt_type,
			artifact=None,
			prompt_text=prompt_text,
			output_path=saved_path,
			error=PromptError(
				message="The prompt preparation step failed. Please try again.",
				code="prompt_build_failed",
			),
		)

	generation_path = "direct"
	artifact_result: ArtifactResult = generate_artifact(prompt_text, prompt_type)
	if not artifact_result.ok:
		_emit_resume_generation_event(
			"generation_failed",
			prompt_run_id,
			generation_path="direct",
			error_code=artifact_result.error_code or "generation_failed",
		)
		return PromptGenerationResponse(
			status="error",
			prompt_run_id=prompt_run_id,
			prompt_type=prompt_type,
			generation_path="direct",
			artifact=None,
			prompt_text=prompt_text,
			output_path=saved_path,
			error=PromptError(
				message=artifact_result.error_message or "The content could not be generated right now. Please try again.",
				code=artifact_result.error_code or "generation_failed",
			),
		)

	if prompt_type == "resume":
		source_map_ok, source_map_reason = _validate_resume_source_map(artifact_result.content or "")
		if not source_map_ok:
			repair_prompt_text = _build_resume_source_map_repair_prompt(prompt_text, source_map_reason)
			_emit_resume_generation_event(
				"generation_retry_requested",
				prompt_run_id,
				generation_path="direct",
				reason=source_map_reason,
			)
			repair_result: ArtifactResult = generate_artifact(repair_prompt_text, prompt_type)
			if not repair_result.ok:
				_emit_resume_generation_event(
					"generation_failed",
					prompt_run_id,
					generation_path="repair",
					error_code=repair_result.error_code or "generation_failed",
				)
				return PromptGenerationResponse(
					status="error",
					prompt_run_id=prompt_run_id,
					prompt_type=prompt_type,
					generation_path="repair",
					artifact=None,
					prompt_text=prompt_text,
					output_path=saved_path,
					error=PromptError(
						message=repair_result.error_message or "The content could not be generated right now. Please try again.",
						code=repair_result.error_code or "generation_failed",
					),
				)

			repair_ok, repair_reason = _validate_resume_source_map(repair_result.content or "")
			if not repair_ok:
				_emit_resume_generation_event(
					"generation_failed",
					prompt_run_id,
					generation_path="repair",
					reason=repair_reason,
				)
				return PromptGenerationResponse(
					status="error",
					prompt_run_id=prompt_run_id,
					prompt_type=prompt_type,
					generation_path="repair",
					artifact=None,
					prompt_text=prompt_text,
					output_path=saved_path,
					error=PromptError(
						message=f"Resume traceability validation failed: {repair_reason}",
						code="source_map_validation_failed",
					),
				)
			artifact_result = repair_result
			generation_path = "repair"
			_emit_resume_generation_event(
				"generation_repaired",
				prompt_run_id,
				generation_path="repair",
				reason=source_map_reason,
			)
		prose_mode = _resume_prose_validation_mode()
		if prose_mode != "off":
			prose_ok, prose_reason = _validate_resume_prose_claims(prompt_text, context_path, artifact_result.content or "")
			if not prose_ok:
				if prose_mode == "enforce":
					_emit_resume_generation_event(
						"generation_failed",
						prompt_run_id,
						generation_path=generation_path,
						reason=prose_reason,
					)
					return PromptGenerationResponse(
						status="error",
						prompt_run_id=prompt_run_id,
						prompt_type=prompt_type,
						generation_path=generation_path,
						artifact=None,
						prompt_text=prompt_text,
						output_path=saved_path,
						error=PromptError(
							message=f"Resume claim validation failed: {prose_reason}",
							code="resume_claim_validation_failed",
						),
					)
				_emit_resume_generation_event(
					"generation_warning",
					prompt_run_id,
					generation_path=generation_path,
					reason=f"resume_claim_validation_report_only: {prose_reason}",
				)
		content_ok, content_reason = _validate_resume_output_guardrails(artifact_result.content or "")
		if not content_ok:
			_emit_resume_generation_event(
				"generation_failed",
				prompt_run_id,
				generation_path=generation_path,
				reason=content_reason,
			)
			return PromptGenerationResponse(
				status="error",
				prompt_run_id=prompt_run_id,
				prompt_type=prompt_type,
				generation_path=generation_path,
				artifact=None,
				prompt_text=prompt_text,
				output_path=saved_path,
				error=PromptError(
					message=f"Resume output validation failed: {content_reason}",
					code="resume_content_validation_failed",
				),
			)
		else:
			_emit_resume_generation_event(
				"generation_complete",
				prompt_run_id,
				generation_path=generation_path,
			)
	else:
		_emit_resume_generation_event(
			"generation_complete",
			prompt_run_id,
			generation_path="direct",
		)

	# Save generated artifact alongside the prompt so post-generation checks have a target
	artifact_path: str | None = None
	if saved_path and artifact_result.content:
		try:
			artifact_path = saved_path.replace("_prompt_", "_artifact_")
			Path(artifact_path).write_text(artifact_result.content, encoding="utf-8")
		except Exception:
			artifact_path = None

	return PromptGenerationResponse(
		status="ok",
		prompt_run_id=prompt_run_id,
		prompt_type=prompt_type,
		generation_path=generation_path,
		artifact=PromptArtifact(type=prompt_type, content=artifact_result.content or ""),
		prompt_text=prompt_text,
		output_path=artifact_path or saved_path,
		error=None,
	)


@app.post("/api/prompts/resume", response_model=PromptGenerationResponse)
def create_resume_prompt(request: PromptRequest) -> PromptGenerationResponse:
	return _create_prompt("resume", request)


@app.post("/api/prompts/outreach", response_model=PromptGenerationResponse)
def create_outreach_prompt(request: PromptRequest) -> PromptGenerationResponse:
	return _create_prompt("outreach", request)


@app.post("/api/prompts/consulting", response_model=PromptGenerationResponse)
def create_consulting_prompt(request: PromptRequest) -> PromptGenerationResponse:
	return _create_prompt("consulting", request)


@app.post("/api/prompts/interview", response_model=PromptGenerationResponse)
def create_interview_prompt(request: PromptRequest) -> PromptGenerationResponse:
	return _create_prompt("interview", request)


@app.post("/api/prompts/weekly-review", response_model=PromptGenerationResponse)
def create_weekly_review_prompt(request: PromptRequest) -> PromptGenerationResponse:
	return _create_prompt("weekly_review", request)


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


