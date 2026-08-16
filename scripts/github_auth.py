#!/usr/bin/env python3
"""Shared GitHub authentication helpers for repository automation."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_API_URL = "https://api.github.com"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "env.json"


class GitHubAuthError(RuntimeError):
    """Raised when GitHub automation is requested without valid auth."""


def _load_config_token(config_path: Path = CONFIG_PATH) -> str | None:
    if not config_path.exists():
        return None
    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    token = config.get("github", {}).get("token", "").strip()
    return token or None


def resolve_github_token() -> tuple[str | None, str | None]:
    """Resolve a token and identify the source used."""
    env_token = os.environ.get("GH_TOKEN")
    if env_token:
        return env_token, "GH_TOKEN"

    env_token = os.environ.get("GITHUB_TOKEN")
    if env_token:
        return env_token, "GITHUB_TOKEN"

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        result = None

    if result and result.returncode == 0:
        token = result.stdout.strip()
        if token:
            return token, "gh auth token"

    config_token = _load_config_token()
    if config_token:
        return config_token, "config/env.json github.token"

    return None, None


def get_github_token() -> str | None:
    token, _source = resolve_github_token()
    return token


def check_github_auth() -> bool:
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    return result.returncode == 0


def require_github_token(purpose: str = "GitHub automation") -> tuple[str, str]:
    token, source = resolve_github_token()
    if token and source:
        return token, source
    raise GitHubAuthError(
        f"{purpose} requires GitHub authentication. "
        "Set GH_TOKEN or GITHUB_TOKEN, run `gh auth login`, "
        "or add github.token to config/env.json."
    )


def make_github_api_request(
    endpoint: str,
    token: str | None = None,
    *,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    api_url: str = DEFAULT_API_URL,
) -> dict[str, Any]:
    """Make a GitHub API request and return parsed JSON."""
    url = endpoint if endpoint.startswith("http") else f"{api_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "StrataOS-GitHub-Automation",
    }
    payload = None
    if token:
        headers["Authorization"] = "Bearer " + token
    if data is not None:
        headers["Content-Type"] = "application/json"
        payload = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method=method.upper())
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode())


def format_http_error(error: urllib.error.HTTPError) -> str:
    """Return a readable GitHub API error message."""
    message = f"{error.code} {error.reason}"
    try:
        payload = json.loads(error.read().decode())
    except (json.JSONDecodeError, OSError):
        return message
    detail = payload.get("message")
    if detail:
        return f"{message}: {detail}"
    return message
