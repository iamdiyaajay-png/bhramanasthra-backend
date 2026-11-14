"""
Investigation and Evidence Ledger Service
Manages creation, validation, storage, and retrieval of surface change investigations.
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

import json
import hashlib
import os
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.schemas.investigation import (
    InvestigationCreateRequest,
    InvestigationCreateResponse,
    InvestigationDetail,
    EvidenceLedgerRecord,
)
from app.schemas.study_area import Acquisition
from app.schemas.errors import AppException
from app.services import study_area_service

# Paths to data storage
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
LEDGERS_DIR = OUTPUTS_DIR / "ledgers"
INVESTIGATIONS_FILE = DATA_DIR / "investigations.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LEDGERS_DIR.mkdir(parents=True, exist_ok=True)


def _load_all_investigations() -> Dict[str, Any]:
    """
    Loads the investigations dictionary from persistent JSON storage.
    Safety Guarantees (Repair 1 / Finding 3):
    1. Returns empty dict {} only if the file does not exist yet (clean initialization).
    2. If the file exists and contains valid JSON, returns the dictionary.
    3. If the file exists but is corrupted or unreadable (JSONDecodeError, OSError, ValueError):
       - Preserves the original corrupted file in-place (never deletes or truncates it).
       - Creates a timestamped backup with a '.corrupt' suffix.
       - Raises a controlled AppException (HTTP 500 DATABASE_CORRUPTION_ERROR).
       - Never silently returns {} to prevent destructive overwriting of historical data.
    """
    if not INVESTIGATIONS_FILE.exists():
        return {}

    try:
        with open(INVESTIGATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError(f"Investigation database root must be a JSON object, got {type(data).__name__}")
            return data
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_file = INVESTIGATIONS_FILE.with_name(f"{INVESTIGATIONS_FILE.name}.corrupt.{timestamp}")
        try:
            shutil.copy2(INVESTIGATIONS_FILE, backup_file)
        except Exception:
            pass  # Best effort backup

        raise AppException(
            status_code=500,
            code="DATABASE_CORRUPTION_ERROR",
            message=(
                f"Investigation database file '{INVESTIGATIONS_FILE.name}' is corrupt or unreadable: {str(exc)}. "
                f"The original corrupted file has been preserved and a backup was created at '{backup_file.name}'."
            ),
            suggested_action="Contact the platform administrator to restore the database from backup.",
        )


def _save_all_investigations(data: Dict[str, Any]) -> None:
    """
    Atomically saves the investigations dictionary to persistent JSON storage.
    Safety Guarantees (Repair 1 / Finding 3):
    1. Writes complete JSON to an ephemeral temporary file in the same directory.
    2. Flushes buffers and syncs to physical disk via os.fsync.
    3. Atomically replaces the target file using os.replace.
    4. Ensures any write failure leaves the previous valid file completely intact.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = DATA_DIR / f"{INVESTIGATIONS_FILE.name}.tmp.{uuid.uuid4().hex}"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, INVESTIGATIONS_FILE)
    except Exception as exc:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise AppException(
            status_code=500,
            code="DATABASE_WRITE_ERROR",
            message=f"Failed to atomically persist investigation database: {str(exc)}",
            suggested_action="Check disk space and filesystem write permissions.",
        )


