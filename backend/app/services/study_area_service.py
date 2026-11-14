"""
Study Area and Satellite Acquisition Service
Reads and serves study area metadata and satellite pass histories.
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

import json
from pathlib import Path
from typing import List

from app.schemas.study_area import StudyArea, Acquisition, AcquisitionsResponse
from app.schemas.errors import AppException

# Resolve path to backend/data directory
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STUDY_AREAS_FILE = DATA_DIR / "study_areas.json"
ACQUISITIONS_FILE = DATA_DIR / "acquisitions.json"


def get_all_study_areas() -> List[StudyArea]:
    """
    Load and return all available study areas from data storage.
    """
    if not STUDY_AREAS_FILE.exists():
        return []
    with open(STUDY_AREAS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [StudyArea(**item) for item in data]


def get_study_area_by_id(study_area_id: str) -> StudyArea:
    """
    Find a specific study area by its ID or raise a standardized 404 AppException.
    """
    study_areas = get_all_study_areas()
    for area in study_areas:
        if area.id == study_area_id:
            return area

    raise AppException(
        status_code=404,
        code="STUDY_AREA_NOT_FOUND",
        message=f"Study area '{study_area_id}' was not found in the platform registry.",
        suggested_action="Use GET /api/study-areas to review the list of available monitored study areas.",
    )


def get_acquisitions_for_study_area(study_area_id: str) -> AcquisitionsResponse:
    """
    Retrieve satellite acquisition passes for a given study area.
    """
    # 1. Verify that the study area actually exists
    study_area = get_study_area_by_id(study_area_id)

    # 2. Check that the data file is available
    if not ACQUISITIONS_FILE.exists():
        raise AppException(
            status_code=500,
            code="ACQUISITIONS_STORAGE_ERROR",
            message="The acquisitions data store could not be located.",
            suggested_action="Verify that backend/data/acquisitions.json is populated.",
        )

    with open(ACQUISITIONS_FILE, "r", encoding="utf-8") as f:
        acquisitions_map = json.load(f)

    # 3. Check if this study area has recorded acquisitions
    if study_area_id not in acquisitions_map:
        raise AppException(
            status_code=404,
            code="ACQUISITIONS_NOT_FOUND",
            message=f"No satellite acquisition records found for study area '{study_area_id}'.",
            suggested_action="Check if satellite passes have been ingested for this study area.",
        )

    entry = acquisitions_map[study_area_id]
    acquisitions = [Acquisition(**acq) for acq in entry.get("acquisitions", [])]
    valid_count = sum(1 for a in acquisitions if a.valid)

    return AcquisitionsResponse(
        study_area_id=study_area.id,
        study_area_name=study_area.name,
        total_acquisitions=len(acquisitions),
        valid_acquisitions_count=valid_count,
        data_provenance=entry.get("data_provenance", "ILLUSTRATIVE — NOT REAL DATA"),
        acquisitions=acquisitions,
    )

