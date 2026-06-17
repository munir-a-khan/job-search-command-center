import pytest
from app.services import latex_render


@pytest.fixture()
def ctx(sample_profile_payload, fake_parsed_jd):
    profile = dict(sample_profile_payload)
    return {"profile": profile, "jd": fake_parsed_jd, "template_type": "private"}


def test_latex_escape_handles_specials():
    e = latex_render._latex_escape
    assert e("a & b") == r"a \& b"
    assert e("$10%") == r"\$10\%"
    assert "\\textbackslash" in e("a\\b")
    assert e(None) == ""


def test_render_private_template(ctx):
    out = latex_render.render_tex("private", ctx)
    assert "\\documentclass" in out
    assert "Jane Doe" in out
    assert "Acme Data" in out
    assert "FastAPI" in out  # from skills


def test_render_federal_template(ctx):
    out = latex_render.render_tex("federal", ctx)
    assert "FEDERAL SUMMARY" in out
    assert "Jane Doe" in out
    assert "Hours per week" in out


def test_render_state_template(ctx):
    out = latex_render.render_tex("state", ctx)
    assert "\\documentclass" in out
    assert "Jane Doe" in out


def test_render_rejects_unknown_template(ctx):
    with pytest.raises(ValueError):
        latex_render.render_tex("invalid", ctx)


def test_render_handles_empty_optional_sections(ctx):
    ctx2 = {**ctx, "profile": {
        "full_name": "Jane",
        "email": "j@x.com",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "summary": "",
        "education": [],
        "work_history": [],
        "projects": [],
        "skills": {},
        "certifications": [],
    }}
    out = latex_render.render_tex("private", ctx2)
    assert "Jane" in out
    # Sections with no data should be absent
    assert "EXPERIENCE" not in out
    assert "PROJECTS" not in out


def test_render_escapes_dangerous_input(ctx):
    ctx2 = {**ctx, "profile": {**ctx["profile"], "full_name": "Test & Co. $50%"}}
    out = latex_render.render_tex("private", ctx2)
    assert "Test \\& Co. \\$50\\%" in out
