import importlib.util
import pathlib


_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_module(rel_path: str, module_name: str):
    path = _ROOT / rel_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


resume_tailor = _load_module(
    "automation/resume-tailoring/scripts/resume_tailor_v1.py",
    "resume_tailor_v1",
)
verify_output = _load_module(
    "automation/resume-tailoring/scripts/verify_resume_output.py",
    "verify_resume_output",
)


def test_context_normalization_maps_nested_track_payload():
    raw_ctx = {
        "candidate": "James Naphen",
        "tracks": {
            "A": {"resume_text": "Resume A body"},
            "B": {"resume_text": "Resume B body"},
            "C": {"resume_text": "Resume C body"},
        },
        "linkedin_history": {"note": "LinkedIn long-form history"},
    }

    normalized = resume_tailor._normalize_user_context(raw_ctx)

    assert normalized["base_resume_a"] == "Resume A body"
    assert normalized["base_resume_b"] == "Resume B body"
    assert normalized["base_resume_c"] == "Resume C body"
    assert normalized["linkedin_profile"] == "LinkedIn long-form history"


def test_context_normalization_does_not_override_existing_flat_fields():
    raw_ctx = {
        "base_resume_b": "Existing Resume B",
        "tracks": {
            "B": {"resume_text": "Nested Resume B"},
        },
    }

    normalized = resume_tailor._normalize_user_context(raw_ctx)

    assert normalized["base_resume_b"] == "Existing Resume B"


def test_context_normalization_skips_placeholder_linkedin_note():
    raw_ctx = {
        "linkedin_history": {
            "note": "Full text pulled from PDF earlier in this conversation; not repeated here."
        }
    }

    normalized = resume_tailor._normalize_user_context(raw_ctx)

    assert "linkedin_profile" not in normalized


def test_input_validation_fails_when_sources_are_placeholders():
    context = {
        "selected_base_resume": "[Paste Resume B - Platform Stabilization content here]",
        "job_description": "Real JD content",
    }
    user_ctx = {
        "base_resume_a": "[Paste Resume A - Risk & AI Governance content here]",
        "base_resume_b": "[Paste Resume B - Platform Stabilization content here]",
        "base_resume_c": "[Paste Resume C - AI Product/CPO Conversion content here]",
        "linkedin_profile": "[Paste full LinkedIn history here]",
        "operator_brief_a": "[Paste Track A operator brief here]",
        "operator_brief_b": "[Paste Track B operator brief here]",
        "operator_brief_c": "[Paste Track C operator brief here]",
        "master_resume": "[Paste legacy master resume content here]",
    }

    result = resume_tailor._validate_resume_inputs(context, user_ctx)

    assert result["status"] == "fail"
    assert result["reason"] == "missing_sources"
    assert "Selected Base Resume" in result["missing_fields"]
    assert "Ground-Truth Inventory" in result["missing_fields"]
    assert "INPUT VALIDATION FAILED" in result["message"]


def test_input_validation_fails_when_jd_is_placeholder_even_with_sources():
    context = {
        "selected_base_resume": "Real base resume content",
        "job_description": "[Paste JD text here]",
    }
    user_ctx = {
        "base_resume_b": "Real base resume content",
        "linkedin_profile": "Real LinkedIn history",
    }

    result = resume_tailor._validate_resume_inputs(context, user_ctx)

    assert result["status"] == "fail"
    assert result["reason"] == "missing_jd"
    assert "Target Job Description" in result["missing_fields"]
    assert "Missing Target Job Description content" in result["message"]


def test_gap_line_format_accepts_canonical_policy_line():
    text = "GAP: JD requires [Splunk ITSI]. Not found in source materials. Resume generated without this claim."
    assert verify_output.find_non_canonical_gap_lines(text) == []


def test_gap_line_format_rejects_non_canonical_line():
    text = "GAP: JD asks for Splunk ITSI but missing in source."
    violations = verify_output.find_non_canonical_gap_lines(text)
    assert len(violations) == 1


def test_load_source_text_supports_nested_tracks_payload(tmp_path):
    context_path = tmp_path / "context.json"
    context_path.write_text(
        """
{
  "tracks": {
    "A": {"resume_text": "Resume A evidence"},
    "B": {"resume_text": "Resume B evidence"}
  },
  "linkedin_history": {"note": "LinkedIn evidence"}
}
""".strip(),
        encoding="utf-8",
    )

    source_text = verify_output.load_source_text(str(context_path))

    assert "Resume A evidence" in source_text
    assert "Resume B evidence" in source_text
    assert "LinkedIn evidence" in source_text


def test_load_source_text_skips_placeholder_linkedin_note(tmp_path):
        context_path = tmp_path / "context_with_placeholder_note.json"
        context_path.write_text(
                """
{
    "tracks": {
        "A": {"resume_text": "Resume A evidence"}
    },
    "linkedin_history": {
        "note": "Full text pulled from PDF earlier in this conversation; not repeated here."
    }
}
""".strip(),
                encoding="utf-8",
        )

        source_text = verify_output.load_source_text(str(context_path))

        assert "Resume A evidence" in source_text
        assert "not repeated here" not in source_text
