from __future__ import annotations

from automation.common.import_helpers import load_module_from_path


def test_dynamic_import_interview_prep_module():
    mod = load_module_from_path(
        "automation/interview-prep/scripts/interview_prep_v1.py",
        "interview_prep_v1",
    )
    assert hasattr(mod, "main")
