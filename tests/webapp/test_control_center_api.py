from __future__ import annotations

import csv
import json
import os
import sqlite3
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


def _valid_resume_artifact() -> str:
    return """### 0. Policy Compliance Report
- Input validation status: pass

### 0.5. Source Map (required)
- [Professional Experience] - Led platform modernization roadmap. -> sourced from [base_resume_b: Company Alpha line 1]

### 1. Tailored Resume Content
- Led platform modernization roadmap.

### 2. Keyword Analysis
- platform modernization
""".strip()


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
                            "role_tags": ["engineer"],
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

    def fake_generate(prompt_text: str, kind: str):
        if kind == "resume":
            return generation.ArtifactResult(ok=True, content=_valid_resume_artifact())
        return generation.ArtifactResult(ok=True, content=f"Finished {kind} body")

    monkeypatch.setattr(app_module, "generate_artifact", fake_generate)

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
        assert resume_payload["generation_path"] == "direct"
        assert resume_payload["artifact"]["type"] == "resume"
        assert "### 0.5. Source Map" in resume_payload["artifact"]["content"]
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
        assert len(activity.json()) >= 1


def test_control_center_additional_prompt_types(monkeypatch, tmp_path: Path):
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
            ts = "20260720_220000"
            _write_csv(
                output_dir / f"jobs_discovered_{ts}.csv",
                [
                    {
                        "title": "Technical Program Manager",
                        "location": "Remote",
                        "company": "Acme",
                        "source": "sample",
                        "url": "https://example.com/job/2",
                        "posted_date": "2026-07-20",
                    }
                ],
            )
            _write_csv(
                output_dir / f"jobs_scored_{ts}.csv",
                [
                    {
                        "title": "Technical Program Manager",
                        "location": "Remote",
                        "company": "Acme",
                        "source": "sample",
                        "url": "https://example.com/job/2",
                        "posted_date": "2026-07-20",
                        "score": "0.73",
                        "bucket": "Strong",
                    }
                ],
            )
            (output_dir / f"jobs_enriched_{ts}.json").write_text(
                json.dumps(
                    [
                        {
                            "title": "Technical Program Manager",
                            "company": "Acme",
                            "location": "Remote",
                            "url": "https://example.com/job/2",
                            "role_tags": ["program management", "stakeholder alignment"],
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

        if "consulting_offer_v1.py" in command_text:
            return _make_fake_prompt_subprocess(output_dir / "consulting" / "consulting_prompt_test.txt")

        if "interview_prep_v1.py" in command_text:
            return _make_fake_prompt_subprocess(output_dir / "interview" / "interview_prompt_test.txt")

        if "weekly_review_v1.py" in command_text:
            return _make_fake_prompt_subprocess(output_dir / "review" / "weekly_review_prompt_test.txt")

        return CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    monkeypatch.setattr(app_module, "_run_subprocess", fake_run)

    monkeypatch.setattr(
        app_module,
        "generate_artifact",
        lambda prompt_text, kind: generation.ArtifactResult(ok=True, content=f"Finished {kind} body"),
    )

    with TestClient(app_module.app) as client:
        run = client.post("/api/runs/job-discovery")
        assert run.status_code == 200

        jobs = client.get("/api/jobs")
        assert jobs.status_code == 200
        payload = jobs.json()
        assert len(payload) == 1
        job_id = payload[0]["id"]

        consulting = client.post("/api/prompts/consulting", json={"no_sources": True})
        assert consulting.status_code == 200
        consulting_payload = consulting.json()
        assert consulting_payload["status"] == "ok"
        assert consulting_payload["artifact"]["type"] == "consulting"
        assert consulting_payload["artifact"]["content"] == "Finished consulting body"

        interview = client.post("/api/prompts/interview", json={"job_id": job_id, "no_sources": True})
        assert interview.status_code == 200
        interview_payload = interview.json()
        assert interview_payload["status"] == "ok"
        assert interview_payload["artifact"]["type"] == "interview"
        assert interview_payload["artifact"]["content"] == "Finished interview body"

        weekly_review = client.post("/api/prompts/weekly-review", json={"no_sources": True})
        assert weekly_review.status_code == 200
        weekly_payload = weekly_review.json()
        assert weekly_payload["status"] == "ok"
        assert weekly_payload["artifact"]["type"] == "weekly_review"
        assert weekly_payload["artifact"]["content"] == "Finished weekly_review body"


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

def test_resolve_resume_context_path_prefers_local_fixture(monkeypatch, tmp_path: Path):
    sample_context = tmp_path / "resume_context.sample.json"
    sample_context.write_text('{"base_resume_b": "placeholder"}', encoding="utf-8")
    local_context = tmp_path / "resume_context.local.json"
    local_context.write_text('{"base_resume_b": "real content"}', encoding="utf-8")

    monkeypatch.setattr(app_module, "DEFAULT_RESUME_CONTEXT", sample_context)
    monkeypatch.setattr(app_module, "LOCAL_RESUME_CONTEXT", local_context)
    monkeypatch.setattr(app_module.config, "get", lambda key, default=None: str(sample_context) if key == "RESUME_USER_CONTEXT_PATH" else default)

    resolved = app_module._resolve_resume_context_path()

    assert resolved == local_context


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
            (output_dir / f"jobs_enriched_{ts}.json").write_text(
                json.dumps(
                    [
                        {
                            "title": "Senior Platform Engineer",
                            "company": "Acme",
                            "location": "Remote",
                            "url": "https://example.com/job/1",
                            "role_tags": ["engineer"],
                        }
                    ]
                ),
                encoding="utf-8",
            )
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


def test_resume_prompt_input_validation_failure(monkeypatch, tmp_path: Path):
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
            (output_dir / f"jobs_enriched_{ts}.json").write_text(
                json.dumps(
                    [
                        {
                            "title": "Senior Platform Engineer",
                            "company": "Acme",
                            "location": "Remote",
                            "url": "https://example.com/job/1",
                            "role_tags": ["engineer"],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            (output_dir / f"jobs_discovered_{ts}.summary.json").write_text(json.dumps({"counts": {"total_discovered": 1, "exported": 1}}), encoding="utf-8")
            return CompletedProcess(command, 0, stdout="discovery complete\n", stderr="")

        if "resume_tailor_v1.py" in command_text:
            prompt_path = output_dir / "resume" / "resume_prompt_validation_failed.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(
                "INPUT VALIDATION FAILED\nMissing/placeholder inputs: Selected Base Resume, Ground-Truth Inventory\n",
                encoding="utf-8",
            )
            stdout = f"Saved: {prompt_path}\n"
            return CompletedProcess(command, 4, stdout=stdout, stderr="")

        return CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    generation_called = {"value": False}

    def fake_generate_artifact(prompt_text: str, kind: str):
        generation_called["value"] = True
        return generation.ArtifactResult(ok=True, content="Should not run")

    monkeypatch.setattr(app_module, "_run_subprocess", fake_run)
    monkeypatch.setattr(app_module, "generate_artifact", fake_generate_artifact)

    with TestClient(app_module.app) as client:
        assert client.post("/api/runs/job-discovery").status_code == 200
        job_id = client.get("/api/jobs").json()[0]["id"]
        resume = client.post("/api/prompts/resume", json={"job_id": job_id, "no_sources": True})
        assert resume.status_code == 200
        body = resume.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "input_validation_failed"
        assert "INPUT VALIDATION FAILED" in body["prompt_text"]
        assert generation_called["value"] is False


def test_resume_prompt_source_map_validation_failure(monkeypatch, tmp_path: Path):
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
            (output_dir / f"jobs_enriched_{ts}.json").write_text(
                json.dumps(
                    [
                        {
                            "title": "Senior Platform Engineer",
                            "company": "Acme",
                            "location": "Remote",
                            "url": "https://example.com/job/1",
                            "role_tags": ["engineer"],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            (output_dir / f"jobs_discovered_{ts}.summary.json").write_text(json.dumps({"counts": {"total_discovered": 1, "exported": 1}}), encoding="utf-8")
            return CompletedProcess(command, 0, stdout="discovery complete\n", stderr="")

        if "resume_tailor_v1.py" in command_text:
            return _make_fake_prompt_subprocess(output_dir / "resume" / "resume_prompt_test.txt")

        return CompletedProcess(command, 1, stdout="", stderr="unexpected command")

    def fake_generate_artifact(prompt_text: str, kind: str):
        return generation.ArtifactResult(
            ok=True,
            content="""
### 0. Policy Compliance Report
- Input validation status: pass

### 1. Tailored Resume Content
- Invented bullet without any source map coverage

### 2. Keyword Analysis
- placeholder
""".strip(),
        )

    monkeypatch.setattr(app_module, "_run_subprocess", fake_run)
    monkeypatch.setattr(app_module, "generate_artifact", fake_generate_artifact)

    with TestClient(app_module.app) as client:
        assert client.post("/api/runs/job-discovery").status_code == 200
        job_id = client.get("/api/jobs").json()[0]["id"]
        resume = client.post("/api/prompts/resume", json={"job_id": job_id, "no_sources": True})
        assert resume.status_code == 200
        body = resume.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "source_map_validation_failed"


def test_resume_prompt_retries_with_source_map_repair(monkeypatch):
    _set_success_config(monkeypatch)
    call_count = {"value": 0}

    def fake_generate_artifact(prompt_text: str, kind: str):
        call_count["value"] += 1
        if call_count["value"] == 1:
            return generation.ArtifactResult(
                ok=True,
                content="""
### 0. Policy Compliance Report
- Input validation status: pass

### 1. Tailored Resume Content
- Missing source map on first attempt

### 2. Keyword Analysis
- placeholder
""".strip(),
            )
        return generation.ArtifactResult(
            ok=True,
            content="""
### 0. Policy Compliance Report
- Input validation status: pass

### 0.5. Source Map (required)
- Tailored Resume Content bullet -> sourced from Resume B: Professional Summary

### 1. Tailored Resume Content
- Tailored Resume Content bullet

### 2. Keyword Analysis
- placeholder
""".strip(),
        )

    monkeypatch.setattr(app_module, "generate_artifact", fake_generate_artifact)

    with TestClient(app_module.app) as client:
        client.post("/api/runs/job-discovery")
        job_id = client.get("/api/jobs").json()[0]["id"]
        resume = client.post("/api/prompts/resume", json={"job_id": job_id, "no_sources": True})
        assert resume.status_code == 200
        body = resume.json()
        assert body["status"] == "ok"
        assert body["generation_path"] == "repair"
        assert body["artifact"]["type"] == "resume"
        assert call_count["value"] == 2


def test_resume_prompt_accepts_variant_source_map_heading(monkeypatch):
    _set_success_config(monkeypatch)

    def fake_generate_artifact(prompt_text: str, kind: str):
        return generation.ArtifactResult(
            ok=True,
            content="""
### 0 Policy Compliance Report
- Input validation status: pass

### 0.5 Source Map
- Professional Summary bullet -> sourced from Resume B: role/overview

### 1. Tailored Resume Content
- Professional Summary bullet

### 2. Keyword Analysis
- placeholder
""".strip(),
        )

    monkeypatch.setattr(app_module, "generate_artifact", fake_generate_artifact)

    with TestClient(app_module.app) as client:
        client.post("/api/runs/job-discovery")
        job_id = client.get("/api/jobs").json()[0]["id"]
        resume = client.post("/api/prompts/resume", json={"job_id": job_id, "no_sources": True})
        assert resume.status_code == 200
        body = resume.json()
        assert body["status"] == "ok"
        assert body["artifact"]["type"] == "resume"


def test_resume_prompt_rejects_ats_score_estimate(monkeypatch):
    _set_success_config(monkeypatch)

    def fake_generate_artifact(prompt_text: str, kind: str):
        return generation.ArtifactResult(
            ok=True,
            content="""
### 0. Policy Compliance Report
- Input validation status: pass

### 0.5. Source Map (required)
- Professional Summary bullet 1 -> sourced from Resume B: Professional Summary, "Technical program leader focused on platform reliability and service operations."

### 1. Tailored Resume Content
- Professional Summary bullet 1

### 2. Keyword Analysis
- placeholder

### 4. ATS Optimization Notes
- Match score estimate: 90% match to job description
""".strip(),
        )

    monkeypatch.setattr(app_module, "generate_artifact", fake_generate_artifact)

    with TestClient(app_module.app) as client:
        client.post("/api/runs/job-discovery")
        job_id = client.get("/api/jobs").json()[0]["id"]
        resume = client.post("/api/prompts/resume", json={"job_id": job_id, "no_sources": True})
        assert resume.status_code == 200
        body = resume.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "resume_content_validation_failed"


def test_resume_prompt_prose_violation_report_mode_allows_output(monkeypatch):
    _set_success_config(monkeypatch)

    def fake_generate_artifact(prompt_text: str, kind: str):
        return generation.ArtifactResult(
            ok=True,
            content="""
### 0. Policy Compliance Report
- Input validation status: pass

### 0.5. Source Map (required)
- Professional Experience bullet 1 -> sourced from Resume B: Company Alpha / Bullet 1
- Professional Experience bullet 2 -> sourced from Resume B: Company Alpha / Bullet 3

### 1. Tailored Resume Content
- Led platform modernization roadmap across infrastructure and operations teams.
- Coordinated cross-functional technical programs.

### 2. Keyword Analysis
- placeholder
""".strip(),
        )

    monkeypatch.setattr(app_module, "generate_artifact", fake_generate_artifact)

    with TestClient(app_module.app) as client:
        client.post("/api/runs/job-discovery")
        job_id = client.get("/api/jobs").json()[0]["id"]
        resume = client.post("/api/prompts/resume", json={"job_id": job_id, "no_sources": True})
        assert resume.status_code == 200
        body = resume.json()
        assert body["status"] == "ok"
        assert body["artifact"]["type"] == "resume"


def test_init_db_adds_phase1_search_columns_and_indexes(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "jobs.db"
    monkeypatch.setattr(app_module, "DB_PATH", db_path)

    app_module.init_db()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cols = {str(r["name"]) for r in conn.execute("PRAGMA table_info(jobs)").fetchall()}
        expected_cols = {
            "country_code",
            "state_region",
            "city",
            "salary_min",
            "salary_max",
            "salary_currency",
            "job_type",
            "work_type",
            "company_normalized",
            "title_normalized",
            "posted_at_utc",
            "search_document",
        }
        assert expected_cols.issubset(cols)

        idx_rows = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='jobs'").fetchall()
        idx = {str(r["name"]) for r in idx_rows}
        expected_idx = {
            "idx_jobs_posted_at_utc",
            "idx_jobs_location",
            "idx_jobs_job_type_work_type",
            "idx_jobs_company_normalized",
            "idx_jobs_title_normalized",
        }
        assert expected_idx.issubset(idx)
    finally:
        conn.close()


def test_replace_jobs_populates_phase1_normalized_fields(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "jobs.db"
    monkeypatch.setattr(app_module, "DB_PATH", db_path)
    app_module.init_db()

    jobs = [
        {
            "title": "Senior Technical Program Manager",
            "company": "Acme",
            "location": "Austin, TX, US",
            "source": "sample",
            "url": "https://example.com/jobs/1",
            "posted_date": "2026-07-20",
            "score": 0.91,
            "bucket": "Exceptional",
            "raw_json": {
                "salary_min": 185000,
                "salary_max": 220000,
                "salary_currency": "USD",
                "job_type": "full-time",
                "work_type": "hybrid",
                "description": "TPM role leading platform initiatives",
            },
        }
    ]

    inserted = app_module._replace_jobs_for_run(101, jobs)
    assert inserted == 1

    conn = app_module.connect_db()
    try:
        row = conn.execute(
            """
            SELECT country_code, state_region, city, salary_min, salary_max, salary_currency,
                   job_type, work_type, company_normalized, title_normalized, posted_at_utc,
                   search_document
            FROM jobs
            WHERE run_id = 101
            LIMIT 1
            """
        ).fetchone()
        assert row is not None
        payload = dict(row)
        assert payload["country_code"] == "US"
        assert payload["state_region"] == "TX"
        assert payload["city"] == "Austin"
        assert payload["salary_min"] == 185000
        assert payload["salary_max"] == 220000
        assert payload["salary_currency"] == "USD"
        assert payload["job_type"] == "full-time"
        assert payload["work_type"] == "hybrid"
        assert payload["company_normalized"] == "acme"
        assert payload["title_normalized"] == "senior technical program manager"
        assert str(payload["posted_at_utc"]).startswith("2026-07-20")
        assert "TPM role leading platform initiatives" in str(payload["search_document"])
    finally:
        conn.close()


def test_list_jobs_applies_default_relevance_filters(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "jobs.db"
    monkeypatch.setattr(app_module, "DB_PATH", db_path)
    app_module.init_db()

    jobs = [
        {
            "title": "Custodian",
            "company": "Facilities Co",
            "location": "Remote",
            "source": "sample",
            "url": "https://example.com/jobs/custodian",
            "posted_date": "2026-07-20",
            "score": 0.2,
            "bucket": "Weak",
            "raw_json": {"role_tags": []},
        },
        {
            "title": "Software Engineer",
            "company": "Tech Co",
            "location": "Remote",
            "source": "sample",
            "url": "https://example.com/jobs/eng",
            "posted_date": "2026-07-20",
            "score": 0.82,
            "bucket": "Strong",
            "raw_json": {"role_tags": ["engineer"]},
        },
    ]
    inserted = app_module._replace_jobs_for_run(201, jobs)
    assert inserted == 2

    with TestClient(app_module.app) as client:
        response = client.get("/api/jobs?run_id=201")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 1
        assert payload[0]["title"] == "Software Engineer"


def test_list_jobs_can_include_low_relevance_when_requested(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "jobs.db"
    monkeypatch.setattr(app_module, "DB_PATH", db_path)
    app_module.init_db()

    jobs = [
        {
            "title": "Custodian",
            "company": "Facilities Co",
            "location": "Remote",
            "source": "sample",
            "url": "https://example.com/jobs/custodian",
            "posted_date": "2026-07-20",
            "score": 0.2,
            "bucket": "Weak",
            "raw_json": {"role_tags": []},
        },
        {
            "title": "Software Engineer",
            "company": "Tech Co",
            "location": "Remote",
            "source": "sample",
            "url": "https://example.com/jobs/eng",
            "posted_date": "2026-07-20",
            "score": 0.82,
            "bucket": "Strong",
            "raw_json": {"role_tags": ["engineer"]},
        },
    ]
    inserted = app_module._replace_jobs_for_run(202, jobs)
    assert inserted == 2

    with TestClient(app_module.app) as client:
        response = client.get("/api/jobs?run_id=202&include_low_relevance=true")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 2


def test_search_jobs_applies_default_relevance_filters(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "jobs.db"
    monkeypatch.setattr(app_module, "DB_PATH", db_path)
    app_module.init_db()

    jobs = [
        {
            "title": "Custodian",
            "company": "Facilities Co",
            "location": "Remote",
            "source": "sample",
            "url": "https://example.com/jobs/custodian",
            "posted_date": "2026-07-20",
            "score": 0.2,
            "bucket": "Weak",
            "raw_json": {"role_tags": []},
        },
        {
            "title": "Platform Engineer",
            "company": "Tech Co",
            "location": "Remote",
            "source": "sample",
            "url": "https://example.com/jobs/platform",
            "posted_date": "2026-07-20",
            "score": 0.9,
            "bucket": "Exceptional",
            "raw_json": {"role_tags": ["engineer"]},
        },
    ]
    inserted = app_module._replace_jobs_for_run(203, jobs)
    assert inserted == 2

    with TestClient(app_module.app) as client:
        response = client.post("/api/jobs/search", json={"query": ""})
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        assert len(payload["items"]) == 1
        assert payload["items"][0]["title"] == "Platform Engineer"


def test_search_jobs_can_include_low_relevance_when_requested(monkeypatch, tmp_path: Path):
    db_path = tmp_path / "jobs.db"
    monkeypatch.setattr(app_module, "DB_PATH", db_path)
    app_module.init_db()

    jobs = [
        {
            "title": "Custodian",
            "company": "Facilities Co",
            "location": "Remote",
            "source": "sample",
            "url": "https://example.com/jobs/custodian",
            "posted_date": "2026-07-20",
            "score": 0.2,
            "bucket": "Weak",
            "raw_json": {"role_tags": []},
        },
        {
            "title": "Platform Engineer",
            "company": "Tech Co",
            "location": "Remote",
            "source": "sample",
            "url": "https://example.com/jobs/platform",
            "posted_date": "2026-07-20",
            "score": 0.9,
            "bucket": "Exceptional",
            "raw_json": {"role_tags": ["engineer"]},
        },
    ]
    inserted = app_module._replace_jobs_for_run(204, jobs)
    assert inserted == 2

    with TestClient(app_module.app) as client:
        response = client.post(
            "/api/jobs/search",
            json={"query": "", "include_low_relevance": True},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 2
