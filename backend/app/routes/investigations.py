"""
Investigation API Routes
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

from fastapi import APIRouter, Path, status, Depends
from fastapi.responses import FileResponse, HTMLResponse

from app.schemas.investigation import (
    InvestigationCreateRequest,
    InvestigationCreateResponse,
    InvestigationDetail,
)
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.schemas.errors import ErrorResponse
from app.services import investigation_service, evidence_service, layer_service, report_service
from app.dependencies import verify_api_key

router = APIRouter(tags=["Investigations & Evidence Ledger"])

# Standard boundary validation regex for safe path parameters (SEC-05)
ID_PATTERN = r"^[A-Za-z0-9_-]+$"


@router.post(
    "/investigations",
    response_model=InvestigationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new surface change investigation",
    description=(
        "Registers an investigation for a study area, baseline reference date, and comparison date. "
        "Validates orbit geometry, identifies post-event passes, and initializes an Evidence Ledger. "
        "Requires authentication via 'X-API-Key' header."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid dates or inconsistent orbit geometry"},
        401: {"model": ErrorResponse, "description": "Missing or invalid API key"},
        404: {"model": ErrorResponse, "description": "Study area or acquisition not found"},
        422: {"model": ErrorResponse, "description": "Missing or malformed request parameters"},
        500: {"model": ErrorResponse, "description": "Server authentication configuration error"},
    },
    dependencies=[Depends(verify_api_key)],
)
def create_investigation(payload: InvestigationCreateRequest):
    """
    Creates an investigation using the selected study area, reference date, and comparison date.
    Returns the assigned unique investigation_id and initial status.
    """
    return investigation_service.create_investigation(payload)


@router.get(
    "/investigations/{investigation_id}",
    response_model=InvestigationDetail,
    summary="Retrieve investigation details and Evidence Ledger",
    description="Returns complete details, satellite metadata, processing status, and traceable Evidence Ledger for an investigation.",
    responses={
        404: {"model": ErrorResponse, "description": "Investigation ID not found in registry"},
        422: {"model": ErrorResponse, "description": "Malformed investigation ID format"},
    },
)
def get_investigation(
    investigation_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Unique investigation identifier (e.g. INV-2026-KER-001)",
    )
):
    """
    Returns investigation details and current evidence status.
    """
    return investigation_service.get_investigation_by_id(investigation_id)


@router.get(
    "/investigations/{investigation_id}/evaluation",
    response_model=EvaluationResponse,
    summary="Retrieve Beat Test evaluation and three-state evidence label",
    description=(
        "Returns the temporal Beat Test results, persistence ratio, valid/excluded acquisition counts, "
        "active confounder flags, and three-state evidence label (Supported, Inconclusive, or Unverified) "
        "as specified in PRD Section 9."
    ),
    responses={
        404: {"model": ErrorResponse, "description": "Investigation ID not found in registry"},
        422: {"model": ErrorResponse, "description": "Malformed investigation ID format"},
    },
)
def get_evaluation(
    investigation_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Unique investigation identifier (e.g. INV-2026-KER-001)",
    )
):
    """
    Returns actual evaluation results and evidence label rationale when available.
    """
    return evidence_service.get_investigation_evaluation(investigation_id)


@router.post(
    "/investigations/{investigation_id}/evaluate",
    response_model=EvaluationResponse,
    summary="Evaluate investigation with Beat Test observations and assign evidence label",
    description=(
        "Applies the Beat Test temporal persistence rules (>= 2/3 repeated detection requirement) and "
        "three-state evidence mapping from PRD Section 9. Updates the Evidence Ledger in persistent JSON storage. "
        "Requires authentication via 'X-API-Key' header."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid evaluation parameters"},
        401: {"model": ErrorResponse, "description": "Missing or invalid API key"},
        404: {"model": ErrorResponse, "description": "Investigation ID not found in registry"},
        422: {"model": ErrorResponse, "description": "Malformed request parameters or investigation ID"},
        500: {"model": ErrorResponse, "description": "Server authentication configuration error"},
    },
    dependencies=[Depends(verify_api_key)],
)
def evaluate_investigation(
    investigation_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Unique investigation identifier (e.g. INV-2026-KER-001)",
    ),
    payload: EvaluationRequest = ...,
):
    """
    Evaluates the investigation with supplied post-event observations and confounder checks.
    Updates the persistent Evidence Ledger and returns the assigned evidence label and reasons.
    """
    return evidence_service.evaluate_investigation(investigation_id, payload)


@router.get(
    "/investigations/{investigation_id}/layers",
    summary="List available map layers for an investigation",
    description="Returns the manifest of supported and available map layers for the specified investigation.",
    responses={
        404: {"model": ErrorResponse, "description": "Investigation ID not found in registry"},
        422: {"model": ErrorResponse, "description": "Malformed investigation ID format"},
    },
)
def list_layers(
    investigation_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Unique investigation identifier (e.g. INV-2026-KER-001)",
    )
):
    """
    Returns available map layers, descriptions, and file status for this investigation.
    """
    return layer_service.list_investigation_layers(investigation_id)


@router.get(
    "/investigations/{investigation_id}/layers/{layer}",
    summary="Serve requested map layer or file asset",
    description=(
        "Serves the requested SAR map layer (e.g. 'change-mask', 'continuous', 'reference', 'comparison') "
        "as a valid GeoJSON or image asset with appropriate content-type headers."
    ),
    responses={
        200: {
            "description": "Map layer asset file stream (GeoJSON, PNG, or GeoTIFF)",
            "content": {
                "application/geo+json": {},
                "application/json": {},
                "image/png": {},
                "image/tiff": {},
            },
        },
        400: {"model": ErrorResponse, "description": "Unsupported layer name or directory traversal attempt"},
        404: {"model": ErrorResponse, "description": "Investigation ID or layer asset not found"},
        422: {"model": ErrorResponse, "description": "Malformed path parameters"},
    },
)
def get_layer(
    investigation_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Unique investigation identifier (e.g. INV-2026-KER-001)",
    ),
    layer: str = Path(
        ...,
        description="Canonical map layer name or alias (e.g. change-mask)",
    ),
):
    """
    Serves the requested map layer for the investigation.
    """
    file_path, media_type = layer_service.get_layer_asset_path(investigation_id, layer)
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=file_path.name,
    )


@router.get(
    "/investigations/{investigation_id}/report",
    response_class=HTMLResponse,
    summary="Generate a printable investigation report",
    description=(
        "Generates an executive, printable HTML report summarizing the Evidence Ledger, "
        "Beat Test results, and data provenance. Includes native browser printing and PDF export capability."
    ),
    responses={
        200: {
            "description": "Printable HTML report stream",
            "content": {"text/html": {}},
        },
        404: {"model": ErrorResponse, "description": "Investigation ID not found in registry"},
        422: {"model": ErrorResponse, "description": "Malformed investigation ID format"},
    },
)
def get_investigation_report(
    investigation_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Unique investigation identifier (e.g. INV-2026-KER-001)",
    )
):
    """
    Generates and serves a self-contained, printable HTML report for the investigation.
    Strictly read-only and idempotent.
    """
    html_content = report_service.generate_html_report(investigation_id)
    return HTMLResponse(content=html_content, status_code=status.HTTP_200_OK)
