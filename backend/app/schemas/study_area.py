"""
Pydantic Schemas for Study Areas and Satellite Acquisitions
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class StudyArea(BaseModel):
    """
    Schema representing a geographic Study Area monitored by BHnMISnTRA.
    """
    id: str = Field(..., description="Unique slug identifier (e.g. 'kerala-floods-2018')")
    name: str = Field(..., description="Human-readable title of the study area")
    description: str = Field(..., description="Contextual summary of the geographic region and event")
    bounding_box: List[float] = Field(
        ...,
        description="Bounding box [min_lon, min_lat, max_lon, max_lat] in WGS84 coordinates",
        min_length=4,
        max_length=4,
    )
    crs: str = Field("EPSG:4326", description="Coordinate Reference System")
    phenomenon_type: str = Field(..., description="Physical phenomenon: 'flood', 'clearing', or 'landslide'")
    expected_behavior: str = Field(..., description="Expected temporal evolution: 'receding' or 'sustained'")
    data_tier: str = Field("Tier 1 (Core)", description="Data tier: Core or Extended")
    data_provenance: str = Field("ILLUSTRATIVE — NOT REAL DATA", description="Provenance tag: REAL, PREPARED, or ILLUSTRATIVE")
    default_reference_date: str = Field(..., description="Recommended pre-event baseline date (YYYY-MM-DD)")
    default_comparison_date: str = Field(..., description="Recommended event peak / comparison date (YYYY-MM-DD)")


class Acquisition(BaseModel):
    """
    Schema representing an individual SAR satellite acquisition pass.
    """
    acquisition_id: str = Field(..., description="Full satellite product identifier")
    date: str = Field(..., description="Acquisition date (YYYY-MM-DD)")
    datetime: str = Field(..., description="Full ISO-8601 acquisition timestamp")
    mission: str = Field("Sentinel-1A", description="Satellite mission name")
    sensor: str = Field("C-SAR", description="Instrument type")
    mode: str = Field("IW", description="Acquisition mode, e.g. Interferometric Wide (IW)")
    polarization: List[str] = Field(default=["VV", "VH"], description="Radar polarization channels")
    orbit_direction: str = Field(..., description="Orbit direction: 'ASCENDING' or 'DESCENDING'")
    track: int = Field(..., description="Relative orbit track number")
    valid: bool = Field(True, description="Whether this acquisition is usable for the Beat Test")
    exclusion_reason: Optional[str] = Field(None, description="Reason if excluded from temporal series")
    data_provenance: str = Field("ILLUSTRATIVE — NOT REAL DATA", description="Provenance classification")


class AcquisitionsResponse(BaseModel):
    """
    Wrapper response containing all satellite passes for a study area.
    """
    study_area_id: str
    study_area_name: str
    total_acquisitions: int
    valid_acquisitions_count: int
    data_provenance: str = "ILLUSTRATIVE — NOT REAL DATA"
    acquisitions: List[Acquisition]

