"""
LexGuard — AI Contract Intelligence Platform
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.requests import Request
from starlette.responses import Response
from pathlib import Path

from config import CORS_ORIGINS
from rag.vector_store import init_vector_store
from api.routes import upload, analyze, report, compare


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, cleanup on shutdown."""
    # Startup: initialize ChromaDB
    init_vector_store()
    print("✅ LexGuard backend started — ChromaDB initialized")
    yield
    # Shutdown cleanup
    print("🛑 LexGuard backend shutting down")


app = FastAPI(
    title="LexGuard",
    description="AI-Powered Contract Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    return response

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routes ──────────────────────────────────────────────────────────
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(report.router, prefix="/api", tags=["Reports"])
app.include_router(compare.router, prefix="/api", tags=["Compare"])

# Serve the frontend static files built into `/app/frontend_dist`
frontend_dir = Path(__file__).resolve().parent / "frontend_dist"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    index = frontend_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"detail": "Not Found"}


@app.get("/")
async def root():
    return {
        "name": "LexGuard",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
