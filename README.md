# Job Search Command Center

A fully dockerized, AI-powered web app for managing a job hunt end to end.

- **Job Description Parser** — paste a JD, Claude extracts role, company, requirements, ATS keywords.
- **Resume Tailor** — Claude rewrites your bullet points to mirror the JD, then compiles a real PDF via Tectonic.
- **Cover Letter Generator** — short, sincere, plain-text cover letters.
- **Application Tracker** — status, dates, follow-up reminders, notes per application.
- **Pipeline Dashboard** — KPIs and recent activity across the whole pipeline.

Three resume formats are supported out of the box:
| Channel | Template | Page target | Style |
| --- | --- | --- | --- |
| `private` | `private.tex.j2` | 1 page | terse, ATS-friendly |
| `federal` | `federal.tex.j2` | 2 pages | USAJOBS-style with hours, salary, supervisor |
| `state` | `state.tex.j2` | 1 page | CalCareers / CalJOBS-style |

You can swap or extend the LaTeX templates in `backend/app/latex_templates/` without touching the rest of the stack.

## Stack

| Layer | Tech |
| --- | --- |
| Frontend | React 18 + Vite, served via Nginx |
| Backend | FastAPI + SQLAlchemy + Jinja2 |
| AI | Claude API (`claude-sonnet-4-6` by default) |
| LaTeX | Tectonic (single static binary, ~50 MB) |
| Storage | SQLite (bind-mounted under `./data`) |
| Containerization | Docker + docker-compose |

## Quick start

1. Copy `.env.example` → `.env` and set:
   - `ANTHROPIC_API_KEY` — Claude API key.
   - `API_KEY` — anything random (e.g. `openssl rand -hex 32`); the backend rejects any request without `X-API-Key: <this value>`. Leave empty in dev to disable auth.
2. Bring it up:
   ```bash
   docker compose up --build
   ```
3. Open <http://localhost:8080>. Paste your `API_KEY` into the top bar; it's saved in localStorage. The API is on <http://localhost:8000> with docs at `/docs`.

The first build downloads Tectonic and warms its cache; expect 3–5 minutes the first time.

## Typical flow

1. **Profile** — enter your work history, education, projects, skills. Bullets here are *baselines* — Claude rewrites them per job.
2. **Job Descriptions** — paste a posting, pick the channel (private / federal / state), parse with Claude.
3. **Applications** — pair a profile with a JD, pick a template.
4. **Application detail** — click *Generate resume* (produces a PDF + .tex) and *Generate cover letter*.
5. **Dashboard** — track status, follow-up reminders, and recent activity.

## Truthfulness

The resume tailor prompt explicitly forbids inventing experience, certifications, dates, employers, or metrics. If the JD requires something you genuinely lack, it will surface those gaps under `missing_keywords` / `warnings` instead of fabricating them.

## Layout

```
job-search-command-center/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── db/
│       ├── routers/
│       ├── schemas/
│       ├── services/
│       └── latex_templates/
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    └── src/
        ├── api/
        ├── pages/
        └── styles/
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST/PUT/DELETE | `/api/profiles` | Profile CRUD |
| GET/POST/DELETE | `/api/jds` | JD CRUD; POST parses via Claude |
| GET/POST/PATCH/DELETE | `/api/applications` | Application CRUD |
| GET | `/api/applications/dashboard/summary` | Dashboard aggregates |
| POST | `/api/generate/resume` | Tailor + render + compile resume PDF |
| POST | `/api/generate/cover-letter` | Generate cover letter |
| GET | `/api/generate/file?path=…` | Download a generated artifact |

Full OpenAPI schema at <http://localhost:8000/docs>.

## License

MIT.
