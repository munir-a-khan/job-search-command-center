from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, default="")
    location = Column(String, default="")
    linkedin = Column(String, default="")
    github = Column(String, default="")
    website = Column(String, default="")
    summary = Column(Text, default="")
    education = Column(JSON, default=list)
    work_history = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    skills = Column(JSON, default=dict)
    certifications = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True)
    raw_text = Column(Text, nullable=False)
    company = Column(String, default="")
    role = Column(String, default="")
    location = Column(String, default="")
    posting_url = Column(String, default="")
    source = Column(String, default="private")  # private | federal | state
    parsed = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    applications = relationship("Application", back_populates="jd", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"))
    status = Column(String, default="saved")  # saved | applied | interview | offer | rejected | withdrawn
    applied_date = Column(DateTime, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    notes = Column(Text, default="")
    resume_path = Column(String, default="")
    resume_tex_path = Column(String, default="")
    cover_letter_path = Column(String, default="")
    template_type = Column(String, default="private")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    jd = relationship("JobDescription", back_populates="applications")
    profile = relationship("Profile")
