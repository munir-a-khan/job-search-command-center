import json
import re
from anthropic import Anthropic
from ..config import settings


class ClaudeError(RuntimeError):
    pass


def _client() -> Anthropic:
    if not settings.anthropic_api_key:
        raise ClaudeError("ANTHROPIC_API_KEY is not configured")
    return Anthropic(api_key=settings.anthropic_api_key)


def _extract_text(response) -> str:
    parts: list[str] = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts).strip()


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return text


def chat_json(system: str, user: str, max_tokens: int = 2048) -> dict:
    client = _client()
    resp = client.messages.create(
        model=settings.claude_model,
        max_tokens=max_tokens,
        system=system + "\n\nYou MUST respond with a single JSON object and nothing else.",
        messages=[{"role": "user", "content": user}],
    )
    raw = _strip_json_fence(_extract_text(resp))
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise ClaudeError(f"Model did not return valid JSON: {exc}\n---\n{raw[:1200]}")


def chat_text(system: str, user: str, max_tokens: int = 2048) -> str:
    client = _client()
    resp = client.messages.create(
        model=settings.claude_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return _extract_text(resp)
