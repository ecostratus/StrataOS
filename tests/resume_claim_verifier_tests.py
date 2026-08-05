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


verifier = _load_module(
    "automation/resume-tailoring/scripts/verify_resume_claims.py",
    "verify_resume_claims",
)


def test_verify_claims_passes_when_skills_and_metrics_exist_in_source():
    source = """
    Skills: ServiceNow, AWS, CMDB
    Outcomes: improved response time by 45% and handled 750K+ annual interactions.
    """
    output = """
    ## Skills
    - ServiceNow, AWS, CMDB

    ## Professional Experience
    - Reduced incident response time by 45%.
    - Supported 750K+ annual interactions.
    """

    report = verifier.verify_claims(source, output)

    assert report["passed"] is True
    assert report["unsupported_skill_claims"] == []
    assert report["unsupported_metric_claims"] == []


def test_verify_claims_flags_unsupported_skill():
    source = "Skills: ServiceNow, AWS"
    output = """
    ## Skills
    - ServiceNow, Splunk ITSI
    """

    report = verifier.verify_claims(source, output)

    assert report["passed"] is False
    assert "Splunk ITSI" in report["unsupported_skill_claims"]


def test_verify_claims_flags_unsupported_metric():
    source = "Outcomes include 45% reduction in incidents."
    output = """
    ## Professional Experience
    - Reduced incident volume by 60%.
    """

    report = verifier.verify_claims(source, output)

    assert report["passed"] is False
    assert "60%" in report["unsupported_metric_claims"]


def test_extract_skill_tool_claims_from_skills_section():
    output = """
    ## Skills
    - ServiceNow, AWS, CMDB (advanced)
    - AIOps

    ## Education
    - Sample University
    """

    claims = verifier.extract_skill_tool_claims(output)

    assert "ServiceNow" in claims
    assert "AWS" in claims
    assert "CMDB" in claims
    assert "AIOps" in claims
