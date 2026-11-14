"""
Evidence Labeling and Beat Test Service
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
Implements PRD Section 9: Three-State Evidence Label Logic & Beat Test Temporal Evaluation
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from app.schemas.investigation import EvidenceLedgerRecord
from app.schemas.evaluation import ObservationItem, EvaluationRequest, EvaluationResponse
from app.schemas.errors import AppException
from app.services import study_area_service
from app.services.investigation_service import (
    _load_all_investigations,
    _save_all_investigations,
    LEDGERS_DIR,
)

# PRD Section 9 Threshold Constants
MIN_VALID_LATER_ACQUISITIONS = 3
PERSISTENCE_THRESHOLD_RATIO = 2.0 / 3.0  # 66.67%


def evaluate_beat_test(
    observations: List[ObservationItem],
    expected_behavior: str = "sustained",
) -> Tuple[str, int, int, Optional[float], bool, List[Dict[str, Any]]]:
    """
    Evaluates temporal persistence or recession across post-event satellite acquisitions (PRD Section 9).

    Rules:
    1. Excludes invalid acquisitions from the valid count and records their reasons.
       Excluded acquisitions MUST NEVER be counted as evidence of persistence or disappearance.
    2. Requires at least 3 valid later acquisitions for evaluation.
       Fewer than 3 yields temporal_result = 'insufficient'.
    3. Phenomenon-Specific Temporal Rules (Repair 2 / Finding 2):
       - Sustained phenomena (e.g. landslides):
         Requires repeated change detection in at least 2/3 (66.7%) of valid later passes
         (temporal_result = 'matches'). Otherwise temporal_result = 'does_not_match'.
       - Receding phenomena (e.g. receding flood inundation):
         A receding flood is expected to recede in subsequent passes.
         * If change persists across ALL valid acquisitions (100% continuous persistence),
           recession did NOT occur, so temporal_result = 'does_not_match'. (Prevents incorrectly
           labelling a non-receding flood as Supported merely because changes persist).
         * If initial change is confirmed (detected in >= 2/3 of passes) AND recession is observed
           in subsequent acquisitions (i.e. detected_count < valid_count and latest pass receded),
           temporal_result = 'matches'.
         * If detected in < 2/3 passes, temporal_result = 'does_not_match'.

    Returns:
        (temporal_result, valid_count, detected_count, persistence_ratio, meets_threshold, excluded_acqs)
    """
    valid_observations: List[ObservationItem] = []
    excluded_acqs: List[Dict[str, Any]] = []

    for obs in observations:
        if obs.valid:
            valid_observations.append(obs)
        else:
            reason = obs.exclusion_reason or "Flagged invalid acquisition"
            excluded_acqs.append({
                "acquisition_id": obs.acquisition_id,
                "date": obs.date,
                "reason": reason,
            })

    valid_count = len(valid_observations)

    # Threshold Check: At least 3 valid later acquisitions required
    if valid_count < MIN_VALID_LATER_ACQUISITIONS:
        return ("insufficient", valid_count, 0, None, False, excluded_acqs)

    # Sort valid observations chronologically by date
    valid_observations.sort(key=lambda o: o.date)

    detected_count = sum(1 for obs in valid_observations if obs.change_detected)
    ratio = detected_count / valid_count
    behavior = expected_behavior.strip().lower() if expected_behavior else "sustained"

    if behavior == "receding":
        # Receding phenomenon rules:
        # 1. If change persists across all acquisitions (100%), no recession occurred
        if detected_count == valid_count:
            meets_threshold = False
            temporal_result = "does_not_match"
        # 2. Significant detection in initial monitoring (>= 66.7%) followed by recession in later observation
        elif ratio >= (PERSISTENCE_THRESHOLD_RATIO - 1e-6) and not valid_observations[-1].change_detected:
            meets_threshold = True
            temporal_result = "matches"
        else:
            meets_threshold = False
            temporal_result = "does_not_match"
    else:
        # Sustained phenomenon rules (PRD Section 9 standard persistence ratio):
        meets_threshold = ratio >= (PERSISTENCE_THRESHOLD_RATIO - 1e-6)
        if meets_threshold:
            temporal_result = "matches"
        else:
            temporal_result = "does_not_match"

    return (temporal_result, valid_count, detected_count, round(ratio, 4), meets_threshold, excluded_acqs)


def map_evidence_label(
    temporal_result: str,
    confounder_flags: List[str],
    valid_count: int,
    detected_count: int,
    ratio: Optional[float],
    excluded_acqs: List[Dict[str, Any]],
    expected_behavior: str = "sustained",
) -> Tuple[str, str, List[str]]:
    """
    Maps Beat Test temporal results and confounder checks to one of the 3 evidence states:
      - Supported
      - Inconclusive
      - Unverified

    Rules (PRD Section 9):
    1. Supported:
       Temporal result = 'matches' AND Confounder flag = 'Clear' AND valid_count >= 3.
    2. Inconclusive:
       valid_count >= 3 AND (Temporal result = 'does_not_match' OR Confounder flag = 'Flagged').
    3. Unverified:
       valid_count < 3, or no same-geometry series available.
       *Never label a region Supported if there are fewer than 3 valid later acquisitions.*
       *Reference agreement must NOT determine the evidence label.*

    Returns:
        (evidence_label, verification_status, reasons_for_label)
    """
    reasons: List[str] = []
    behavior = expected_behavior.strip().lower() if expected_behavior else "sustained"

    # Check confounders status
    flagged_confounders = [
        f for f in confounder_flags
        if f.upper().startswith("FLAGGED") or (f.upper() != "CLEAR" and f.strip() != "")
    ]
    confounders_clear = len(flagged_confounders) == 0

    # 1. UNVERIFIED: Fewer than 3 valid later acquisitions
    if valid_count < MIN_VALID_LATER_ACQUISITIONS:
        label = "Unverified"
        verification_status = "UNVERIFIED"
        reasons.append(
            f"Fewer than 3 valid later satellite acquisitions available for Beat Test evaluation "
            f"(found {valid_count}, required at least {MIN_VALID_LATER_ACQUISITIONS})."
        )
        reasons.append(
            "Temporal persistence or recession cannot be confirmed with an insufficient post-event observation series."
        )
        if excluded_acqs:
            reasons.append(
                f"{len(excluded_acqs)} acquisition(s) excluded due to data quality or orbit geometry constraints "
                f"and omitted from observation counts."
            )
        reasons.append(
            "PRD Section 9 strictly forbids assigning 'Supported' status without at least 3 valid later acquisitions."
        )
        return (label, verification_status, reasons)

    # 2. SUPPORTED: Temporal matches expected AND confounders clear AND valid passes >= 3
    if temporal_result == "matches" and confounders_clear:
        label = "Supported"
        verification_status = "SUPPORTED"
        reasons.append(
            f"Sufficient post-event observations available: {valid_count} valid satellite acquisitions "
            f"evaluated (minimum required: {MIN_VALID_LATER_ACQUISITIONS})."
        )
        if behavior == "receding":
            reasons.append(
                f"Beat Test passed for receding phenomenon: initial surface change detected in {detected_count}/{valid_count} "
                f"valid passes ({ratio:.1%}) followed by documented recession in subsequent acquisitions."
            )
        else:
            reasons.append(
                f"Beat Test repeated-detection requirement satisfied: change detected in {detected_count}/{valid_count} "
                f"valid passes ({ratio:.1%}), meeting the >= 66.7% persistence threshold."
            )
        reasons.append(
            "Confounder check clear: no severe weather, ionospheric noise, or steep topographic distortion flagged."
        )
        if excluded_acqs:
            reasons.append(
                f"{len(excluded_acqs)} acquisition(s) excluded for data quality reasons and excluded from observation counts."
            )
        reasons.append(
            "Independent reference agreement recorded for context but does not determine this evidence label (PRD Section 9)."
        )
        return (label, verification_status, reasons)

    # 3. INCONCLUSIVE: Temporal does not match OR Confounder flagged
    label = "Inconclusive"
    verification_status = "INCONCLUSIVE"
    reasons.append(
        f"Evaluated {valid_count} valid post-event satellite acquisitions (meets sample size requirement >= 3)."
    )

    if temporal_result == "does_not_match":
        if behavior == "receding" and detected_count == valid_count:
            reasons.append(
                f"Expected behavior is 'receding', but surface change persisted across all {detected_count}/{valid_count} "
                f"evaluated passes (100.0%) with no observed recession. Continuous persistence does not support receding flood behavior."
            )
        else:
            pct_str = f"{ratio:.1%}" if ratio is not None else "0.0%"
            reasons.append(
                f"Beat Test temporal requirement not met: change detected in only {detected_count}/{valid_count} "
                f"valid passes ({pct_str}), falling below the required 66.7% threshold."
            )

    if not confounders_clear:
        confounder_details = "; ".join(flagged_confounders)
        reasons.append(
            f"Active confounder(s) flagged: {confounder_details}. "
            f"Environmental or radar artifacts prevent confirming surface change."
        )

    if excluded_acqs:
        reasons.append(
            f"{len(excluded_acqs)} acquisition(s) excluded for data quality reasons and excluded from observation counts."
        )

    reasons.append(
        "Temporal observation behavior does not match expected profile under clear conditions."
    )
    return (label, verification_status, reasons)


def get_investigation_evaluation(investigation_id: str) -> EvaluationResponse:
    """
    Retrieves the current evaluation status and Beat Test results for an investigation.
    Reads directly from persistent storage.
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
    ledger = record.get("ledger", {})

    valid_count = ledger.get("valid_later_acquisitions_count", 0)
    beat_test_result = ledger.get("beat_test_result", "NOT_AVAILABLE")
    beat_test_status = ledger.get("beat_test_status", "NOT_YET_PROCESSED")
    evidence_label = ledger.get("evidence_label", "Unverified")
    verification_status = ledger.get("verification_status", "UNVERIFIED")
    confounder_flags = ledger.get("confounder_flags", ["CLEAR"])
    excluded_acqs = ledger.get("excluded_acquisitions", [])
    reasons = ledger.get("reasons_for_label", [])
    expected_behavior = ledger.get("expected_behavior", "sustained").strip().lower()

    detected_count = ledger.get("detected_later_acquisitions_count", 0)
    ratio = None
    if valid_count > 0 and beat_test_status == "COMPLETED":
        ratio = round(detected_count / valid_count, 4) if valid_count >= MIN_VALID_LATER_ACQUISITIONS else None

    if ratio is not None:
        if expected_behavior == "receding":
            meets_threshold = (ratio >= (PERSISTENCE_THRESHOLD_RATIO - 1e-6)) and (detected_count < valid_count)
        else:
            meets_threshold = ratio >= (PERSISTENCE_THRESHOLD_RATIO - 1e-6)
    else:
        meets_threshold = False

    confounders_clear = not any(
        f.upper().startswith("FLAGGED") or (f.upper() != "CLEAR" and f.strip() != "")
        for f in confounder_flags
    )

    current_notes = ledger.get("evaluation_notes") or record.get("notes")

    return EvaluationResponse(
        investigation_id=investigation_id,
        evidence_label=evidence_label,
        verification_status=verification_status,
        beat_test_status=beat_test_status,
        beat_test_result=beat_test_result,
        valid_observations_count=valid_count,
        detected_observations_count=detected_count,
        persistence_ratio=ratio,
        persistence_threshold=0.667,
        meets_persistence_threshold=meets_threshold,
        excluded_acquisitions=excluded_acqs,
        confounder_flags=confounder_flags,
        confounders_clear=confounders_clear,
        reasons_for_label=reasons,
        changed_area_sq_km=ledger.get("changed_area_sq_km"),
        notes=current_notes,
        data_provenance="ILLUSTRATIVE — NOT REAL DATA",
    )


