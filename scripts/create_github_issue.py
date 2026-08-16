#!/usr/bin/env python3
"""Create a GitHub issue using env/config tokens or saved gh auth."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
from pathlib import Path

import github_auth


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Repository in owner/name format")
    parser.add_argument("--title", required=True, help="Issue title")
    body_group = parser.add_mutually_exclusive_group(required=True)
    body_group.add_argument("--body", help="Issue body text")
    body_group.add_argument("--body-file", help="Path to a markdown body file")
    parser.add_argument("--label", action="append", default=[], help="Issue label (repeatable)")
    parser.add_argument("--dry-run", action="store_true", help="Print the request instead of creating the issue")
    return parser.parse_args(argv)


def load_body(body: str | None, body_file: str | None) -> str:
    if body is not None:
        return body
    if body_file is None:
        raise ValueError("Issue body is required")
    return Path(body_file).read_text(encoding="utf-8")


def validate_repo(repo: str) -> str:
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("--repo must be in owner/name format")
    return repo


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": args.title,
        "body": load_body(args.body, args.body_file),
    }
    if args.label:
        payload["labels"] = args.label
    return payload


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        repo = validate_repo(args.repo)
        payload = build_payload(args)
        token, source = github_auth.require_github_token("GitHub issue creation")
    except (ValueError, github_auth.GitHubAuthError) as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.dry_run:
        print(json.dumps({"repo": repo, "auth_source": source, "payload": payload}, indent=2))
        return 0

    try:
        issue = github_auth.make_github_api_request(
            f"repos/{repo}/issues",
            token,
            method="POST",
            data=payload,
        )
    except urllib.error.HTTPError as exc:
        print(f"GitHub API request failed: {github_auth.format_http_error(exc)}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Failed to create issue: {exc}", file=sys.stderr)
        return 1

    print(f"Created issue #{issue['number']}: {issue['html_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
