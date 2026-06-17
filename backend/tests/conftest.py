import os
import tempfile

# Configure env BEFORE importing app modules so settings pick it up.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from app.db import models  # noqa: F401
from app import security as security_mod
from app import config as config_mod
from app.main import app


def _fresh_engine(path: str):
    url = f"sqlite:///{path}".replace("\\", "/")
    eng = create_engine(url, connect_args={"check_same_thread": False}, future=True)
    Base.metadata.create_all(bind=eng)
    return eng, sessionmaker(bind=eng, autoflush=False, autocommit=False, future=True)


@pytest.fixture()
def tmp_db():
    d = tempfile.mkdtemp(prefix="jscc-test-")
    path = os.path.join(d, "app.db")
    eng, SessionLocal = _fresh_engine(path)

    def _get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield d
    app.dependency_overrides.pop(get_db, None)
    eng.dispose()


@pytest.fixture()
def client(tmp_db, monkeypatch):
    monkeypatch.setattr(config_mod.settings, "api_key", "", raising=False)
    return TestClient(app)


@pytest.fixture()
def client_with_auth(tmp_db, monkeypatch):
    monkeypatch.setattr(config_mod.settings, "api_key", "secret-xyz", raising=False)
    return TestClient(app), "secret-xyz"


@pytest.fixture()
def sample_profile_payload():
    return {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+1 555 000 1111",
        "location": "Brooklyn, NY",
        "linkedin": "linkedin.com/in/janedoe",
        "github": "github.com/janedoe",
        "summary": "Backend engineer with 5 years building data platforms.",
        "education": [
            {
                "school": "NYU",
                "degree": "B.S. Computer Science",
                "location": "New York, NY",
                "start": "2016",
                "end": "2020",
                "gpa": "3.7",
                "coursework": "Algorithms, Databases, Distributed Systems",
                "honors": "",
            }
        ],
        "work_history": [
            {
                "title": "Senior Backend Engineer",
                "company": "Acme Data",
                "location": "Remote",
                "start": "2022",
                "end": "Present",
                "hours_per_week": "40",
                "salary": "",
                "supervisor": "",
                "may_contact": "Yes",
                "bullets": [
                    "Built FastAPI services and Postgres data pipelines.",
                    "Cut p99 latency from 800ms to 120ms via caching.",
                ],
            }
        ],
        "projects": [
            {"name": "Open Source CLI", "focus": "Python", "date": "2023", "bullets": ["Tool for managing config drift."]},
        ],
        "skills": {"Languages": "Python, Go, TypeScript", "Backend": "FastAPI, Postgres"},
        "certifications": [],
    }


@pytest.fixture()
def fake_parsed_jd():
    return {
        "company": "FooCorp",
        "role": "Backend Engineer",
        "location": "Remote",
        "seniority": "Mid-Senior",
        "salary_range": "",
        "must_have_skills": ["Python", "FastAPI"],
        "nice_to_have_skills": ["Kubernetes"],
        "keywords": ["Python", "FastAPI", "Postgres", "REST"],
        "responsibilities": ["Build APIs", "Own services"],
        "requirements": ["3+ years backend"],
        "summary": "Mid-senior backend engineer building Python/FastAPI services.",
    }
