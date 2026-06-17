from .claude_client import chat_text

SYSTEM = (
    "You write concise, sincere cover letters. Three short paragraphs. "
    "Open with the role and a specific reason the candidate fits. "
    "Middle paragraph cites two real, verifiable accomplishments from the candidate profile "
    "and ties them to the JD's needs. Close with availability and contact. "
    "No purple prose, no clichés ('passionate', 'dynamic', 'synergy'), no invented experience. "
    "Plain text only (no markdown)."
)


def generate_cover_letter(profile: dict, jd: dict, extra_instructions: str = "") -> str:
    import json as _json
    user = (
        "Write the cover letter as plain text, ready to paste. "
        "Use the candidate's real name, the real hiring company, and the real role.\n\n"
        f"Candidate profile:\n{_json.dumps(profile, ensure_ascii=False)}\n\n"
        f"Job description (parsed):\n{_json.dumps(jd, ensure_ascii=False)}\n\n"
        f"Additional caller instructions: {extra_instructions or '(none)'}\n"
    )
    return chat_text(SYSTEM, user, max_tokens=1500).strip()
