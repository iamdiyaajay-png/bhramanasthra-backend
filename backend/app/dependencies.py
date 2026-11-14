"""
Authentication and Authorization Dependencies
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
Member 2: Backend Development & Evidence Ledger
"""

import os
import secrets
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Security, status
from fastapi.security import APIKeyHeader

from app.schemas.errors import AppException

# Ensure .env is loaded reliably regardless of working directory
_backend_dir = Path(__file__).resolve().parent.parent
_backend_env = _backend_dir / ".env"
_root_env = _backend_dir.parent / ".env"


def _load_env_files(override: bool = False) -> None:
    """Helper to load environment variables from backend/.env or root .env."""
    if _backend_env.is_file():
        load_dotenv(dotenv_path=_backend_env, override=override)
    elif _root_env.is_file():
        load_dotenv(dotenv_path=_root_env, override=override)
    else:
        load_dotenv(override=override)


_load_env_files(override=False)

# Declare APIKeyHeader security scheme for OpenAPI / Swagger UI
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="API Key required for mutation endpoints. Set 'X-API-Key' header.",
)


def get_server_api_key() -> str:
    """
    Retrieves the configured server API key from the environment.
    If initially empty, re-attempts loading from backend/.env or root .env
    dynamically without requiring a server restart.
    Returns stripped string or empty string if not configured.
    Never uses a hardcoded fallback.
    """
    key = os.getenv("BHNMISNTRA_API_KEY", "").strip()
    if not key:
        _load_env_files(override=True)
        key = os.getenv("BHNMISNTRA_API_KEY", "").strip()
    return key


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    FastAPI dependency that enforces authentication for protected mutation endpoints.
    - Constant-time verification using secrets.compare_digest.
    - Fails closed with HTTP 500 if the server key is missing or empty.
    - Fails with HTTP 401 if the client key is missing or invalid.
    """
    server_key = get_server_api_key()

    # Fail closed if server has no configured API key
    if not server_key:
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="SERVER_CONFIGURATION_ERROR",
            message="Backend authentication is not configured. Server API key is missing.",
            suggested_action="Set the 'BHNMISNTRA_API_KEY' environment variable in the server environment.",
        )

    # Missing client header
    if not api_key:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTHENTICATION_REQUIRED",
            message="Missing or invalid API key. Access to mutation endpoints requires authentication.",
            suggested_action="Provide a valid 'X-API-Key' header in your request.",
        )

    # Constant-time comparison
    if not secrets.compare_digest(api_key.strip(), server_key):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTHENTICATION_REQUIRED",
            message="Missing or invalid API key. Access to mutation endpoints requires authentication.",
            suggested_action="Provide a valid 'X-API-Key' header in your request.",
        )

    return api_key
