"""
Standard Error Handling Schemas and Custom Exception
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

import logging
from pydantic import BaseModel
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("bhnmistra")


class ErrorResponse(BaseModel):
    """
    Standardized Error Response schema as required by PRD Section 8.
    All error responses across the platform must follow this exact contract.
    """
    code: str
    message: str
    suggested_action: str


class AppException(Exception):
    """
    Custom application exception that formats into our standard ErrorResponse.
    """
    def __init__(self, status_code: int, code: str, message: str, suggested_action: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.suggested_action = suggested_action
        super().__init__(message)


def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    FastAPI exception handler that converts AppException into a JSONResponse.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "suggested_action": exc.suggested_action,
        },
    )


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    FastAPI exception handler that converts Pydantic validation errors
    into the required 3-field standard ErrorResponse.
    Ensures validation messages end with exactly one final period.
    """
    errors = exc.errors() if exc else []
    first_error = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", []))
    raw_msg = first_error.get("msg")

    if raw_msg is not None:
        clean_msg = str(raw_msg).strip().rstrip(".")
        clean_msg = clean_msg.strip()
    else:
        clean_msg = ""

    if not clean_msg:
        clean_msg = "Invalid request parameters"

    message = f"Validation failed for '{field}': {clean_msg}."

    return JSONResponse(
        status_code=422,
        content={
            "code": "INVALID_REQUEST_PARAMETERS",
            "message": message,
            "suggested_action": "Check the API schema at /docs and provide all required fields in the expected format.",
        },
    )


def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Standardizes generic HTTP exceptions (such as 404 Route Not Found or 405 Method Not Allowed)
    into the PRD Section 8 standard ErrorResponse without leaking internal details.
    """
    if exc.status_code == 404:
        code = "NOT_FOUND"
        message = str(exc.detail) if exc.detail else "Requested resource was not found."
        suggested_action = "Check the endpoint URL and review available routes at /docs."
    elif exc.status_code == 405:
        code = "METHOD_NOT_ALLOWED"
        message = str(exc.detail) if exc.detail else "HTTP method not allowed for this endpoint."
        suggested_action = "Verify the permitted HTTP methods for this endpoint at /docs."
    else:
        code = f"HTTP_{exc.status_code}"
        message = str(exc.detail) if exc.detail else "An HTTP error occurred."
        suggested_action = "Refer to the API documentation at /docs."

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": code,
            "message": message,
            "suggested_action": suggested_action,
        },
    )


def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all global exception handler for unexpected, unhandled server exceptions.
    Logs full exception trace internally for debugging, while shielding users and clients
    from internal stack traces, system paths, or credential leakage.
    """
    logger.error(
        f"Unhandled server error during {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred while processing your request.",
            "suggested_action": "Retry the request. If the issue persists, inspect the backend logs or contact the BHRAMANASTHRA engineering lead.",
        },
    )
