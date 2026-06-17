from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db import models
from ..schemas.models import ProfileCreate, ProfileOut

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


def _to_dict(profile: ProfileCreate) -> dict:
    data = profile.model_dump()
    data["education"] = [e for e in data.get("education", [])]
    data["work_history"] = [w for w in data.get("work_history", [])]
    data["projects"] = [p for p in data.get("projects", [])]
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
