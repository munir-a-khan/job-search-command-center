import json
from unittest.mock import patch
from app.services import jd_parser


def fake_response(payload: dict):
    return json.dumps(payload)


@patch("app.services.jd_parser.chat_json")
def test_parse_jd_normalizes_lists(chat_json_mock):
    chat_json_mock.return_value = {
        "company": "FooCorp",
        "role": "Backend Engineer",
        "location": "Remote",
        "seniority": "Senior",
        "salary_range": "$150k-$180k",
        "must_have_skills": "Python",  # model returned a string instead of list
        "nice_to_have_skills": None,
        "keywords": ["Python", "FastAPI", ""],
        "responsibilities": ["Own services"],
        "requirements": [],
        "summary": "One liner.",
    }
    out = jd_parser.parse_jd("raw jd text", source="private")
    assert out["company"] == "FooCorp"
    assert out["must_have_skills"] == ["Python"]
    assert out["nice_to_have_skills"] == []
    assert out["keywords"] == ["Python", "FastAPI"]  # blank dropped
    assert isinstance(out["responsibilities"], list)
    assert out["summary"] == "One liner."


@patch("app.services.jd_parser.chat_json")
def test_parse_jd_passes_source(chat_json_mock):
    chat_json_mock.return_value = {}
    jd_parser.parse_jd("raw", source="federal")
    args, kwargs = chat_json_mock.call_args
    # second arg is user prompt; should mention federal
    assert "federal" in args[1].lower()
