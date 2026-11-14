"""
Evidence Ledger API Routes
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

from fastapi import APIRouter, Path
from fastapi.responses import FileResponse

from app.schemas.investigation import EvidenceLedgerRecord
from app.schemas.errors import ErrorResponse
from app.services import ledger_service

router = APIRouter(prefix="/investigations", tags=["Evidence Ledger Operations"])

# Standard boundary validation regex for safe path parameters (SEC-05)
ID_PATTERN = r"^[A-Za-z0-9_-]+$"


@router.get(
    "/{investigation_id}/ledger",
    response_model=EvidenceLedgerRecord,
    summary="Retrieve complete Evidence Ledger JSON",
    description=(
        "Returns the complete, traceable Evidence Ledger record for a specific investigation, "
        "including all satellite provenance, acquisition IDs, processing parameters, and uncertainty rationale."
    ),
    responses={
        404: {"model": ErrorResponse, "description": "Investigation ID not found in registry"},
        422: {"model": ErrorResponse, "description": "Malformed investigation ID format"},
    },
)
def get_investigation_ledger(
    investigation_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Unique investigation identifier (e.g. INV-2026-KER-001)",
    )
):
    """
    Returns the complete Evidence Ledger JSON for the specified investigation.
    """
    return ledger_service.get_ledger_by_investigation_id(investigation_id)


@router.get(
    "/{investigation_id}/ledger/download",
    summary="Download Evidence Ledger as a JSON file",
    description=(
        "Downloads the complete Evidence Ledger as a standalone .json file with "
        "appropriate attachment headers and filename ('evidence-ledger-{id}.json')."
    ),
    responses={
        200: {
            "content": {"application/json": {}},
            "description": "Evidence Ledger JSON file stream",
        },
        404: {"model": ErrorResponse, "description": "Investigation ID not found in registry"},
        422: {"model": ErrorResponse, "description": "Malformed investigation ID format"},
    },
)
def download_investigation_ledger(
    investigation_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Unique investigation identifier (e.g. INV-2026-KER-001)",
    )
):
    """
    Downloads the ledger as a valid JSON file.
    """
    file_path, filename = ledger_service.get_ledger_file_for_download(investigation_id)
    return FileResponse(
        path=str(file_path),
        media_type="application/json",
        filename=filename,
    )
