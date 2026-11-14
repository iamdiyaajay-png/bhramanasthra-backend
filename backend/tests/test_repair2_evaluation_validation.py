"""
Tests for Repair 2: Beat Test Scientific Logic & Evaluation Validation
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)

Verifies audit findings 2 and 5:
- Finding 2: Beat Test actively evaluates expected_behavior (receding vs sustained).
  * Receding phenomena with 100% persistence across all passes are NOT labeled Supported (does_not_match / Inconclusive).
  * Receding phenomena with initial detection (>= 2/3) followed by recession match expected behavior (Supported).
  * Sustained phenomena with >= 2/3 persistence match expected behavior (Supported).
  * Fewer than 3 valid later acquisitions yields Unverified / insufficient.
- Finding 5A: changed_area_sq_km non-negative validation (>= 0.0 accepted, negative rejected with 422).
- Finding 5B: Observation date on/before comparison_date rejected with 400 INVALID_OBSERVATION_DATE.
  Observations not in study area timeline rejected with 400 ACQUISITION_NOT_IN_STUDY_AREA.
  Empty observations list rejected with 400 EMPTY_OBSERVATIONS_LIST.
- Finding 5C: Evaluation notes saved and returned in evaluation and ledger endpoints.
  Existing notes preserved when omitted in subsequent evaluation calls.
"""

from tests.conftest_base import BaseTestCase
from app.services import investigation_service as inv_service


