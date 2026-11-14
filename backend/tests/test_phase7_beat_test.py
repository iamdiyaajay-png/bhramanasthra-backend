"""
Tests for Phase 7: Three-State Evidence Label Logic & Beat Test Temporal Evaluation
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
PRD Section 9: Temporal Persistence Rules & Thresholds
"""

from tests.conftest_base import BaseTestCase


class TestBeatTest(BaseTestCase):

    def test_beat_test_fewer_than_3_valid_acquisitions_unverified(self):
        """Fewer than 3 valid later acquisitions yields Unverified label and insufficient beat test."""
        payload = {
            "observations": [
                {
                    "acquisition_id": "S1A_TEST_001",
                    "date": "2018-08-28",
                    "valid": True,
                    "exclusion_reason": None,
                    "change_detected": True,
                },
                {
                    "acquisition_id": "S1A_TEST_002",
                    "date": "2018-09-09",
                    "valid": True,
                    "exclusion_reason": None,
                    "change_detected": True,
                },
                {
                    "acquisition_id": "S1A_TEST_003",
                    "date": "2018-09-21",
                    "valid": False,
                    "exclusion_reason": "High ionospheric noise",
                    "change_detected": False,
                },
            ],
            "confounder_flags": ["CLEAR"],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["evidence_label"], "Unverified")
        self.assertEqual(body["beat_test_result"], "insufficient")
        self.assertEqual(body["valid_observations_count"], 2)
        self.assertEqual(len(body["excluded_acquisitions"]), 1)

    def test_beat_test_supported_exact_3_passes(self):
        """Exactly 3 valid passes with 2/3 detected and clear confounders yields Supported."""
        payload = {
            "observations": [
                {"acquisition_id": "S1A_PASS_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_PASS_02", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_PASS_03", "date": "2018-09-21", "valid": True, "change_detected": False},
            ],
            "confounder_flags": ["CLEAR"],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["evidence_label"], "Supported")
        self.assertEqual(body["beat_test_result"], "matches")
        self.assertEqual(body["valid_observations_count"], 3)
        self.assertEqual(body["detected_observations_count"], 2)
        self.assertTrue(body["meets_persistence_threshold"])
        self.assertTrue(body["confounders_clear"])

    def test_beat_test_inconclusive_low_persistence(self):
        """Detection in < 2/3 valid acquisitions (1/3 = 33.3%) yields Inconclusive."""
        payload = {
            "observations": [
                {"acquisition_id": "S1A_PASS_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_PASS_02", "date": "2018-09-09", "valid": True, "change_detected": False},
                {"acquisition_id": "S1A_PASS_03", "date": "2018-09-21", "valid": True, "change_detected": False},
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

    def test_beat_test_inconclusive_flagged_confounder(self):
        """Active confounder yields Inconclusive even when change detected in 3/3 acquisitions."""
        payload = {
            "observations": [
                {"acquisition_id": "S1A_PASS_01", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_PASS_02", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_PASS_03", "date": "2018-09-21", "valid": True, "change_detected": True},
            ],
            "confounder_flags": ["FLAGGED: Extreme precipitation & standing water artifact"],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["evidence_label"], "Inconclusive")
        self.assertFalse(body["confounders_clear"])

    def test_beat_test_invalid_pass_exclusion(self):
        """Invalid acquisitions are excluded from count and exclusion reasons are documented."""
        payload = {
            "observations": [
                {"acquisition_id": "S1A_P1", "date": "2018-08-28", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_P2", "date": "2018-09-09", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_P3", "date": "2018-09-21", "valid": True, "change_detected": True},
                {"acquisition_id": "S1A_P4", "date": "2018-10-03", "valid": False, "exclusion_reason": "Orbit track mismatch", "change_detected": False},
            ],
            "confounder_flags": ["CLEAR"],
        }
        status, _, body, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-002/evaluate", body=payload, auth=True
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["valid_observations_count"], 3)
        self.assertEqual(len(body["excluded_acquisitions"]), 1)
        self.assertEqual(body["excluded_acquisitions"][0]["reason"], "Orbit track mismatch")

    def test_get_evaluation_success(self):
        """GET /api/investigations/{id}/evaluation retrieves evaluation state."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-2026-KER-001/evaluation", auth=False)
        self.assertEqual(status, 200)
        self.assertEqual(body["investigation_id"], "INV-2026-KER-001")
        self.assertIn("evidence_label", body)
        self.assertIn("meets_persistence_threshold", body)

    def test_get_evaluation_not_found(self):
        """GET /api/investigations/{id}/evaluation returns 404 for unknown ID."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-UNKNOWN-999/evaluation", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")
