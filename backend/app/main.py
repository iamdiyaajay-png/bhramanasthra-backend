"""
BHnMISnTRA Backend — Main Entry Point
NASA Space Apps Challenge 2026: Dancing with the SARs
Member 2: Backend, API Development & Evidence Ledger
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment variables from .env are loaded reliably
_backend_dir = Path(__file__).resolve().parent.parent
_backend_env = _backend_dir / ".env"
_root_env = _backend_dir.parent / ".env"
if _backend_env.is_file():
    load_dotenv(dotenv_path=_backend_env, override=False)
elif _root_env.is_file():
    load_dotenv(dotenv_path=_root_env, override=False)
else:
    load_dotenv(override=False)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.errors import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    global_exception_handler,
)
from app.routes import study_areas, investigations, ledger

# 1. Initialize FastAPI application with project metadata
app = FastAPI(
    title="BHnMISnTRA — Radar Evidence & Surface Change Platform",
    description=(
        "Backend API and Evidence Ledger for NASA Space Apps Challenge 2026. "
        "Investigates surface changes using SAR satellite data and the Beat Test."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 2. Register Standard Error Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 3. Configure Security Headers Middleware (SEC-03)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Middleware injecting defensive security headers into all responses:
    - X-Content-Type-Options: nosniff (prevents MIME type sniffing)
    - X-Frame-Options: SAMEORIGIN (prevents clickjacking while allowing same-origin embedding)
    - Referrer-Policy: strict-origin-when-cross-origin
    - Content-Security-Policy: Report-safe CSP permitting inline styling & print triggers,
      plus OpenAPI/Swagger UI assets.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
    )
    return response

# 4. Configure Explicit CORS (SEC-01)
# Trusted development origins for Vite, React, Next.js, and local server
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

cors_env = os.getenv("BHNMISNTRA_CORS_ORIGINS", "").strip()
allowed_origins = list(DEFAULT_CORS_ORIGINS)
if cors_env:
    for origin in cors_env.split(","):
        clean_origin = origin.strip()
        if clean_origin and clean_origin not in allowed_origins:
            allowed_origins.append(clean_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,  # Authentication uses API-key header, not cookies
    allow_methods=["*"],      # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],      # Allows X-API-Key, Content-Type, etc.
)

# 5. Include API Routers
app.include_router(study_areas.router, prefix="/api")
app.include_router(investigations.router, prefix="/api")
app.include_router(ledger.router, prefix="/api")

# 6. System Health Check Endpoint
@app.get("/api/health", tags=["System"])
def health_check():
    """
    System Health Check endpoint.
    Used by frontend and diagnostics to verify that the backend is online.
    """
    return {
        "status": "healthy",
        "service": "BHnMISnTRA Backend & Evidence Ledger",
        "challenge": "Dancing with the SARs",
        "version": "1.0.0",
    }

# 7. Root Endpoint
@app.get("/", tags=["System"])
def root():
    """Root landing endpoint pointing developers to documentation."""
    return {
        "message": "Welcome to BHnMISnTRA Radar Evidence Platform API",
        "docs": "/docs",
        "health": "/api/health",
    }