def evaluate_investigation(
    investigation_id: str,
    req: EvaluationRequest,
) -> EvaluationResponse:
    """
    Executes Beat Test evaluation and three-state label assignment for an investigation.
    Updates the Evidence Ledger in persistent JSON storage.
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
    ledger_data = record.get("ledger", {})
    study_area_id = record.get("study_area_id")
    comparison_date = record.get("comparison_date")

    # Retrieve valid acquisitions for this study area to validate observations (Repair 2 / Finding 5B)
    acq_response = study_area_service.get_acquisitions_for_study_area(study_area_id)
    study_area_acqs = acq_response.acquisitions
    study_area_dates = {a.date for a in study_area_acqs}
    study_area_acq_ids = {a.acquisition_id for a in study_area_acqs}

    # 1. Determine observation passes to evaluate with strict validation
    if req.observations is not None:
        if not req.observations:
            raise AppException(
                status_code=400,
                code="EMPTY_OBSERVATIONS_LIST",
                message="Observations list cannot be empty when explicitly provided.",
                suggested_action="Provide at least 3 post-event satellite observations or omit the field to use study area acquisitions.",
            )

        for obs in req.observations:
            # Rejection 1: Observations dated on or before comparison date
            if obs.date <= comparison_date:
                raise AppException(
                    status_code=400,
                    code="INVALID_OBSERVATION_DATE",
                    message=(
                        f"Observation '{obs.acquisition_id}' has date '{obs.date}', which is on or before "
                        f"the investigation comparison date '{comparison_date}'. "
                        f"Post-event Beat Test observations must occur strictly after the comparison date."
                    ),
                    suggested_action="Provide observation passes that occurred strictly after the comparison date.",
                )

            # Rejection 2: Observations not recorded in the study area's timeline
            if obs.acquisition_id not in study_area_acq_ids and obs.date not in study_area_dates:
                raise AppException(
                    status_code=400,
                    code="ACQUISITION_NOT_IN_STUDY_AREA",
                    message=(
                        f"Observation '{obs.acquisition_id}' (date: '{obs.date}') does not correspond to any "
                        f"satellite pass recorded for study area '{study_area_id}'."
                    ),
                    suggested_action=f"Select satellite acquisitions from the official timeline for study area '{study_area_id}' via GET /api/study-areas/{study_area_id}/acquisitions.",
                )

        observations_to_eval = req.observations
    else:
        # Load existing post-event acquisitions from study area timeline
        ref_track = ledger_data.get("track", 0)
        ref_orbit = ledger_data.get("orbit_direction", "")

        later_acqs = [
            a for a in acq_response.acquisitions
            if a.date > comparison_date
            and a.track == ref_track
            and a.orbit_direction == ref_orbit
        ]
        # Build default observations: change detection has not run yet by default
        observations_to_eval = [
            ObservationItem(
                acquisition_id=a.acquisition_id,
                date=a.date,
                valid=a.valid,
                exclusion_reason=a.exclusion_reason,
                change_detected=False,
            )
            for a in later_acqs
        ]

    # 2. Confounder flags
    confounder_flags = req.confounder_flags if req.confounder_flags is not None else ledger_data.get("confounder_flags", ["CLEAR"])

    # 3. Execute Beat Test Temporal Persistence/Recession Evaluation (Repair 2 / Finding 2)
    expected_behavior = ledger_data.get("expected_behavior", "sustained")
    (
        temporal_result,
        valid_count,
        detected_count,
        ratio,
        meets_threshold,
        excluded_acqs,
    ) = evaluate_beat_test(observations_to_eval, expected_behavior)

    # 4. Execute Three-State Evidence Label Mapping
    (
        evidence_label,
        verification_status,
        reasons_for_label,
    ) = map_evidence_label(
        temporal_result=temporal_result,
        confounder_flags=confounder_flags,
        valid_count=valid_count,
        detected_count=detected_count,
        ratio=ratio,
        excluded_acqs=excluded_acqs,
        expected_behavior=expected_behavior,
    )

    # 5. Build summary persistence description
    behavior = expected_behavior.strip().lower() if expected_behavior else "sustained"
    if valid_count < MIN_VALID_LATER_ACQUISITIONS:
        persistence_desc = f"Insufficient post-event observations ({valid_count} valid passes, minimum required: {MIN_VALID_LATER_ACQUISITIONS})"
    elif meets_threshold:
        if behavior == "receding":
            persistence_desc = f"Receding behavior confirmed: initial change detected in {detected_count}/{valid_count} ({ratio:.1%}) passes with subsequent recession"
        else:
            persistence_desc = f"Change persisted across {detected_count}/{valid_count} ({ratio:.1%}) valid later acquisitions (meets >= 66.7% threshold)"
    else:
        if behavior == "receding" and detected_count == valid_count:
            persistence_desc = f"Change persisted across all {detected_count}/{valid_count} (100.0%) passes without observed recession (does not match receding behavior)"
        else:
            persistence_desc = f"Change detected in {detected_count}/{valid_count} ({ratio:.1%}) valid later acquisitions (below 66.7% threshold)"

    # 6. Update Evidence Ledger
    ledger_data["valid_later_acquisitions_count"] = valid_count
    ledger_data["detected_later_acquisitions_count"] = detected_count
    ledger_data["excluded_acquisitions"] = excluded_acqs
    ledger_data["beat_test_status"] = "COMPLETED"
    ledger_data["beat_test_result"] = temporal_result
    ledger_data["persistence_result"] = persistence_desc
    ledger_data["confounder_flags"] = confounder_flags
    ledger_data["evidence_label"] = evidence_label
    ledger_data["verification_status"] = verification_status
    ledger_data["reasons_for_label"] = reasons_for_label

    # Preserve notes: update if provided, preserve existing if omitted (Repair 2 / Finding 5C)
    if req.notes is not None:
        ledger_data["evaluation_notes"] = req.notes
        record["notes"] = req.notes

    if req.changed_area_sq_km is not None:
        ledger_data["changed_area_sq_km"] = req.changed_area_sq_km
        ledger_data["change_detection_status"] = "COMPLETED"

    # Update parent record
    record["status"] = "EVALUATED"
    record["processing_status"]["beat_test_execution"] = "COMPLETED"
    record["ledger"] = ledger_data

    # 7. Persist to investigations.json and dedicated outputs/ledgers/{id}.json
    investigations_db[investigation_id] = record
    _save_all_investigations(investigations_db)

    LEDGERS_DIR.mkdir(parents=True, exist_ok=True)
    ledger_file = LEDGERS_DIR / f"{investigation_id}.json"
    with open(ledger_file, "w", encoding="utf-8") as f:
        json.dump(ledger_data, f, indent=2)

    confounders_clear = not any(
        f.upper().startswith("FLAGGED") or (f.upper() != "CLEAR" and f.strip() != "")
        for f in confounder_flags
    )

    current_notes = ledger_data.get("evaluation_notes") or record.get("notes")

    return EvaluationResponse(
        investigation_id=investigation_id,
        evidence_label=evidence_label,
        verification_status=verification_status,
        beat_test_status="COMPLETED",
        beat_test_result=temporal_result,
        valid_observations_count=valid_count,
        detected_observations_count=detected_count,
        persistence_ratio=ratio,
        persistence_threshold=0.667,
        meets_persistence_threshold=meets_threshold,
        excluded_acquisitions=excluded_acqs,
        confounder_flags=confounder_flags,
        confounders_clear=confounders_clear,
        reasons_for_label=reasons_for_label,
        changed_area_sq_km=ledger_data.get("changed_area_sq_km"),
        notes=current_notes,
        data_provenance="ILLUSTRATIVE — NOT REAL DATA",
    )
