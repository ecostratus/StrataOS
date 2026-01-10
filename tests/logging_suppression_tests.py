import io
import logging
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(ROOT, "automation", "job-discovery", "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from logging_utils import (
    set_jsonl_sink,
    set_suppress_stdout_if_jsonl,
    structured_log,
)


def test_stdout_suppression_when_jsonl_enabled(tmp_path, capsys):
    # Configure logger to use root logger
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)
    # Enable JSONL sink and suppress stdout
    sink_path = tmp_path / "run.jsonl"
    set_jsonl_sink(str(sink_path))
    set_suppress_stdout_if_jsonl(True)

    structured_log(logger, "info", "suppress_test", foo="bar")
    out = capsys.readouterr().out
    # Expect no stdout since suppression is on
    assert out == ""

    # JSONL should contain the line
    with open(sink_path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]
    assert lines and "\"event\":\"suppress_test\"" in lines[-1]
