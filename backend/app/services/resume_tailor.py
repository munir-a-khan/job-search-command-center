from .claude_client import chat_json

SYSTEM = (
    "You are an expert resume strategist. You rewrite a candidate's existing work-history "
    "bullets so they mirror the language of a target job description while remaining 100% truthful. "
    "Do not invent skills, tools, certifications, employers, dates, metrics, or experience. "
    "Bold-worthy keywords (no markup, just real language) come from the JD. "
    "Bullets must remain concise: under 28 words each, lead with a strong verb."
)

INSTRUCTIONS = """
You receive:
- candidate_profile: structured profile (name, summary, work_history, projects, skills, education).
- jd: parsed job description with keywords/requirements.
- template_type: 'private' (one-page, terse), 'federal' (USAJOBS-style, longer bullets with measurable detail), or 'state' (CalCareers/CalJOBS - one page, exact duty-statement language).
- extra_instructions: free-form caller notes (can be empty).

Return JSON:
{
  "summary": "<one short sentence tailored to this JD>",
  "skills": {"Languages": "...", "Backend": "...", "Tools": "...", "Soft": "..."},
  "tailored_work": [
    {"company": "<exact match>", "title": "<exact match>", "bullets": ["...", "..."]}
  ],
  "tailored_projects": [
    {"name": "<exact match>", "bullets": ["..."]}
  ],
  "missing_keywords": ["<JD keywords the candidate truly has no basis for>"],
  "warnings": ["<honesty risks: missing required certs, clearance, license, years of experience>"]
}

Rules:
- Keep the same companies / titles / project names / dates / education that exist in the profile. Do not invent new ones.
- Only include companies/projects that are actually relevant to this JD; you may omit weaker ones.
- For 'federal' template_type, write 3-6 bullets per job, each can be longer (under 40 words), include outcomes.
- For 'private' or 'state' template_type, write 2-4 short bullets per job, under 22 words each.
- "skills" map keys should be category labels you choose based on what the JD prioritizes.
- "missing_keywords" is for items the candidate genuinely lacks - do NOT fabricate them into bullets.
"""


def tailor_resume(candidate_profile: dict, jd: dict, template_type: str = "private", extra_instructions: str = "") -> dict:
    user_payload = {
        "candidate_profile": candidate_profile,
        "jd": jd,
        "template_type": template_type,
        "extra_instructions": extra_instructions,
    }
    import json as _json
    user = INSTRUCTIONS + "\n\nINPUT:\n" + _json.dumps(user_payload, ensure_ascii=False)
    data = chat_json(SYSTEM, user, max_tokens=3500)
    data.setdefault("summary", "")
    data.setdefault("skills", {})
    data.setdefault("tailored_work", [])
    data.setdefault("tailored_projects", [])
    data.setdefault("missing_keywords", [])
    data.setdefault("warnings", [])
    return data
