from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path
from subprocess import CompletedProcess

from fastapi.testclient import TestClient

from webapp.backend import app as app_module
from webapp.backend import generation


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _make_fake_prompt_subprocess(prompt_path: Path, prompt_text: str = "Prompt body", returncode: int = 0, stdout_suffix: str = ""):
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    if returncode == 0:
        prompt_path.write_text(prompt_text, encoding="utf-8")
    stdout = f"Saved: {prompt_path}\n{stdout_suffix}".strip() if returncode == 0 else stdout_suffix or "prompt step failed\n"
    stderr = "" if returncode == 0 else "raw stderr should not leak"
    return CompletedProcess(["python"], returncode, stdout=stdout if stdout.endswith("\n") else f"{stdout}\n", stderr=stderr)


def _set_success_config(monkeypatch):
    monkeypatch.setattr(generation.config, "get", lambda key, default=None: {
        "AI_PROVIDER": "openai",
        "OPENAI_API_KEY": "real-key",
        "OPENAI_MODEL": "gpt-4",
        "OPENAI_TEMPERATURE": "0.2",
        "OPENAI_MAX_TOKENS": "256",
    }.get(key, default))


class _FakeCompletionResponse:
    def __init__(self, content: str):
        self.choices = [type("Choice", (), {"message": type("Message", (), {"content": content})()})()]


class _FakeOpenAIClient:
    def __init__(self, response: _FakeCompletionResponse | None = None, exc: Exception | None = None):
        self._response = response or _FakeCompletionResponse("Finished artifact")
        self._exc = exc
        self.chat = type("Chat", (), {"completions": type("Completions", (), {"create": self._create})()})()

    def _create(self, *args, **kwargs):
        if self._exc is not None:
            raise self._exc
        return self._response


class _FakeAuthError(Exception):
    pass


def test_control_center_api_smoke(monkeypatch, tmp_path: Path):
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    db_path = tmp_path / "jobs.db"
    log_path = tmp_path / "events.jsonl"
    log_path.write_text('{"ts":"2026-07-20T00:00:00Z","category":"test","event":"seed"}\n', encoding="utf-8")

    monkeypatch.setattr(app_module, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(app_module, "DB_PATH", db_path)
    monkeypatch.setattr(app_module, "LOG_PATH", log_path)
    _set_success_config(monkeypatch)

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

        if "resume_tailor_v1.py" in command_text:
            return _make_fake_prompt_subprocess(output_dir / "resume" / "resume_prompt_test.txt")

        if "outreach_generator_v1.py" in command_text:
            return _make_fake_prompt_subprocess(output_dir / "outreach" / "outreach_prompt_test.txt")

        return CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    monkeypatch.setattr(app_module, "_run_subprocess", fake_run)
    monkeypatch.setattr(app_module, "generate_artifact", lambda prompt_text, kind: generation.ArtifactResult(ok=True, content=f"Finished {kind} body"))

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
        resume_payload = resume.json()
        assert resume_payload["status"] == "ok"
        assert resume_payload["artifact"]["type"] == "resume"
        assert resume_payload["artifact"]["content"] == "Finished resume body"
        assert "Prompt body" in resume_payload["prompt_text"]

        outreach = client.post("/api/prompts/outreach", json={"job_id": job_id, "no_sources": True})
        assert outreach.status_code == 200
        outreach_payload = outreach.json()
        assert outreach_payload["status"] == "ok"
        assert outreach_payload["artifact"]["type"] == "outreach"
        assert outreach_payload["artifact"]["content"] == "Finished outreach body"
        assert "Prompt body" in outreach_payload["prompt_text"]

        activity = client.get("/api/activity?limit=5")
        assert activity.status_code == 200
        assert len(activity.json()) == 1


def test_generate_artifact_success(monkeypatch):
    _set_success_config(monkeypatch)
    monkeypatch.setattr(generation, "_build_client", lambda api_key: _FakeOpenAIClient(_FakeCompletionResponse("Finished resume")))

    result = generation.generate_artifact("Prompt body", "resume")

    assert result.ok is True
    assert result.content == "Finished resume"
    assert result.error_message is None
    assert result.error_code is None


def test_generate_artifact_failure_returns_clean_error(monkeypatch):
    _set_success_config(monkeypatch)
    failure_client = _FakeOpenAIClient(exc=_FakeAuthError("invalid key: secret"))
    monkeypatch.setattr(generation, "_build_client", lambda api_key: failure_client)

    result = generation.generate_artifact("Prompt body", "outreach")

    assert result.ok is False
    assert result.content is None
    assert result.error_code == "authentication_error"
    assert result.error_message is not None
    assert "invalid key" not in result.error_message.lower()


def test_generate_artifact_missing_configuration(monkeypatch):
    monkeypatch.setattr(generation.config, "get", lambda key, default=None: {
        "AI_PROVIDER": "openai",
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY_HERE",
        "OPENAI_MODEL": "gpt-4",
        "OPENAI_TEMPERATURE": "0.2",
        "OPENAI_MAX_TOKENS": "256",
    }.get(key, default))
    monkeypatch.setattr(
        generation.config,
        "get_json",
        lambda path, default=None: "YOUR_OPENAI_API_KEY_HERE" if path == "ai_services.openai.api_key" else default,
    )
    called = {"value": False}

    def fail_if_called(api_key: str):
        called["value"] = True
        raise AssertionError("network should not be called when config is missing")

    monkeypatch.setattr(generation, "_build_client", fail_if_called)

    result = generation.generate_artifact("Prompt body", "resume")

    assert result.ok is False
    assert result.error_code == "missing_configuration"
    assert called["value"] is False


def test_resume_prompt_failure_is_sanitized(monkeypatch, tmp_path: Path):
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_path / "jobs.db"
    log_path = tmp_path / "events.jsonl"
    log_path.write_text('', encoding="utf-8")

    monkeypatch.setattr(app_module, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(app_module, "DB_PATH", db_path)
    monkeypatch.setattr(app_module, "LOG_PATH", log_path)
    _set_success_config(monkeypatch)

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
                    },
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
                    },
                ],
            )
            (output_dir / f"jobs_enriched_{ts}.json").write_text(json.dumps([{"title": "Senior Platform Engineer", "company": "Acme", "location": "Remote", "url": "https://example.com/job/1"}]), encoding="utf-8")
            (output_dir / f"jobs_discovered_{ts}.summary.json").write_text(json.dumps({"counts": {"total_discovered": 1, "exported": 1}}), encoding="utf-8")
            return CompletedProcess(command, 0, stdout="discovery complete\n", stderr="")

        if "resume_tailor_v1.py" in command_text:
            return CompletedProcess(command, 1, stdout="raw stdout leak\n", stderr="raw stderr leak")

        return CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    monkeypatch.setattr(app_module, "_run_subprocess", fake_run)
    monkeypatch.setattr(app_module, "generate_artifact", lambda prompt_text, kind: generation.ArtifactResult(ok=True, content=f"Finished {kind} body"))

    with TestClient(app_module.app) as client:
        assert client.post("/api/runs/job-discovery").status_code == 200
        job_id = client.get("/api/jobs").json()[0]["id"]
        resume = client.post("/api/prompts/resume", json={"job_id": job_id, "no_sources": True})
        assert resume.status_code == 200
        body = resume.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "prompt_build_failed"
        assert "raw stdout leak" not in json.dumps(body)
        assert "raw stderr leak" not in json.dumps(body)
