"""
Regression checks for job discovery track precedence.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "automation" / "job-discovery" / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import job_discovery_v1 as orchestrator  # type: ignore

_FIXTURE_DIR = _REPO_ROOT / "tests" / "fixtures" / "job_discovery"


def _load_fixture(name: str) -> list[dict[str, object]]:
    return json.loads((_FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _load_profile_tracks() -> list[dict[str, object]]:
    config_path = _REPO_ROOT / "config" / "env.json"
    config_data = json.loads(config_path.read_text(encoding="utf-8"))
    filters_cfg = config_data["job_discovery"]["filters"]
    profile_tracks, _ = orchestrator._build_profile_tracks(filters_cfg)
    return profile_tracks


def _assert_fixture(name: str) -> None:
    profile_tracks = _load_profile_tracks()
    for row in _load_fixture(name):
        selected_track, _, selected_label = orchestrator._select_profile_track(
            str(row["title"]),
            str(row.get("search_text") or row["title"]),
            profile_tracks,
        )
        assert selected_track is not None, f"No track selected for {row['title']}"
        assert selected_label == row["expected_profile_track"], (
            f"{row['title']} => {selected_label!r}, expected {row['expected_profile_track']!r}"
        )


def test_track_b_precedence_fixture() -> None:
    _assert_fixture("track_b_precedence_fixture.json")


def test_track_ac_boundary_fixture() -> None:
    _assert_fixture("track_ac_boundary_fixture.json")
