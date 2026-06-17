from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.database import Base, engine
from .db import models  # noqa: F401  ensures models register
from .routers import applications, generate, jds, profiles
from .security import require_api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Job Search Command Center", version="0.1.0", lifespan=lifespan)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_dep = [Depends(require_api_key)]
app.include_router(profiles.router, dependencies=auth_dep)
app.include_router(jds.router, dependencies=auth_dep)
app.include_router(applications.router, dependencies=auth_dep)
app.include_router(generate.router, dependencies=auth_dep)


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "model": settings.claude_model,
        "claude_configured": bool(settings.anthropic_api_key),
        "auth_required": bool(settings.api_key),
    }