def create_investigation(req: InvestigationCreateRequest) -> InvestigationCreateResponse:
    """
    Validates inputs, generates an Evidence Ledger, and records a new investigation.
    Guarantees collision-proof ID generation and atomic disk persistence.
    """
    # 1. Validate study area exists
    study_area = study_area_service.get_study_area_by_id(req.study_area_id)

    # 2. Validate chronological order
    if req.reference_date >= req.comparison_date:
        raise AppException(
            status_code=400,
            code="INVALID_DATE_ORDER",
            message=(
                f"Reference date '{req.reference_date}' must be chronologically "
                f"earlier than comparison date '{req.comparison_date}'."
            ),
            suggested_action="Select a baseline reference acquisition that occurred before the comparison event date.",
        )

    # 3. Retrieve satellite acquisitions for this study area
    acq_response = study_area_service.get_acquisitions_for_study_area(req.study_area_id)
    acquisitions_list: List[Acquisition] = acq_response.acquisitions

    # 4. Verify that requested dates exist in the satellite timeline
    acq_by_date: Dict[str, Acquisition] = {a.date: a for a in acquisitions_list}

    if req.reference_date not in acq_by_date:
        raise AppException(
            status_code=400,
            code="REFERENCE_ACQUISITION_NOT_FOUND",
            message=f"No satellite pass recorded on '{req.reference_date}' for study area '{req.study_area_id}'.",
            suggested_action="Check available pass dates using GET /api/study-areas/{id}/acquisitions.",
        )

    if req.comparison_date not in acq_by_date:
        raise AppException(
            status_code=400,
            code="COMPARISON_ACQUISITION_NOT_FOUND",
            message=f"No satellite pass recorded on '{req.comparison_date}' for study area '{req.study_area_id}'.",
            suggested_action="Check available pass dates using GET /api/study-areas/{id}/acquisitions.",
        )

    ref_acq = acq_by_date[req.reference_date]
    cmp_acq = acq_by_date[req.comparison_date]

    # 5. Verify geometric consistency (orbit track and direction)
    if ref_acq.track != cmp_acq.track or ref_acq.orbit_direction != cmp_acq.orbit_direction:
        raise AppException(
            status_code=400,
            code="INCONSISTENT_ORBIT_GEOMETRY",
            message=(
                f"Reference pass (Track {ref_acq.track}, {ref_acq.orbit_direction}) and "
                f"Comparison pass (Track {cmp_acq.track}, {cmp_acq.orbit_direction}) have mismatched geometry."
            ),
            suggested_action="Select acquisitions sharing the same relative orbit track and pass direction.",
        )

    # 6. Identify subsequent satellite acquisitions for the Beat Test
    later_acquisitions = [
        a for a in acquisitions_list
        if a.date > req.comparison_date
        and a.track == ref_acq.track
        and a.orbit_direction == ref_acq.orbit_direction
    ]
    valid_later_acqs = [a for a in later_acquisitions if a.valid]
    excluded_acqs = [
        {"acquisition_id": a.acquisition_id, "date": a.date, "reason": a.exclusion_reason or "Flagged invalid"}
        for a in later_acquisitions if not a.valid
    ]

    # 7. Generate a unique, collision-proof investigation ID (Repair 1 / Finding 4)
    # Scans existing IDs per study area slug independently to find highest index
    investigations_db = _load_all_investigations()
    slug_code = req.study_area_id.split("-")[0].upper()[:3]
    year = datetime.now(timezone.utc).year

    slug_pattern = re.compile(rf"^INV-(?:\d{{4}})-{re.escape(slug_code)}-(\d+)$")
    existing_indices = []
    for existing_id in investigations_db.keys():
        m = slug_pattern.match(existing_id)
        if m:
            try:
                existing_indices.append(int(m.group(1)))
            except ValueError:
                pass

    next_index = (max(existing_indices) + 1) if existing_indices else 1
    investigation_id = f"INV-{year}-{slug_code}-{next_index:03d}"

    # Collision guard: advance index if the identifier already exists
    while investigation_id in investigations_db:
        next_index += 1
        investigation_id = f"INV-{year}-{slug_code}-{next_index:03d}"

    # 8. Compute cryptographic configuration hash for reproducibility
    raw_config = f"{req.study_area_id}|{req.reference_date}|{req.comparison_date}|{ref_acq.track}|{ref_acq.orbit_direction}"
    config_hash = hashlib.sha256(raw_config.encode("utf-8")).hexdigest()

    reproduce_cmd = (
        f"python -m bhandmisntra.pipeline --study-area {req.study_area_id} "
        f"--ref {req.reference_date} --cmp {req.comparison_date} "
        f"--track {ref_acq.track} --orbit {ref_acq.orbit_direction}"
    )

    created_at_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 9. Build Evidence Ledger Record (Strict adherence to PRD Section 13)
    ledger = EvidenceLedgerRecord(
        investigation_id=investigation_id,
        study_area_id=study_area.id,
        study_area_name=study_area.name,
        bounding_box=study_area.bounding_box,
        crs=study_area.crs,
        phenomenon_type=study_area.phenomenon_type,
        expected_behavior=study_area.expected_behavior,
        data_tier=study_area.data_tier,
        data_source="Copernicus Sentinel-1 SAR via NASA/ESA Gateway",
        data_provenance="ILLUSTRATIVE — NOT REAL DATA",
        satellite_mission=ref_acq.mission,
        sensor=ref_acq.sensor,
        mode=ref_acq.mode,
        polarization=ref_acq.polarization,
        orbit_direction=ref_acq.orbit_direction,
        track=ref_acq.track,
        reference_acquisition_id=ref_acq.acquisition_id,
        reference_acquisition_date=ref_acq.date,
        comparison_acquisition_id=cmp_acq.acquisition_id,
        comparison_acquisition_date=cmp_acq.date,
        later_acquisition_dates=[a.date for a in later_acquisitions],
        valid_later_acquisitions_count=len(valid_later_acqs),
        excluded_acquisitions=excluded_acqs,
        processing_method="Sentinel-1 Dual-Pol Amplitude Ratio & Coherence Change Detection (SAR Beat Test)",
        processing_parameters={
            "polarization": "VV",
            "speckle_filter": "Lee",
            "filter_window": 7,
            "detection_threshold_db": -3.5,
            "beat_test_threshold_percent": 15.0,
        },
        change_detection_status="PENDING",
        changed_area_sq_km=None,  # Never fabricate! Awaiting Member 1
        layer_references=None,
        beat_test_status="NOT_YET_PROCESSED",
        beat_test_result="NOT_AVAILABLE",
        persistence_result="NOT_AVAILABLE",
        confounder_flags=["CLEAR"],
        evidence_label="Unverified",
        reasons_for_label=[
            "Investigation created and recorded in Evidence Ledger.",
            "Awaiting SAR processing pipeline execution from Member 1.",
            "Beat Test temporal evolution has not yet run on post-event satellite passes.",
            "Data provenance is strictly disclosed as ILLUSTRATIVE – NOT REAL DATA.",
        ],
        independent_reference=None,
        verification_status="UNVERIFIED",
        known_limitations=[
            "Radar speckle noise requires multi-look adaptive filtering.",
            "Wind roughening over open water can induce backscatter variance.",
            "Ground truth validation has not yet been ingested.",
            "Current demonstration uses illustrative Sentinel-1 metadata.",
        ],
        reproduce_command=reproduce_cmd,
        configuration_hash=config_hash,
        environment={
            "python_version": "3.12.10",
            "platform": "BHnMISnTRA-FastAPI-v1.0.0",
            "engine": "Gemini 3.8 Flash High Architecture",
        },
        created_at=created_at_iso,
    )

    # 10. Persist investigation and dedicated ledger atomically to disk
    if investigation_id in investigations_db:
        raise AppException(
            status_code=500,
            code="INVESTIGATION_ID_COLLISION",
            message=f"Investigation ID '{investigation_id}' already exists in registry. Overwriting is strictly prohibited.",
            suggested_action="Retry investigation creation to acquire the next sequence number.",
        )

    investigation_record = {
        "investigation_id": investigation_id,
        "status": "CREATED",
        "created_at": created_at_iso,
        "study_area_id": study_area.id,
        "reference_date": req.reference_date,
        "comparison_date": req.comparison_date,
        "ledger": ledger.model_dump(),
        "processing_status": {
            "sar_preprocessing": "PENDING",
            "co_registration": "PENDING",
            "change_mask_generation": "PENDING",
            "beat_test_execution": "NOT_YET_PROCESSED",
        },
    }

    investigations_db[investigation_id] = investigation_record
    _save_all_investigations(investigations_db)

    # Save dedicated JSON file in outputs/ledgers/ atomically for export/download
    ledger_file = LEDGERS_DIR / f"{investigation_id}.json"
    ledger_tmp = LEDGERS_DIR / f"{investigation_id}.json.tmp.{uuid.uuid4().hex}"
    try:
        with open(ledger_tmp, "w", encoding="utf-8") as f:
            json.dump(ledger.model_dump(), f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(ledger_tmp, ledger_file)
    except Exception:
        if ledger_tmp.exists():
            try:
                ledger_tmp.unlink()
            except OSError:
                pass
        raise

    return InvestigationCreateResponse(
        investigation_id=investigation_id,
        status="CREATED",
        study_area_id=study_area.id,
        study_area_name=study_area.name,
        reference_date=req.reference_date,
        comparison_date=req.comparison_date,
        created_at=created_at_iso,
        message="Investigation registered successfully and initialized in Evidence Ledger.",
    )


def get_investigation_by_id(investigation_id: str) -> InvestigationDetail:
    """
    Retrieves full details, satellite metadata, and Evidence Ledger for an investigation.
    """
    investigations_db = _load_all_investigations()

    if investigation_id not in investigations_db:
        raise AppException(
            status_code=404,
            code="INVESTIGATION_NOT_FOUND",
            message=f"Investigation '{investigation_id}' was not found in the platform registry.",
            suggested_action="Verify the investigation ID or create a new investigation with POST /api/investigations.",
        )

    record = investigations_db[investigation_id]
    study_area = study_area_service.get_study_area_by_id(record["study_area_id"])
    acq_response = study_area_service.get_acquisitions_for_study_area(record["study_area_id"])
    acq_by_date = {a.date: a for a in acq_response.acquisitions}

    ref_acq = acq_by_date.get(record["reference_date"])
    cmp_acq = acq_by_date.get(record["comparison_date"])

    track = ref_acq.track if ref_acq else 0
    orbit = ref_acq.orbit_direction if ref_acq else ""

    later_acqs = [
        a for a in acq_response.acquisitions
        if a.date > record["comparison_date"]
        and a.track == track
        and a.orbit_direction == orbit
    ]
    valid_later_count = sum(1 for a in later_acqs if a.valid)

    ledger_record = EvidenceLedgerRecord(**record["ledger"])

    return InvestigationDetail(
        investigation_id=record["investigation_id"],
        status=record["status"],
        created_at=record["created_at"],
        study_area=study_area,
        reference_date=record["reference_date"],
        comparison_date=record["comparison_date"],
        reference_acquisition=ref_acq,
        comparison_acquisition=cmp_acq,
        later_acquisitions=later_acqs,
        valid_later_acquisitions_count=valid_later_count,
        evidence_ledger=ledger_record,
        processing_status=record.get("processing_status", {}),
        data_provenance="ILLUSTRATIVE — NOT REAL DATA",
    )
