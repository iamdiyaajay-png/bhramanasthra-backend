"""
Tests for Repair 1: Investigation Data Safety and Unique Collision-Proof IDs
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
Verifies Finding 3 (Corrupt JSON protection, backups, atomic writes)
and Finding 4 (Independent per-slug sequence scanning, collision-proofing).
"""

import json
from unittest.mock import patch
from pathlib import Path

from tests.conftest_base import BaseTestCase
import app.services.investigation_service as inv_service
from app.schemas.errors import AppException


class TestInvestigationDataSafetyAndUniqueIDs(BaseTestCase):

    # -------------------------------------------------------------------------
    # Finding 3: Corrupt JSON Protection & Atomic Writes
    # -------------------------------------------------------------------------

    def test_corrupt_json_preserved_and_backup_created(self):
        """Corrupted investigations.json is preserved, backed up, and raises controlled error."""
        corrupt_bytes = b'{"INV-2026-KER-001": { "corrupted": true, UNTERMINATED_STRING'
        with open(inv_service.INVESTIGATIONS_FILE, "wb") as f:
            f.write(corrupt_bytes)

        # Loading must raise controlled AppException, never silently return {}
        with self.assertRaises(AppException) as ctx:
            inv_service._load_all_investigations()

        self.assertEqual(ctx.exception.status_code, 500)
        self.assertEqual(ctx.exception.code, "DATABASE_CORRUPTION_ERROR")

        # Verify the original corrupted file is intact and not deleted or truncated
        with open(inv_service.INVESTIGATIONS_FILE, "rb") as f:
            content_after = f.read()
        self.assertEqual(content_after, corrupt_bytes)

        # Verify a .corrupt backup file was created in the data directory
        backups = list(inv_service.DATA_DIR.glob(f"{inv_service.INVESTIGATIONS_FILE.name}.corrupt.*"))
        self.assertGreater(len(backups), 0, "Expected at least one .corrupt backup file to be created")
        with open(backups[0], "rb") as f:
            backup_content = f.read()
        self.assertEqual(backup_content, corrupt_bytes)

    def test_corrupt_json_causes_controlled_error_on_api(self):
        """API endpoints return standard HTTP 500 when database file is corrupted."""
        with open(inv_service.INVESTIGATIONS_FILE, "w", encoding="utf-8") as f:
            f.write("INVALID JSON SYNTAX HERE")

        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-2026-KER-001", auth=False)
        self.assertEqual(status, 500)
        self.assertEqual(body["code"], "DATABASE_CORRUPTION_ERROR")
        self.assertIn("suggested_action", body)

    def test_atomic_write_preserves_old_file_if_saving_fails(self):
        """Atomic write ensures that if persisting fails, previous valid file is untouched."""
        original_data = {"ORIGINAL-ID": {"status": "VALID_ORIGINAL"}}
        inv_service._save_all_investigations(original_data)

        # Read back to confirm baseline
        loaded = inv_service._load_all_investigations()
        self.assertEqual(loaded, original_data)

        # Simulate unexpected filesystem error during os.replace
        with patch("os.replace", side_effect=OSError("Disk full or locked file")):
            with self.assertRaises(AppException) as ctx:
                inv_service._save_all_investigations({"NEW-ID": {"status": "SHOULD_FAIL"}})

            self.assertEqual(ctx.exception.status_code, 500)
            self.assertEqual(ctx.exception.code, "DATABASE_WRITE_ERROR")

        # Confirm the original file was NOT destroyed or overwritten
        restored = inv_service._load_all_investigations()
        self.assertEqual(restored, original_data)

        # Confirm no temporary files linger in data directory
        lingering_tmp = list(inv_service.DATA_DIR.glob(f"{inv_service.INVESTIGATIONS_FILE.name}.tmp.*"))
        self.assertEqual(len(lingering_tmp), 0)

    def test_missing_database_file_returns_empty_dict(self):
        """When investigations.json does not exist (initial clean state), returns empty dict."""
        if inv_service.INVESTIGATIONS_FILE.exists():
            inv_service.INVESTIGATIONS_FILE.unlink()

        self.assertFalse(inv_service.INVESTIGATIONS_FILE.exists())
        data = inv_service._load_all_investigations()
        self.assertEqual(data, {})

    # -------------------------------------------------------------------------
    # Finding 4: Independent Per-Slug Sequences & Collision-Proofing
    # -------------------------------------------------------------------------

    def test_new_ids_use_correct_per_study_area_sequence(self):
        """New investigation IDs scan highest existing number per slug independently."""
        # Baseline seed data in self.tmp_data has:
        # KER: INV-2026-KER-001..003, 005..008 (highest is 8)
        # VAL: INV-2026-VAL-004 (highest is 4)

        # 1. Create a Kerala investigation -> must be INV-2026-KER-009
        ker_payload = {
            "study_area_id": "kerala-floods-2018",
            "reference_date": "2018-08-08",
            "comparison_date": "2018-08-16",
        }
        status, _, ker_body, _ = self.call_api("POST", "/api/investigations", body=ker_payload, auth=True)
        self.assertEqual(status, 201)
        self.assertEqual(ker_body["investigation_id"], "INV-2026-KER-009")

        # 2. Create a Valencia investigation -> must be INV-2026-VAL-005 (not 001, not 010!)
        val_payload = {
            "study_area_id": "valencia-inundation-2024",
            "reference_date": "2024-10-23",
            "comparison_date": "2024-10-31",
        }
        status, _, val_body, _ = self.call_api("POST", "/api/investigations", body=val_payload, auth=True)
        self.assertEqual(status, 201)
        self.assertEqual(val_body["investigation_id"], "INV-2026-VAL-005")

        # 3. Create a Wayanad investigation (slug WAY) -> starts at INV-2026-WAY-001
        way_payload = {
            "study_area_id": "wayanad-landslide-2024",
            "reference_date": "2024-07-20",
            "comparison_date": "2024-08-01",
        }
        status, _, way_body, _ = self.call_api("POST", "/api/investigations", body=way_payload, auth=True)
        self.assertEqual(status, 201)
        self.assertEqual(way_body["investigation_id"], "INV-2026-WAY-001")

        # 4. Create another Valencia investigation -> advances to INV-2026-VAL-006
        status, _, val_body2, _ = self.call_api("POST", "/api/investigations", body=val_payload, auth=True)
        self.assertEqual(status, 201)
        self.assertEqual(val_body2["investigation_id"], "INV-2026-VAL-006")

    def test_existing_ids_are_never_overwritten_on_collision(self):
        """Collision guard advances sequence and never overwrites an existing record."""
        # Manually inject an investigation at KER-009
        db = inv_service._load_all_investigations()
        preexisting_record = {
            "investigation_id": "INV-2026-KER-009",
            "status": "PREEXISTING_RECORD",
            "created_at": "2026-01-01T00:00:00Z",
            "study_area_id": "kerala-floods-2018",
            "reference_date": "2018-08-08",
            "comparison_date": "2018-08-16",
            "ledger": {"investigation_id": "INV-2026-KER-009", "evidence_label": "Unverified"},
            "processing_status": {},
        }
        db["INV-2026-KER-009"] = preexisting_record
        inv_service._save_all_investigations(db)

        # Now trigger investigation creation for Kerala
        ker_payload = {
            "study_area_id": "kerala-floods-2018",
            "reference_date": "2018-08-08",
            "comparison_date": "2018-08-16",
        }
        status, _, body, _ = self.call_api("POST", "/api/investigations", body=ker_payload, auth=True)
        self.assertEqual(status, 201)

        # The ID must have automatically bypassed KER-009 and allocated KER-010
        self.assertEqual(body["investigation_id"], "INV-2026-KER-010")

        # Verify KER-009 was NEVER overwritten and retains its original data
        reloaded = inv_service._load_all_investigations()
        self.assertIn("INV-2026-KER-009", reloaded)
        self.assertEqual(reloaded["INV-2026-KER-009"]["status"], "PREEXISTING_RECORD")
        self.assertIn("INV-2026-KER-010", reloaded)

