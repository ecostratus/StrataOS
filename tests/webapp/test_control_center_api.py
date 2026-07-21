from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path
from subprocess import CompletedProcess

from fastapi.testclient import TestClient

from webapp.backend import app as app_module


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def test_control_center_api_smoke(monkeypatch, tmp_path: Path):
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    db_path = tmp_path / "jobs.db"
    log_path = tmp_path / "events.jsonl"
    log_path.write_text('{"ts":"2026-07-20T00:00:00Z","category":"test","event":"seed"}\n', encoding="utf-8")

    monkeypatch.setattr(app_module, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(app_module, "DB_PATH", db_path)
    monkeypatch.setattr(app_module, "LOG_PATH", log_path)

    def fake_run(command: list[str]):
        command_text = " ".join(command)
        if "job_discovery_v1.py" in command_text:
            ts = "20260720_210000"
            _write_csv(
                output_dir / f"jobs_discovered_{ts}.csv",
                [
                    {
                        "title": "Senior Platform Engineer",
                        "location": "Remote",
                        "company": "Acme",
                        "source": "sample",
                        "url": "https://example.com/job/1",
                        "posted_date": "2026-07-20",
                    }
                ],
            )
            _write_csv(
                output_dir / f"jobs_scored_{ts}.csv",
                [
                    {
                        "title": "Senior Platform Engineer",
                        "location": "Remote",
                        "company": "Acme",
                        "source": "sample",
                        "url": "https://example.com/job/1",
                        "posted_date": "2026-07-20",
                        "score": "0.85",
                        "bucket": "Exceptional",
                    }
                ],
            )
            (output_dir / f"jobs_enriched_{ts}.json").write_text(
                json.dumps(
                    [
                        {
                            "title": "Senior Platform Engineer",
                            "company": "Acme",
                            "location": "Remote",
                            "url": "https://example.com/job/1",
                            "skills": ["Python", "Kubernetes"],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            (output_dir / f"jobs_discovered_{ts}.summary.json").write_text(
                json.dumps({"counts": {"total_discovered": 1, "exported": 1}}),
                encoding="utf-8",
            )
            return CompletedProcess(command, 0, stdout="discovery complete\n", stderr="")

        if "resume_tailor_v1.py" in command_text or "outreach_generator_v1.py" in command_text:
            if "resume_tailor_v1.py" in command_text:
                prompt_path = output_dir / "resume" / "resume_prompt_test.txt"
            else:
                prompt_path = output_dir / "outreach" / "outreach_prompt_test.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text("Prompt body", encoding="utf-8")
            return CompletedProcess(command, 0, stdout=f"Saved: {prompt_path}\n", stderr="")

        return CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    monkeypatch.setattr(app_module, "_run_subprocess", fake_run)

    with TestClient(app_module.app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200

        run = client.post("/api/runs/job-discovery")
        assert run.status_code == 200
        assert run.json()["mirrored_jobs"] == 1

        jobs = client.get("/api/jobs")
        assert jobs.status_code == 200
        payload = jobs.json()
        assert len(payload) == 1
        assert payload[0]["bucket"] == "Exceptional"

        job_id = payload[0]["id"]

        resume = client.post("/api/prompts/resume", json={"job_id": job_id, "no_sources": True})
        assert resume.status_code == 200
        assert "Prompt body" in resume.json()["prompt_text"]

        outreach = client.post("/api/prompts/outreach", json={"job_id": job_id, "no_sources": True})
        assert outreach.status_code == 200
        assert "Prompt body" in outreach.json()["prompt_text"]

        activity = client.get("/api/activity?limit=5")
        assert activity.status_code == 200
        assert len(activity.json()) == 1
