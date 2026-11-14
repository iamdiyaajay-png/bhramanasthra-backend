"""
Pydantic Schemas for Beat Test Evaluation and Three-State Evidence Labeling
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
PRD Section 9: Three-State Evidence Label Logic & Temporal Evaluation Rules
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ObservationItem(BaseModel):
    """
    Individual post-event satellite acquisition observation for the Beat Test.
    """
    acquisition_id: str = Field(..., description="Unique satellite acquisition identifier")
    date: str = Field(..., description="Acquisition date (YYYY-MM-DD)")
    valid: bool = Field(True, description="Whether the satellite pass is valid for scientific evaluation")
    exclusion_reason: Optional[str] = Field(None, description="Reason if excluded (e.g. noise, track mismatch)")
    change_detected: bool = Field(False, description="Whether the surface change signal was detected in this pass")


class EvaluationRequest(BaseModel):
    """
    Request payload to trigger or update an investigation's Beat Test evaluation.
    Allows Member 1's scientific pipeline to submit observation passes and confounder checks.
    """
    observations: Optional[List[ObservationItem]] = Field(
        None,
        description="List of post-event observation passes. If omitted, uses available study area passes.",
    )
    confounder_flags: Optional[List[str]] = Field(
        None,
        description="List of confounder flags (e.g. ['CLEAR'] or ['FLAGGED: Severe ionospheric scintillation'])",
    )
    changed_area_sq_km: Optional[float] = Field(
        None,
        ge=0.0,
        description="Measured changed surface area in square kilometers from Member 1's pipeline (must be non-negative)",
    )
    notes: Optional[str] = Field(
        None,
        description="Operational or scientific notes from pipeline execution",
    )


class EvaluationResponse(BaseModel):
    """
    Standardized response model for GET & POST /api/investigations/{id}/evaluation.
    Complies strictly with PRD Section 9 and Section 13 Evidence Ledger requirements.
    """
    investigation_id: str
    evidence_label: str = Field(
        ...,
        description="Three-state label: 'Supported', 'Inconclusive', or 'Unverified'",
    )
    verification_status: str
    beat_test_status: str
    beat_test_result: str = Field(
        ...,
        description="Temporal result: 'matches', 'does_not_match', 'insufficient', or 'NOT_AVAILABLE'",
    )
    valid_observations_count: int = Field(..., description="Count of valid post-event passes evaluated")
    detected_observations_count: int = Field(..., description="Count of valid passes where change was detected")
    persistence_ratio: Optional[float] = Field(
        None,
        description="Detection ratio (detected / valid). None if insufficient observations.",
    )
    persistence_threshold: float = Field(
        0.667,
        description="Required persistence threshold (2/3 = 66.7%) from PRD Section 9",
    )
    meets_persistence_threshold: bool
    excluded_acquisitions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Excluded passes with documented exclusion reasons (never counted in persistence)",
    )
    confounder_flags: List[str] = Field(
        default_factory=list,
        description="Active confounder flags",
    )
    confounders_clear: bool
    reasons_for_label: List[str] = Field(
        ...,
        description="Understandable, evidence-backed reasons justifying the assigned label",
    )
    changed_area_sq_km: Optional[float] = Field(
        None,
        description="Measured changed surface area in square kilometers",
    )
    notes: Optional[str] = Field(
        None,
        description="Operational or scientific notes from pipeline execution",
    )
    data_provenance: str = "ILLUSTRATIVE — NOT REAL DATA"
