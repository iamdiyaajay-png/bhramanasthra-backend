"""
Study Area and Satellite Acquisition API Routes
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

from typing import List
from fastapi import APIRouter, Path

from app.schemas.study_area import StudyArea, AcquisitionsResponse
from app.schemas.errors import ErrorResponse
from app.services import study_area_service

router = APIRouter(tags=["Study Areas & Satellite Data"])

# Standard boundary validation regex for safe path parameters (SEC-05)
ID_PATTERN = r"^[A-Za-z0-9_-]+$"


@router.get(
    "/study-areas",
    response_model=List[StudyArea],
    summary="List available study areas",
    description="Returns all geographic study areas monitored by BHnMISnTRA with bounding boxes and default dates.",
)
def list_study_areas():
    """
    Returns available study areas.
    Used by Member 3 (Frontend) to populate the study area selector dropdown and map boundaries.
    """
    return study_area_service.get_all_study_areas()


@router.get(
    "/study-areas/{study_area_id}",
    response_model=StudyArea,
    summary="Get single study area details",
    description="Returns detailed metadata, bounding box, and CRS for a specific study area.",
    responses={
        404: {"model": ErrorResponse, "description": "Study area not found"},
        422: {"model": ErrorResponse, "description": "Malformed study area ID format"},
    },
)
def get_study_area(
    study_area_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Study area identifier (e.g. kerala-flood-2024)",
    )
):
    """
    Returns details for a single study area.
    """
    return study_area_service.get_study_area_by_id(study_area_id)


@router.get(
    "/study-areas/{study_area_id}/acquisitions",
    response_model=AcquisitionsResponse,
    summary="Get satellite acquisition timeline",
    description="Returns Sentinel-1 SAR acquisition dates, orbit directions, and tracks for a study area.",
    responses={
        404: {"model": ErrorResponse, "description": "Study area not found"},
        422: {"model": ErrorResponse, "description": "Malformed study area ID format"},
    },
)
def get_study_area_acquisitions(
    study_area_id: str = Path(
        ...,
        pattern=ID_PATTERN,
        description="Study area identifier (e.g. kerala-flood-2024)",
    )
):
    """
    Returns satellite acquisition dates and metadata for a study area.
    Used by Member 3 (Frontend) to display the timeline and let the user select reference and comparison dates.
    """
    return study_area_service.get_acquisitions_for_study_area(study_area_id)
