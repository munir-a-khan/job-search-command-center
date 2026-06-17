"""Parse a resume PDF into a structured profile using pypdf + Claude."""
import io

from pypdf import PdfReader

from .claude_client import chat_json, ClaudeError

SYSTEM = (
    "You are a resume parser. Extract structured information from the resume text provided. "
    "Return only information clearly present in the resume. "
    "Use empty strings or empty lists for any missing fields — never guess or fabricate data."
)

JSON_SCHEMA = """
Return JSON with this exact shape (no extra keys):
{
  "full_name": "",
  "email": "",
  "phone": "",
  "location": "",
  "linkedin": "",
  "github": "",
  "website": "",
  "summary": "",
  "education": [
    {"school":"","degree":"","location":"","start":"","end":"","gpa":"","coursework":"","honors":""}
  ],
  "work_history": [
    {"title":"","company":"","location":"","start":"","end":"",
     "hours_per_week":"","salary":"","supervisor":"","may_contact":"Yes","bullets":[]}
  ],
  "projects": [
    {"name":"","focus":"","date":"","bullets":[]}
  ],
  "skills": {"Languages": "Python, Java", "Frameworks": "React, FastAPI"},
  "certifications": []
}

Rules:
- bullets: array of strings, one achievement per entry
- skills: dict mapping category name to comma-separated values (string)
- education/work_history/projects: arrays (can be empty [])
- certifications: array of strings
""".strip()


class ResumeParseError(RuntimeError):
    pass


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from a PDF using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as e:
        raise ResumeParseError(f"Could not read PDF: {e}")

    pages_text = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            pages_text.append(t)

    text = "\n".join(pages_text).strip()
    if not text:
        raise ResumeParseError(
            "Could not extract text from this PDF. "
            "It may be a scanned image — try copy-pasting the text manually into the Profile form."
        )
    return text


def parse_resume_pdf(pdf_bytes: bytes) -> dict:
    """Extract text from PDF, parse with Claude, return normalized profile dict."""
    text = extract_text_from_pdf(pdf_bytes)

    user = f"{JSON_SCHEMA}\n\nResume text:\n---\n{text[:10_000]}\n---"
    try:
        data = chat_json(SYSTEM, user, max_tokens=3000)
    except ClaudeError as e:
        raise ResumeParseError(f"Claude parse failed: {e}")

    # Normalize types so the output always matches ProfileCreate schema
    for k in ("education", "work_history", "projects"):
        v = data.get(k, [])
        data[k] = v if isinstance(v, list) else []

    certs = data.get("certifications", [])
    data["certifications"] = certs if isinstance(certs, list) else []

    skills = data.get("skills", {})
    data["skills"] = skills if isinstance(skills, dict) else {}

    for k in ("full_name", "email", "phone", "location", "linkedin", "github", "website", "summary"):
        data[k] = str(data.get(k, "") or "")

    return data
