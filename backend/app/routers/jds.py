from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db import models
from ..schemas.models import JDCreate, JDOut
from ..services.jd_parser import parse_jd
from ..services.claude_client import ClaudeError

router = APIRouter(prefix="/api/jds", tags=["job-descriptions"])


@router.get("", response_model=list[JDOut])
def list_jds(db: Session = Depends(get_db)):
    return db.query(models.JobDescription).order_by(models.JobDescription.id.desc()).all()


@router.post("", response_model=JDOut)
def create_jd(payload: JDCreate, db: Session = Depends(get_db)):
    raw = (payload.raw_text or "").strip()
    if not raw:
        raise HTTPException(400, "raw_text is required")
    try:
        parsed = parse_jd(raw, source=payload.source)
    except ClaudeError as e:
        raise HTTPException(502, f"Claude parse failed: {e}")
    obj = models.JobDescription(
        raw_text=raw,
        posting_url=payload.posting_url,
        source=payload.source,
        parsed=parsed,
        company=parsed.get("company", ""),
        role=parsed.get("role", ""),
        location=parsed.get("location", ""),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{jd_id}", response_model=JDOut)
def get_jd(jd_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.JobDescription, jd_id)
    if not obj:
        raise HTTPException(404, "JD not found")
    return obj


@router.delete("/{jd_id}")
def delete_jd(jd_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.JobDescription, jd_id)
    if not obj:
        raise HTTPException(404, "JD not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
