import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..db.database import get_db
from ..db import models
from ..schemas.models import (
    CoverLetterRequest,
    CoverLetterResult,
    ResumeGenRequest,
    ResumeGenResult,
)
from ..services.resume_tailor import tailor_resume
from ..services.cover_letter import generate_cover_letter
from ..services.latex_render import render_tex, compile_pdf, ats_check
from ..services.claude_client import ClaudeError

router = APIRouter(prefix="/api/generate", tags=["generate"])


def _profile_to_dict(p: models.Profile) -> dict:
    return {
        "full_name": p.full_name,
        "email": p.email,
        "phone": p.phone,
        "location": p.location,
        "linkedin": p.linkedin,
        "github": p.github,
        "website": p.website,
        "summary": p.summary,
        "education": p.education or [],
        "work_history": p.work_history or [],
        "projects": p.projects or [],
        "skills": p.skills or {},
        "certifications": p.certifications or [],
    }


def _merge_tailored(profile: dict, tailored: dict) -> dict:
    merged = dict(profile)
    merged["summary"] = tailored.get("summary") or profile.get("summary", "")
    merged["skills"] = tailored.get("skills") or profile.get("skills", {})
    by_company_title = {
        (w.get("company", "").strip().lower(), w.get("title", "").strip().lower()): w
        for w in tailored.get("tailored_work", [])
    }
    new_work = []
    for w in profile.get("work_history", []):
        key = (w.get("company", "").strip().lower(), w.get("title", "").strip().lower())
        clone = dict(w)
        if key in by_company_title:
            clone["bullets"] = by_company_title[key].get("bullets", clone.get("bullets", []))
        new_work.append(clone)
    merged["work_history"] = new_work
    by_name = {p.get("name", "").strip().lower(): p for p in tailored.get("tailored_projects", [])}
    new_projects = []
    for p in profile.get("projects", []):
        clone = dict(p)
        key = p.get("name", "").strip().lower()
        if key in by_name:
            clone["bullets"] = by_name[key].get("bullets", clone.get("bullets", []))
        new_projects.append(clone)
    merged["projects"] = new_projects
    return merged


@router.post("/resume", response_model=ResumeGenResult)
def generate_resume(payload: ResumeGenRequest, db: Session = Depends(get_db)):
    app = db.get(models.Application, payload.application_id)
    if not app:
        raise HTTPException(404, "application not found")
    profile = db.get(models.Profile, app.profile_id)
    jd = db.get(models.JobDescription, app.jd_id)
    if not profile or not jd:
        raise HTTPException(400, "application is missing profile or JD")

    profile_dict = _profile_to_dict(profile)
    try:
        tailored = tailor_resume(
            profile_dict,
            jd.parsed or {},
            template_type=payload.template_type,
            extra_instructions=payload.extra_instructions,
        )
    except ClaudeError as e:
        raise HTTPException(502, f"Claude tailor failed: {e}")

    merged = _merge_tailored(profile_dict, tailored)
    context = {
        "profile": merged,
        "jd": jd.parsed or {},
        "template_type": payload.template_type,
    }
    try:
        tex_source = render_tex(payload.template_type, context)
    except Exception as e:
        raise HTTPException(500, f"LaTeX render failed: {e}")

    out_dir = Path(settings.data_dir) / "resumes"
    try:
        tex_path, pdf_path, pages, warnings = compile_pdf(tex_source, out_dir)
    except Exception as e:
        raise HTTPException(500, f"PDF compile failed: {e}")

    ats = ats_check(pdf_path, (jd.parsed or {}).get("keywords", []))

    app.resume_path = pdf_path
    app.resume_tex_path = tex_path
    app.template_type = payload.template_type
    db.commit()

    tailored_bullets = {}
    for w in tailored.get("tailored_work", []):
        key = f"{w.get('company', '')} - {w.get('title', '')}".strip(" -")
        tailored_bullets[key] = w.get("bullets", [])

    return ResumeGenResult(
        tex_path=tex_path,
        pdf_path=pdf_path,
        tailored_bullets=tailored_bullets,
        summary=tailored.get("summary", ""),
        missing_keywords=ats.get("missing_keywords", tailored.get("missing_keywords", [])),
        pages=pages,
        warnings=warnings + tailored.get("warnings", []),
    )


@router.post("/cover-letter", response_model=CoverLetterResult)
def generate_cover_letter_route(payload: CoverLetterRequest, db: Session = Depends(get_db)):
    app = db.get(models.Application, payload.application_id)
    if not app:
        raise HTTPException(404, "application not found")
    profile = db.get(models.Profile, app.profile_id)
    jd = db.get(models.JobDescription, app.jd_id)
    if not profile or not jd:
        raise HTTPException(400, "application is missing profile or JD")

    try:
        body = generate_cover_letter(
            _profile_to_dict(profile),
            jd.parsed or {},
            extra_instructions=payload.extra_instructions,
        )
    except ClaudeError as e:
        raise HTTPException(502, f"Claude cover letter failed: {e}")

    out_dir = Path(settings.data_dir) / "cover_letters"
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"cover-{app.id}.txt"
    full = out_dir / fname
    full.write_text(body, encoding="utf-8")
    app.cover_letter_path = str(full)
    db.commit()

    return CoverLetterResult(body=body, path=str(full))


@router.get("/file")
def download_file(path: str):
    base = Path(settings.data_dir).resolve()
    p = Path(path).resolve()
    if base not in p.parents and p != base:
        raise HTTPException(400, "path escapes data dir")
    if not p.exists():
        raise HTTPException(404, "file not found")
    media = "application/pdf" if p.suffix.lower() == ".pdf" else "text/plain"
    return FileResponse(p, media_type=media, filename=p.name)
