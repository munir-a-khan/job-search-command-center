# Backend — FastAPI + Claude + Tectonic

![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Pydantic 2](https://img.shields.io/badge/Pydantic-2-E92063?style=flat-square&logo=pydantic&logoColor=white)
![Claude Sonnet 4.6](https://img.shields.io/badge/Claude-Sonnet_4.6-D97757?style=flat-square&logo=anthropic&logoColor=white)
![Tectonic LaTeX](https://img.shields.io/badge/Tectonic-LaTeX-008080?style=flat-square&logo=overleaf&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![pytest 23 passing](https://img.shields.io/badge/pytest-23_passing-brightgreen?style=flat-square&logo=pytest&logoColor=white)

The backend is a single FastAPI app. Its job is to:

1. Accept a raw job description, ask Claude to extract structured fields, persist both.
2. Accept a profile (work history, education, skills, projects) and persist it.
3. When asked to generate a resume, send `profile + jd + template_type` to Claude, take back tailored bullets, render a LaTeX file with Jinja2, compile a PDF with Tectonic, and return paths + an ATS check.
4. Generate cover letters the same way (text, no LaTeX).
5. Expose CRUD + a dashboard summary over applications.

## Project layout

```
backend/
├── Dockerfile                  # python:3.11-slim + Tectonic 0.15 + Liberation Sans
├── pytest.ini
├── requirements.txt
├── app/
│   ├── main.py                 # FastAPI app + lifespan, mounts routers with auth dep
│   ├── config.py               # pydantic-settings Settings (env-driven)
│   ├── security.py             # require_api_key dependency
│   ├── db/
│   │   ├── database.py         # SQLAlchemy engine + SessionLocal + get_db
│   │   └── models.py           # Profile, JobDescription, Application
│   ├── schemas/
│   │   └── models.py           # Pydantic IO models
│   ├── routers/
│   │   ├── profiles.py
│   │   ├── jds.py              # POST parses with Claude before saving
│   │   ├── applications.py     # + GET /api/applications/dashboard/summary
│   │   └── generate.py         # POST /resume, POST /cover-letter, GET /file
│   ├── services/
│   │   ├── claude_client.py    # SDK wrapper, JSON-mode helper, error type
│   │   ├── jd_parser.py        # parse_jd(raw, source)
│   │   ├── resume_tailor.py    # tailor_resume(profile, jd, template_type, extra)
│   │   ├── cover_letter.py     # generate_cover_letter(profile, jd, extra)
│   │   └── latex_render.py     # Jinja2 render + Tectonic compile + ATS check
│   └── latex_templates/
│       ├── private.tex.j2
│       ├── federal.tex.j2
│       └── state.tex.j2
└── tests/
    ├── conftest.py             # in-memory SQLite via dependency_overrides
    ├── test_jd_parser.py
    ├── test_resume_tailor.py
    ├── test_cover_letter.py
    ├── test_latex_render.py
    ├── test_routes.py
    └── test_auth.py
```

## Environment

All settings load from environment (Pydantic `BaseSettings`). They live in the root `.env` (the file is git-ignored).

| Var | Default | Required | Notes |
| --- | --- | --- | --- |
| `ANTHROPIC_API_KEY` | _empty_ | yes for AI | Anthropic key used by the SDK. |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | no | Any Anthropic model ID. |
| `API_KEY` | _empty_ | recommended | If set, every `/api/*` request (except `/api/health`) must send `X-API-Key: <value>`. If empty, auth is disabled (dev mode). |
| `DATABASE_URL` | `sqlite:////data/app.db` | no | Use a Postgres URL to switch engines; the code is engine-agnostic. |
| `CORS_ORIGINS` | `localhost:5173,…` | no | Comma-separated. |

## Running locally (without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\Activate on Windows
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
export API_KEY=any-random-string
uvicorn app.main:app --reload
```

Without Tectonic on your `PATH`, the JSON endpoints work fine — only the PDF compile step fails. The Dockerfile installs Tectonic v0.15.0; for native installs see <https://tectonic-typesetting.github.io/>.

## API reference

Generated docs are always at `http://localhost:8000/docs` once the app is up. Summary:

### `GET /api/health`

Open endpoint. Returns `{ ok, model, claude_configured, auth_required }`. The frontend uses `auth_required` to decide whether the API key bar is needed.

### Profiles · `/api/profiles`

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | list profiles |
| `POST` | `/` | create profile from `ProfileCreate` |
| `GET` | `/{id}` | fetch one |
| `PUT` | `/{id}` | full replace |
| `DELETE` | `/{id}` | delete |

Profile fields: `full_name`, `email`, `phone`, `location`, `linkedin`, `github`, `website`, `summary`, `education[]`, `work_history[]` (with optional federal fields `hours_per_week`, `salary`, `supervisor`, `may_contact`), `projects[]`, `skills` (category → freeform string), `certifications[]`.

### Job descriptions · `/api/jds`

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | list |
| `POST` | `/` | parse with Claude, then save |
| `GET` | `/{id}` | fetch one |
| `DELETE` | `/{id}` | delete |

`POST` body: `{ raw_text, posting_url, source }` where `source` is `private | federal | state`.

### Applications · `/api/applications`

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | list |
| `POST` | `/` | create application (links profile + JD) |
| `GET` | `/{id}` | fetch one |
| `PATCH` | `/{id}` | partial update — `status`, dates, `notes`, `template_type` |
| `DELETE` | `/{id}` | delete |
| `GET` | `/dashboard/summary` | totals, status breakdown, follow-ups due in 3 days, recent activity |

Statuses: `saved | applied | interview | offer | rejected | withdrawn`.

### Generation · `/api/generate`

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/resume` | tailor + render + compile. Returns `tex_path`, `pdf_path`, `tailored_bullets`, `summary`, `missing_keywords`, `pages`, `warnings`. |
| `POST` | `/cover-letter` | tailor + write. Returns `body` and `path`. |
| `GET` | `/file?path=…` | download any artifact under `DATA_DIR`. Validates the path can't escape via `..`. |

## How a resume is built

```
client → POST /api/generate/resume {application_id, template_type}
              │
              ▼
   load Application → Profile, JD
              │
              ▼
   resume_tailor.tailor_resume(profile, jd.parsed, template_type)
              │
              │   sends a strict JSON-schema prompt to Claude;
              │   gets back {summary, skills, tailored_work[], tailored_projects[],
              │              missing_keywords, warnings}
              ▼
   _merge_tailored(profile, tailored)
              │
              │   keeps real companies/titles/dates intact;
              │   only replaces bullets and summary.
              ▼
   latex_render.render_tex(template_type, {profile, jd, template_type})
              │
              │   Jinja2 with LaTeX-safe delimiters (<< >>, <% %>);
              │   `tex` filter escapes &, %, $, #, _, etc.
              ▼
   latex_render.compile_pdf(tex, /data/resumes)
              │
              │   spawn `tectonic compile` in a temp dir,
              │   copy resume.pdf + resume.tex out, count pages.
              ▼
   latex_render.ats_check(pdf, keywords)
              │
              │   pypdf extracts text, checks for missing keywords
              │   and unicode ligatures.
              ▼
   persist resume_path + resume_tex_path on Application
              │
              ▼
   return ResumeGenResult to client
```

## Tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest
```

23 tests, all fast (~0.6 s). The strategy:

- Claude is mocked at the `services.claude_client` level (no network).
- The Jinja → LaTeX render path is tested for real (string in, string out).
- The PDF compile path is **not** unit-tested; it's smoke-tested inside the container against `tectonic` after `docker compose up`.
- `conftest.py` overrides the FastAPI `get_db` dependency to use a fresh per-test SQLite file, so the suite is hermetic and reorder-safe.

## Adding a new resume template

1. Drop `your_template.tex.j2` into `app/latex_templates/`.
2. Use the Jinja delimiters from the existing templates: `<<expr|tex>>`, `<% for … %>`, `<# comment #>`.
3. Add the key to the `name` map in `latex_render.render_tex`.
4. Add a UI option in `frontend/src/pages/Applications.jsx` and `ApplicationDetail.jsx`.

## Adding a new Claude-backed feature

Pattern: write a small module under `services/`, use `chat_json` or `chat_text` from `claude_client.py`, surface a typed Pydantic schema in `schemas/models.py`, mount a route under `routers/`. The Claude wrapper handles fence-stripping, regex JSON fallback, and a consistent `ClaudeError → HTTP 502` mapping.