class TestRepair2EvaluationValidation(BaseTestCase):
    """
    Test suite for Repair 2: Beat Test scientific logic and evaluation endpoint validation.
    Guarantees 100% data isolation via BaseTestCase sandbox.
    """

    def test_receding_flood_documented_recession_yields_supported(self):
        """1. Receding flood with documented recession ([True, True, False]) yields Supported + matches."""
        payload = {
            "observations": [
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_03", "date": "2018-09-21", "valid": True, "change_detected": False},
            ],
            "confounder_flags": ["CLEAR"],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["evidence_label"], "Supported")
        self.assertEqual(body["beat_test_result"], "matches")
        self.assertTrue(body["meets_persistence_threshold"])
        self.assertEqual(body["valid_observations_count"], 3)
        self.assertEqual(body["detected_observations_count"], 2)
        reasons_text = " ".join(body["reasons_for_label"])
        self.assertIn("documented recession", reasons_text)

    def test_receding_flood_100pct_persistence_yields_inconclusive(self):
        """2. Receding flood with 100% persistence ([True, True, True]) yields Inconclusive + does_not_match (Finding 2)."""
        payload = {
            "observations": [
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_03", "date": "2018-09-21", "valid": True, "change_detected": True},
            ],
            "confounder_flags": ["CLEAR"],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["evidence_label"], "Inconclusive")
        self.assertEqual(body["beat_test_result"], "does_not_match")
        self.assertFalse(body["meets_persistence_threshold"])
        self.assertEqual(body["valid_observations_count"], 3)
        self.assertEqual(body["detected_observations_count"], 3)
        reasons_text = " ".join(body["reasons_for_label"])
        self.assertTrue(
            "receding" in reasons_text.lower() and "no observed recession" in reasons_text.lower()
        )

    def test_sustained_phenomenon_100pct_persistence_yields_supported(self):
        """3. Sustained phenomenon with 100% persistence yields Supported + matches."""
        # Update expected_behavior in isolated temporary sandbox
        db = inv_service._load_all_investigations()
        record = db["INV-2026-KER-002"]
        record["expected_behavior"] = "sustained"
        record["ledger"]["expected_behavior"] = "sustained"
        inv_service._save_all_investigations(db)

        payload = {
            "observations": [
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_03", "date": "2018-09-21", "valid": True, "change_detected": True},
            ],
            "confounder_flags": ["CLEAR"],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["evidence_label"], "Supported")
        self.assertEqual(body["beat_test_result"], "matches")
        self.assertTrue(body["meets_persistence_threshold"])
        self.assertEqual(body["persistence_ratio"], 1.0)

    def test_fewer_than_3_valid_observations_yields_unverified(self):
        """4. Fewer than 3 valid later observations yields Unverified + insufficient."""
        payload = {
            "observations": [
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
            ],
            "confounder_flags": ["CLEAR"],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["evidence_label"], "Unverified")
        self.assertEqual(body["beat_test_result"], "insufficient")
        self.assertFalse(body["meets_persistence_threshold"])
        self.assertEqual(body["valid_observations_count"], 2)

    def test_observation_date_on_or_before_comparison_date_rejected_400(self):
        """5. Observation dated on or before comparison_date returns HTTP 400 INVALID_OBSERVATION_DATE."""
        # kerala-floods comparison_date is 2018-08-16
        payload = {
            "observations": [
                {"acquisition_id": "S1A_SAME", "date": "2018-08-16", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
            ],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "INVALID_OBSERVATION_DATE")
        self.assertIn("comparison date", body["message"])

        # Prior date (2018-08-08 is reference date)
        payload_prior = {
            "observations": [
                {"acquisition_id": "S1A_PRIOR", "date": "2018-08-08", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
            ],
        }
        status_prior, _, body_prior, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload_prior, auth=True
        )
        self.assertEqual(status_prior, 400)
        self.assertEqual(body_prior["code"], "INVALID_OBSERVATION_DATE")

    def test_observation_outside_study_area_timeline_rejected_400(self):
        """6. Observation outside study area timeline returns HTTP 400 ACQUISITION_NOT_IN_STUDY_AREA."""
        payload = {
            "observations": [
                {"acquisition_id": "S1A_UNKNOWN", "date": "2025-01-01", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
            ],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "ACQUISITION_NOT_IN_STUDY_AREA")
        self.assertIn("satellite pass recorded for study area", body["message"])

    def test_negative_changed_area_rejected_422(self):
        """7. Negative changed_area_sq_km returns HTTP 422 INVALID_REQUEST_PARAMETERS."""
        payload = {
            "changed_area_sq_km": -10.5,
            "confounder_flags": ["CLEAR"],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 422)
        self.assertEqual(body["code"], "INVALID_REQUEST_PARAMETERS")

    def test_zero_changed_area_accepted_200(self):
        """8. Zero changed_area_sq_km (0.0) is accepted (HTTP 200)."""
        payload = {
            "changed_area_sq_km": 0.0,
            "observations": [
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_03", "date": "2018-09-21", "valid": True, "change_detected": False},
            ],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["changed_area_sq_km"], 0.0)

    def test_positive_changed_area_accepted_200(self):
        """9. Positive changed_area_sq_km (34.8) is accepted (HTTP 200)."""
        payload = {
            "changed_area_sq_km": 34.8,
            "observations": [
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_03", "date": "2018-09-21", "valid": True, "change_detected": False},
            ],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["changed_area_sq_km"], 34.8)

    def test_evaluation_notes_saved_and_returned(self):
        """10. Evaluation notes are saved and returned in evaluation and ledger endpoints."""
        custom_notes = "Field ground-truth validation: 34.8 sq km inundation confirmed by Sentinel-1A pass series."
        payload = {
            "notes": custom_notes,
            "observations": [
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_03", "date": "2018-09-21", "valid": True, "change_detected": False},
            ],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["notes"], custom_notes)

        # Verify GET /api/investigations/{id}/evaluation returns the saved notes
        status_get, _, body_get, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-002/evaluation", auth=False
        )
        self.assertEqual(status_get, 200)
        self.assertEqual(body_get["notes"], custom_notes)

        # Verify GET /api/investigations/{id}/ledger returns evaluation_notes
        status_led, _, body_led, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-002/ledger", auth=False
        )
        self.assertEqual(status_led, 200)
        self.assertEqual(body_led.get("evaluation_notes"), custom_notes)

    def test_existing_notes_preserved_when_omitted_in_subsequent_request(self):
        """11. Existing notes are preserved when subsequent evaluation request omits notes."""
        initial_notes = "Initial calibration notes from Member 1 SAR processing run."
        payload_1 = {
            "notes": initial_notes,
            "observations": [
                {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_03", "date": "2018-09-21", "valid": True, "change_detected": False},
            ],
        }
        status1, _, body1, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload_1, auth=True
        )
        self.assertEqual(status1, 200)
        self.assertEqual(body1["notes"], initial_notes)

        # Subsequent evaluation request without notes field
        payload_2 = {
            "changed_area_sq_km": 42.1,
            "confounder_flags": ["CLEAR"],
        }
        status2, _, body2, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload_2, auth=True
        )
        self.assertEqual(status2, 200)
        self.assertEqual(body2["notes"], initial_notes)

        # Confirm GET evaluation endpoint still serves original notes
        status_get, _, body_get, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-002/evaluation", auth=False
        )
        self.assertEqual(status_get, 200)
        self.assertEqual(body_get["notes"], initial_notes)

    def test_empty_observations_list_rejected_400(self):
        """12. Explicit empty observations list [] is rejected with HTTP 400 EMPTY_OBSERVATIONS_LIST."""
        payload = {
            "observations": [],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "EMPTY_OBSERVATIONS_LIST")

