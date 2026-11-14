"""
Tests for Phases 1-4: Health Check, Root Landing, and Study Areas
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

from tests.conftest_base import BaseTestCase


class TestStudyAreas(BaseTestCase):

    def test_health_check(self):
        """GET /api/health should return status healthy and challenge name."""
        status, _, body, _ = self.call_api("GET", "/api/health", auth=False)
        self.assertEqual(status, 200)
        self.assertEqual(body.get("status"), "healthy")
        self.assertIn("Dancing with the SARs", body.get("challenge", ""))

    def test_root_landing(self):
        """GET / should return welcome message with documentation pointers."""
        status, _, body, _ = self.call_api("GET", "/", auth=False)
        self.assertEqual(status, 200)
        self.assertIn("BHnMISnTRA", body.get("message", ""))
        self.assertEqual(body.get("docs"), "/docs")

    def test_list_study_areas(self):
        """GET /api/study-areas should return all monitored study areas."""
        status, _, body, _ = self.call_api("GET", "/api/study-areas", auth=False)
        self.assertEqual(status, 200)
        self.assertIsInstance(body, list)
        self.assertGreaterEqual(len(body), 3)

        ids = [area["id"] for area in body]
        self.assertIn("kerala-floods-2018", ids)
        self.assertIn("valencia-inundation-2024", ids)
        self.assertIn("wayanad-landslide-2024", ids)

        # Check required PRD schema fields
        kerala = next(a for a in body if a["id"] == "kerala-floods-2018")
        self.assertEqual(kerala["crs"], "EPSG:4326")
        self.assertEqual(len(kerala["bounding_box"]), 4)
        self.assertEqual(kerala["data_provenance"], "ILLUSTRATIVE — NOT REAL DATA")

    def test_get_study_area_by_id_success(self):
        """GET /api/study-areas/{id} should return single area details."""
        status, _, body, _ = self.call_api("GET", "/api/study-areas/kerala-floods-2018", auth=False)
        self.assertEqual(status, 200)
        self.assertEqual(body["id"], "kerala-floods-2018")
        self.assertEqual(body["phenomenon_type"], "flood")

    def test_get_study_area_not_found(self):
        """GET /api/study-areas/{id} with unknown ID should return 404 standard error."""
        status, _, body, _ = self.call_api("GET", "/api/study-areas/non-existent-area", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "STUDY_AREA_NOT_FOUND")
        self.assertIn("suggested_action", body)

    def test_get_study_area_acquisitions_success(self):
        """GET /api/study-areas/{id}/acquisitions should return satellite passes timeline."""
        status, _, body, _ = self.call_api("GET", "/api/study-areas/kerala-floods-2018/acquisitions", auth=False)
        self.assertEqual(status, 200)
        self.assertEqual(body["study_area_id"], "kerala-floods-2018")
        acquisitions = body.get("acquisitions", [])
        self.assertGreaterEqual(len(acquisitions), 3)

        first = acquisitions[0]
        self.assertEqual(first["mission"], "Sentinel-1A")
        self.assertEqual(first["orbit_direction"], "DESCENDING")
        self.assertEqual(first["track"], 144)

    def test_get_study_area_acquisitions_not_found(self):
        """GET /api/study-areas/{id}/acquisitions with unknown ID should return 404."""
        status, _, body, _ = self.call_api("GET", "/api/study-areas/unknown-id/acquisitions", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "STUDY_AREA_NOT_FOUND")

