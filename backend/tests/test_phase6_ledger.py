"""
Tests for Phase 6 & Task 1: Evidence Ledger Storage, Retrieval, Download, and Schema Compatibility
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

from app.schemas.investigation import EvidenceLedgerRecord
from tests.conftest_base import BaseTestCase


class TestEvidenceLedger(BaseTestCase):

    def test_get_ledger_success(self):
        """GET /api/investigations/{id}/ledger returns complete Evidence Ledger JSON."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-2026-KER-002/ledger", auth=False)
        self.assertEqual(status, 200)
        self.assertEqual(body["investigation_id"], "INV-2026-KER-002")
        self.assertEqual(body["study_area_id"], "kerala-floods-2018")
        self.assertEqual(body["data_provenance"], "ILLUSTRATIVE — NOT REAL DATA")
        self.assertIn("configuration_hash", body)
        self.assertIn("reproduce_command", body)
        self.assertIn("known_limitations", body)

    def test_get_ledger_not_found(self):
        """GET /api/investigations/{id}/ledger returns 404 for unknown ID."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-UNKNOWN-999/ledger", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")

    def test_download_ledger_file(self):
        """GET /api/investigations/{id}/ledger/download downloads standalone file with attachment headers."""
        status, headers, body, raw = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-002/ledger/download", auth=False
        )
        self.assertEqual(status, 200)
        content_disp = headers.get("content-disposition", "")
        self.assertIn("attachment", content_disp)
        self.assertIn("evidence-ledger-INV-2026-KER-002.json", content_disp)
        self.assertEqual(body["investigation_id"], "INV-2026-KER-002")

    def test_download_ledger_not_found(self):
        """GET /api/investigations/{id}/ledger/download returns 404 for unknown ID."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-UNKNOWN-999/ledger/download", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")

    def test_task1_schema_backwards_compatibility(self):
        """Task 1: Pre-existing ledger without optional fields loads with None values."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-2026-KER-002/ledger", auth=False)
        self.assertEqual(status, 200)
        self.assertIn("independent_reference", body)
        self.assertIn("layer_references", body)
        self.assertIsNone(body["independent_reference"])
        self.assertIsNone(body["layer_references"])

    def test_task1_populated_serialization(self):
        """Task 1: EvidenceLedgerRecord correctly serializes populated independent_reference and layer_references."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-2026-KER-002/ledger", auth=False)
        self.assertEqual(status, 200)

        test_data = dict(body)
        test_data["independent_reference"] = {
            "source": "Copernicus EMS Flood Inundation Map",
            "product_id": "EMSR304_01PERIYAR",
            "reported_extent_sq_km": 15.2,
        }
        test_data["layer_references"] = [
            "/api/investigations/INV-2026-KER-002/layers/change-mask",
            "/api/investigations/INV-2026-KER-002/layers/continuous",
        ]

        record = EvidenceLedgerRecord(**test_data)
        dumped = record.model_dump()
        self.assertEqual(dumped["independent_reference"]["product_id"], "EMSR304_01PERIYAR")
        self.assertEqual(len(dumped["layer_references"]), 2)
