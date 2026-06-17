from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db import models
from ..schemas.models import ProfileCreate, ProfileOut
from ..services.resume_parser import parse_resume_pdf, ResumeParseError

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

MAX_RESUME_BYTES = 5 * 1024 * 1024  # 5 MB


def _to_dict(profile: ProfileCreate) -> dict:
    data = profile.model_dump()
    data["education"] = [e for e in data.get("education", [])]
    data["work_history"] = [w for w in data.get("work_history", [])]
    data["projects"] = [p for p in data.get("projects", [])]
    return data


@router.post("/from-resume")
async def profile_from_resume(file: UploadFile = File(...)):
    """Parse a resume PDF with Claude and return pre-filled profile data (does NOT save)."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_RESUME_BYTES:
        raise HTTPException(413, "File too large — maximum 5 MB")
    if not pdf_bytes:
        raise HTTPException(400, "Uploaded file is empty")

    try:
        data = parse_resume_pdf(pdf_bytes)
    except ResumeParseError as e:
        raise HTTPException(422, str(e))

    return data


@router.get("", response_model=list[ProfileOut])
def list_profiles(db: Session = Depends(get_db)):
    return db.query(models.Profile).order_by(models.Profile.id.desc()).all()


@router.post("", response_model=ProfileOut)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    obj = models.Profile(**_to_dict(payload))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Profile, profile_id)
    if not obj:
        raise HTTPException(404, "profile not found")
    return obj


@router.put("/{profile_id}", response_model=ProfileOut)
def update_profile(profile_id: int, payload: ProfileCreate, db: Session = Depends(get_db)):
    obj = db.get(models.Profile, profile_id)
    if not obj:
        raise HTTPException(404, "profile not found")
    for k, v in _to_dict(payload).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Profile, profile_id)
    if not obj:
        raise HTTPException(404, "profile not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
