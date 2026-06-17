from unittest.mock import patch
from app.services import resume_tailor


@patch("app.services.resume_tailor.chat_json")
def test_tailor_resume_fills_defaults(mock_chat):
    mock_chat.return_value = {"summary": "tailored line"}
    out = resume_tailor.tailor_resume(
        candidate_profile={"full_name": "X"},
        jd={"keywords": ["Python"]},
        template_type="private",
    )
    assert out["summary"] == "tailored line"
    assert out["skills"] == {}
    assert out["tailored_work"] == []
    assert out["missing_keywords"] == []
    assert out["warnings"] == []


@patch("app.services.resume_tailor.chat_json")
def test_tailor_resume_passes_template_type(mock_chat):
    mock_chat.return_value = {}
    resume_tailor.tailor_resume({}, {}, template_type="federal", extra_instructions="emphasize linux")
    args, kwargs = mock_chat.call_args
    payload = args[1]
    assert '"template_type": "federal"' in payload
    assert "emphasize linux" in payload
