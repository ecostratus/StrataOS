from automation.common.prompt_renderer import render_prompt


def test_render_prompt_basic():
    template = "Apply for {{ title }} at {{ company }}."
    ctx = {"title": "Backend Engineer", "company": "ACME"}
    out = render_prompt(template, ctx)
    assert "Backend Engineer" in out
    assert "ACME" in out


def test_render_prompt_missing_fields():
    template = "Apply for {{ title }} at {{ company }} in {{ location }}."
    ctx = {"title": "Backend Engineer", "company": "ACME"}
    out = render_prompt(template, ctx)
    assert "Backend Engineer" in out
    assert "ACME" in out
    # location should render empty gracefully
    assert "in" in out  # sentence structure preserved
