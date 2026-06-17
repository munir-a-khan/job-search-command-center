from .claude_client import chat_json

SYSTEM = (
    "You are a job-description parser for a job application command center. "
    "Read the raw posting and extract a clean structured record. "
    "Be conservative: if a field is not present, return an empty string or empty list. "
    "Keywords should be specific technical and domain terms a resume should mirror."
)

JSON_SCHEMA_HINT = """
Return JSON with this exact shape:
{
  "company": "",
  "role": "",
  "location": "",
  "seniority": "",
  "salary_range": "",
  "must_have_skills": [],
  "nice_to_have_skills": [],
  "keywords": [],
  "responsibilities": [],
  "requirements": [],
  "summary": ""
}
- "summary" is one sentence describing the role.
- "keywords" is 8-20 ATS-style terms from the posting.
- Strings only, no nesting beyond arrays of strings.
""".strip()


def parse_jd(raw_text: str, source: str = "private") -> dict:
    user = (
        f"{JSON_SCHEMA_HINT}\n\n"
        f"Source channel: {source} (private | federal | state).\n\n"
        f"Raw posting:\n---\n{raw_text}\n---"
    )
    data = chat_json(SYSTEM, user, max_tokens=2048)
    for k in (
        "must_have_skills",
        "nice_to_have_skills",
        "keywords",
        "responsibilities",
        "requirements",
    ):
        v = data.get(k, [])
        if not isinstance(v, list):
            data[k] = [str(v)] if v else []
        else:
            data[k] = [str(x) for x in v if x]
    for k in ("company", "role", "location", "seniority", "salary_range", "summary"):
        data[k] = str(data.get(k, "") or "")
    return data
