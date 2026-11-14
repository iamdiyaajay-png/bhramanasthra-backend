"""
Tests for Phase 5: Investigation Creation, Validation, and Retrieval
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

from tests.conftest_base import BaseTestCase


class TestInvestigations(BaseTestCase):

    def test_create_investigation_success(self):
        """POST /api/investigations creates new record and initializes ledger."""
        payload = {
            "study_area_id": "kerala-floods-2018",
            "reference_date": "2018-08-08",
            "comparison_date": "2018-08-16",
        }
        status, _, body, _ = self.call_api("POST", "/api/investigations", body=payload, auth=True)
        self.assertEqual(status, 201)
        self.assertTrue(body["investigation_id"].startswith("INV-2026-KER-"))
        self.assertEqual(body["status"], "CREATED")
        self.assertEqual(body["study_area_id"], "kerala-floods-2018")

        # Verify it can be retrieved immediately
        get_status, _, get_body, _ = self.call_api(
            "GET", f"/api/investigations/{body['investigation_id']}", auth=False
        )
        self.assertEqual(get_status, 200)
        self.assertEqual(get_body["investigation_id"], body["investigation_id"])
        self.assertIn("evidence_ledger", get_body)

    def test_create_investigation_invalid_date_range(self):
        """POST /api/investigations rejects comparison_date <= reference_date with 400."""
        payload = {
            "study_area_id": "kerala-floods-2018",
            "reference_date": "2018-08-16",
            "comparison_date": "2018-08-08",
        }
        status, _, body, _ = self.call_api("POST", "/api/investigations", body=payload, auth=True)
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "INVALID_DATE_ORDER")
        self.assertIn("suggested_action", body)

    def test_create_investigation_study_area_not_found(self):
        """POST /api/investigations rejects unknown study area with 404."""
        payload = {
            "study_area_id": "unknown-nonexistent-area",
            "reference_date": "2018-08-08",
            "comparison_date": "2018-08-16",
        }
        status, _, body, _ = self.call_api("POST", "/api/investigations", body=payload, auth=True)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "STUDY_AREA_NOT_FOUND")

    def test_create_investigation_malformed_payload_422(self):
        """POST /api/investigations missing required fields returns 422 standard validation error."""
        payload = {
            "study_area_id": "kerala-floods-2018",
            # missing reference_date and comparison_date
        }
        status, _, body, _ = self.call_api("POST", "/api/investigations", body=payload, auth=True)
        self.assertEqual(status, 422)
        self.assertEqual(body["code"], "INVALID_REQUEST_PARAMETERS")
        self.assertIn("suggested_action", body)

    def test_get_investigation_by_id_success(self):
        """GET /api/investigations/{id} retrieves existing demo investigation."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-2026-KER-001", auth=False)
        self.assertEqual(status, 200)
        self.assertEqual(body["investigation_id"], "INV-2026-KER-001")
        self.assertEqual(body["study_area"]["name"], "Kerala Flood Basin (Periyar River)")
        self.assertIn("reference_acquisition", body)
        self.assertIn("comparison_acquisition", body)
        self.assertIn("evidence_ledger", body)

    def test_get_investigation_not_found(self):
        """GET /api/investigations/{id} returns 404 for unknown ID."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-UNKNOWN-999", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")
