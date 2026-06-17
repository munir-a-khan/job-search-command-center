from unittest.mock import patch
from app.services import cover_letter


@patch("app.services.cover_letter.chat_text")
def test_cover_letter_strips(mock_chat):
    mock_chat.return_value = "\n\nDear hiring manager,\n\nBody.\n\n"
    out = cover_letter.generate_cover_letter(
        {"full_name": "Jane"},
        {"company": "FooCorp", "role": "BE"},
        extra_instructions="be concise",
    )
    assert out.startswith("Dear")
    assert not out.endswith("\n")


@patch("app.services.cover_letter.chat_text")
def test_cover_letter_includes_inputs(mock_chat):
    mock_chat.return_value = "ok"
    cover_letter.generate_cover_letter({"full_name": "Jane"}, {"company": "FooCorp"})
    args, kwargs = mock_chat.call_args
    user = args[1]
    assert "Jane" in user
    assert "FooCorp" in user
