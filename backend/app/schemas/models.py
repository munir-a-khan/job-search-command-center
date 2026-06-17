from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class EducationEntry(BaseModel):
    school: str = ""
    degree: str = ""
    location: str = ""
    start: str = ""
    end: str = ""
    gpa: str = ""
    coursework: str = ""
    honors: str = ""


class WorkEntry(BaseModel):
    title: str = ""
    company: str = ""
    location: str = ""
    start: str = ""
    end: str = ""
    hours_per_week: str = ""
    salary: str = ""
    supervisor: str = ""
    may_contact: str = "Yes"
    bullets: list[str] = []


class ProjectEntry(BaseModel):
    name: str = ""
    focus: str = ""
    date: str = ""
    bullets: list[str] = []


class ProfileBase(BaseModel):
    full_name: str
    email: str
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    summary: str = ""
    education: list[EducationEntry] = []
    work_history: list[WorkEntry] = []
    projects: list[ProjectEntry] = []
    skills: dict[str, str] = {}
    certifications: list[str] = []


class ProfileCreate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class JDCreate(BaseModel):
    # Provide raw_text, posting_url, or both.
    # If only posting_url is given, the backend will fetch and extract the text.
    raw_text: str = ""
    posting_url: str = ""
    source: str = "private"  # private | federal | state


class JDParsed(BaseModel):
    company: str = ""
    role: str = ""
    location: str = ""
    seniority: str = ""
    salary_range: str = ""
    must_have_skills: list[str] = []
    nice_to_have_skills: list[str] = []
    keywords: list[str] = []
    responsibilities: list[str] = []
    requirements: list[str] = []
    summary: str = ""


class JDOut(BaseModel):
    id: int
    raw_text: str
    company: str
    role: str
    location: str
    posting_url: str
    source: str
    parsed: dict[str, Any]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApplicationBase(BaseModel):
    profile_id: int
    jd_id: int
    status: str = "saved"
    applied_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    notes: str = ""
    template_type: str = "private"


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    applied_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    notes: Optional[str] = None
    template_type: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    profile_id: int
    jd_id: int
    status: str
    applied_date: Optional[datetime]
    follow_up_date: Optional[datetime]
    notes: str
    resume_path: str
    resume_tex_path: str
    cover_letter_path: str
    template_type: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ResumeGenRequest(BaseModel):
    application_id: int
    template_type: str = Field(default="private", description="private | federal | state")
    extra_instructions: str = ""


class ResumeGenResult(BaseModel):
    tex_path: str
    pdf_path: str
    tailored_bullets: dict[str, list[str]]
    summary: str
    missing_keywords: list[str]
    pages: int
    warnings: list[str] = []


class CoverLetterRequest(BaseModel):
    application_id: int
    extra_instructions: str = ""


class CoverLetterResult(BaseModel):
    body: str
    path: str


class DashboardOut(BaseModel):
    total: int
    by_status: dict[str, int]
    follow_ups_due: int
    recent: list[dict[str, Any]]
