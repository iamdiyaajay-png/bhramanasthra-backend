"""
Pydantic Schemas for Investigation Creation, Retrieval, and Evidence Ledger
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.study_area import StudyArea, Acquisition


class InvestigationCreateRequest(BaseModel):
    """
    Request payload to initialize a new surface change investigation.
    """
    study_area_id: str = Field(..., description="ID of the monitored study area (e.g. 'kerala-floods-2018')")
    reference_date: str = Field(
        ...,
        description="Pre-event baseline satellite acquisition date (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    comparison_date: str = Field(
        ...,
        description="Event peak / post-event satellite acquisition date (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class InvestigationCreateResponse(BaseModel):
    """
    Response returned immediately after an investigation is registered.
    """
    investigation_id: str = Field(..., description="Unique investigation identifier (e.g. 'INV-2026-KER-001')")
    status: str = Field(..., description="Initial investigation status (e.g. 'CREATED')")
    study_area_id: str
    study_area_name: str
    reference_date: str
    comparison_date: str
    created_at: str
    message: str


class EvidenceLedgerRecord(BaseModel):
    """
    Comprehensive, traceable Evidence Ledger record as specified in PRD Section 13.
    Captures complete provenance, orbit geometry, parameters, and uncertainty rationale.
    """
    investigation_id: str
    study_area_id: str
    study_area_name: str
    bounding_box: List[float]
    crs: str
    phenomenon_type: str
    expected_behavior: str
    data_tier: str
    data_source: str
    data_provenance: str = "ILLUSTRATIVE — NOT REAL DATA"
    satellite_mission: str
    sensor: str
    mode: str
    polarization: List[str]
    orbit_direction: str
    track: int
    reference_acquisition_id: Optional[str] = None
    reference_acquisition_date: str
    comparison_acquisition_id: Optional[str] = None
    comparison_acquisition_date: str
    later_acquisition_dates: List[str] = []
    valid_later_acquisitions_count: int = 0
    detected_later_acquisitions_count: int = 0
    excluded_acquisitions: List[Dict[str, Any]] = []
    processing_method: str
    processing_parameters: Dict[str, Any]
    change_detection_status: str = "PENDING"
    changed_area_sq_km: Optional[float] = None
    layer_references: Optional[List[str]] = None
    beat_test_status: str = "NOT_YET_PROCESSED"
    beat_test_result: str = "NOT_AVAILABLE"
    persistence_result: str = "NOT_AVAILABLE"
    confounder_flags: List[str] = []
    evidence_label: str = "Unverified"
    reasons_for_label: List[str] = []
    independent_reference: Optional[Dict[str, Any]] = None
    verification_status: str = "UNVERIFIED"
    known_limitations: List[str] = []
    reproduce_command: str
    configuration_hash: str
    environment: Dict[str, Any]
    evaluation_notes: Optional[str] = None
    created_at: str


class InvestigationDetail(BaseModel):
    """
    Full response model for GET /api/investigations/{investigation_id}.
    """
    investigation_id: str
    status: str
    created_at: str
    study_area: StudyArea
    reference_date: str
    comparison_date: str
    reference_acquisition: Optional[Acquisition] = None
    comparison_acquisition: Optional[Acquisition] = None
    later_acquisitions: List[Acquisition] = []
    valid_later_acquisitions_count: int
    evidence_ledger: EvidenceLedgerRecord
    processing_status: Dict[str, str]
    data_provenance: str = "ILLUSTRATIVE — NOT REAL DATA"

