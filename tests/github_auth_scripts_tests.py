import importlib.util
import pathlib
import sys


_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SCRIPTS_DIR = _ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


def _load_module(rel_path: str, module_name: str):
    path = _ROOT / rel_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


github_auth = _load_module("scripts/github_auth.py", "github_auth")
issue_creator = _load_module("scripts/create_github_issue.py", "create_github_issue")


def test_resolve_github_token_prefers_gh_token(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "gh-token")
    monkeypatch.setenv("GITHUB_TOKEN", "github-token")

    token, source = github_auth.resolve_github_token()

    assert token == "gh-token"
    assert source == "GH_TOKEN"


def test_require_github_token_has_clear_error(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(github_auth, "_load_config_token", lambda: None)

    class DummyResult:
        returncode = 1
        stdout = ""

    monkeypatch.setattr(github_auth.subprocess, "run", lambda *args, **kwargs: DummyResult())

    try:
        github_auth.require_github_token("GitHub issue creation")
    except github_auth.GitHubAuthError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected GitHubAuthError")

    assert "GH_TOKEN" in message
    assert "gh auth login" in message


def test_create_issue_dry_run_uses_env_token(monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_TOKEN", "token-from-env")

    exit_code = issue_creator.main(
        [
            "--repo",
            "ecostratus/StrataOS",
            "--title",
            "Hygiene follow-up",
            "--body",
            "Triaged from audit",
            "--label",
            "triage",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert '"auth_source": "GITHUB_TOKEN"' in output
    assert '"labels": [' in output


def test_create_issue_posts_expected_payload(monkeypatch, capsys):
    monkeypatch.setenv("GH_TOKEN", "token-from-env")
    calls = {}

    def _fake_request(endpoint, token, *, method="GET", data=None, api_url=github_auth.DEFAULT_API_URL):
        calls["endpoint"] = endpoint
        calls["token"] = token
        calls["method"] = method
        calls["data"] = data
        calls["api_url"] = api_url
        return {"number": 42, "html_url": "https://github.com/ecostratus/StrataOS/issues/42"}

    monkeypatch.setattr(issue_creator.github_auth, "make_github_api_request", _fake_request)

    exit_code = issue_creator.main(
        [
            "--repo",
            "ecostratus/StrataOS",
            "--title",
            "Hygiene follow-up",
            "--body",
            "Triaged from audit",
        ]
    )

    assert exit_code == 0
    assert calls == {
        "endpoint": "repos/ecostratus/StrataOS/issues",
        "token": "token-from-env",
        "method": "POST",
        "data": {"title": "Hygiene follow-up", "body": "Triaged from audit"},
        "api_url": github_auth.DEFAULT_API_URL,
    }
    assert "Created issue #42" in capsys.readouterr().out
