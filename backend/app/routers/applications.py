from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db import models
from ..schemas.models import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationUpdate,
    DashboardOut,
)

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationOut])
def list_apps(db: Session = Depends(get_db)):
    return db.query(models.Application).order_by(models.Application.id.desc()).all()


@router.post("", response_model=ApplicationOut)
def create_app(payload: ApplicationCreate, db: Session = Depends(get_db)):
    if not db.get(models.Profile, payload.profile_id):
        raise HTTPException(400, "profile not found")
    if not db.get(models.JobDescription, payload.jd_id):
        raise HTTPException(400, "JD not found")
    obj = models.Application(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{app_id}", response_model=ApplicationOut)
def get_app(app_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Application, app_id)
    if not obj:
        raise HTTPException(404, "application not found")
    return obj


@router.patch("/{app_id}", response_model=ApplicationOut)
def update_app(app_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Application, app_id)
    if not obj:
        raise HTTPException(404, "application not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{app_id}")
def delete_app(app_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Application, app_id)
    if not obj:
        raise HTTPException(404, "application not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}


@router.get("/dashboard/summary", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    apps = db.query(models.Application).all()
    by_status: dict[str, int] = {}
    for a in apps:
        by_status[a.status] = by_status.get(a.status, 0) + 1
    now = datetime.utcnow()
    horizon = now + timedelta(days=3)
    follow_ups = sum(1 for a in apps if a.follow_up_date and a.follow_up_date <= horizon)
    recent = []
    for a in sorted(apps, key=lambda x: x.updated_at or x.created_at, reverse=True)[:10]:
        jd = db.get(models.JobDescription, a.jd_id) if a.jd_id else None
        recent.append(
            {
                "id": a.id,
                "status": a.status,
                "company": getattr(jd, "company", ""),
                "role": getattr(jd, "role", ""),
                "applied_date": a.applied_date.isoformat() if a.applied_date else None,
                "follow_up_date": a.follow_up_date.isoformat() if a.follow_up_date else None,
                "updated_at": (a.updated_at or a.created_at).isoformat(),
            }
        )
    return DashboardOut(total=len(apps), by_status=by_status, follow_ups_due=follow_ups, recent=recent)
