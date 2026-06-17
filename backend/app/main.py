from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request, Response
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


# ── Security headers ──────────────────────────────────────────────────────────
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Remove server fingerprint header if present
    if "server" in response.headers:
        del response.headers["server"]
    return response


# ── CORS — only allow configured origins ─────────────────────────────────────
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)

auth_dep = [Depends(require_api_key)]
app.include_router(profiles.router, dependencies=auth_dep)
app.include_router(jds.router, dependencies=auth_dep)
app.include_router(applications.router, dependencies=auth_dep)
app.include_router(generate.router, dependencies=auth_dep)


@app.get("/api/health")
def health():
    # Never expose key values — only booleans
    return {
        "ok": True,
        "model": settings.claude_model,
        "claude_configured": bool(settings.anthropic_api_key),
        "auth_required": bool(settings.api_key),
    }
