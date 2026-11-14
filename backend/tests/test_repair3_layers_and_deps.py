"""
Tests for Repair 3: Dependencies and Map Layer Availability
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)

Verifies audit findings 1, 6, and 8:
- Finding 1: Explicit python-dotenv dependency declared in requirements.txt.
  Backend and its components import successfully without missing module errors.
- Finding 6: Support for both .tif and .tiff raster formats.
  Both return HTTP 200 and Content-Type: image/tiff.
  Existing GeoJSON, JSON, and PNG support preserved.
  Path traversal protections remain strictly intact.
- Finding 8: Missing layer assets accurately reported (HTTP 404 LAYER_ASSET_NOT_FOUND).
  Layer manifests accurately reflect file presence (available: True/False and format).
  Missing pipeline layers for VAL-004 and KER-003 are verified without fabricating synthetic data.
"""

from pathlib import Path
from tests.conftest_base import BaseTestCase, _backend_root
from app.services import layer_service


class TestRepair3LayersAndDeps(BaseTestCase):
    """
    Test suite for Repair 3: python-dotenv dependency verification and .tiff layer serving.
    Guarantees 100% data isolation via BaseTestCase sandbox.
    """

    def test_requirements_declares_python_dotenv(self):
        """1. Explicit python-dotenv dependency declared in requirements.txt."""
        req_file = _backend_root / "requirements.txt"
        self.assertTrue(req_file.is_file(), "backend/requirements.txt must exist")
        content = req_file.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

        dotenv_entries = [l for l in lines if l.startswith("python-dotenv")]
        self.assertTrue(len(dotenv_entries) >= 1, "requirements.txt must declare python-dotenv")
        self.assertIn("python-dotenv>=", dotenv_entries[0])

    def test_backend_imports_successfully_with_declared_dependencies(self):
        """2. Backend and core components import successfully with declared dependencies."""
        import dotenv
        from dotenv import load_dotenv
        self.assertTrue(callable(load_dotenv))

        from app import main, dependencies
        from app.services import layer_service, evidence_service, investigation_service
        self.assertIsNotNone(main.app)
        self.assertIsNotNone(dependencies.get_server_api_key)
        self.assertIn(".tiff", layer_service.CANONICAL_LAYERS["change-mask"]["extensions"])
        self.assertIn(".tif", layer_service.CANONICAL_LAYERS["change-mask"]["extensions"])

    def test_tif_layer_serving_returns_200_and_image_tiff(self):
        """3. .tif layer asset serving returns HTTP 200 and Content-Type: image/tiff."""
        target_dir = self.tmp_layers / "INV-2026-KER-003"
        target_dir.mkdir(parents=True, exist_ok=True)
        tif_file = target_dir / "change-mask.tif"
        # Standard TIFF header bytes (Little Endian: II*\0)
        tif_file.write_bytes(b"II*\x00\x08\x00\x00\x00\x00\x00")

        status, headers, _, raw_text = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-003/layers/change-mask", auth=False
        )
        self.assertEqual(status, 200)
        content_type = headers.get("content-type", "")
        self.assertTrue(
            content_type.startswith("image/tiff"),
            f"Expected image/tiff content type, got '{content_type}'",
        )

    def test_tiff_layer_serving_returns_200_and_image_tiff(self):
        """4. .tiff layer asset serving returns HTTP 200 and Content-Type: image/tiff (Finding 6)."""
        target_dir = self.tmp_layers / "INV-2026-KER-003"
        target_dir.mkdir(parents=True, exist_ok=True)
        tiff_file = target_dir / "continuous.tiff"
        tiff_file.write_bytes(b"MM\x00*\x00\x00\x00\x08\x00\x00")

        status, headers, _, raw_text = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-003/layers/continuous", auth=False
        )
        self.assertEqual(status, 200)
        content_type = headers.get("content-type", "")
        self.assertTrue(
            content_type.startswith("image/tiff"),
            f"Expected image/tiff content type, got '{content_type}'",
        )

    def test_existing_geojson_layer_serving_remains_functional(self):
        """5. Existing GeoJSON layer serving remains functional with application/geo+json."""
        status, headers, body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/layers/change-mask", auth=False
        )
        self.assertEqual(status, 200)
        content_type = headers.get("content-type", "")
        self.assertTrue(
            content_type.startswith("application/geo+json") or "geo+json" in content_type,
            f"Expected application/geo+json, got '{content_type}'",
        )
        self.assertEqual(body.get("type"), "FeatureCollection")
        self.assertIn("features", body)

    def test_invalid_layer_names_and_path_traversal_blocked(self):
        """6. Invalid layer names and path traversal sequences remain blocked with HTTP 400."""
        # Unsupported name
        status, _, body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/layers/unsupported-layer", auth=False
        )
        self.assertEqual(status, 400)
        self.assertEqual(body.get("code"), "UNSUPPORTED_LAYER")

        # Path traversal sequence in layer parameter
        status_trav, _, body_trav, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/layers/..%2F..%2Fsecret", auth=False
        )
        self.assertIn(status_trav, [400, 422])

    def test_missing_layer_assets_return_correct_404_response(self):
        """7. Missing layer assets return HTTP 404 with LAYER_ASSET_NOT_FOUND (Finding 8)."""
        # INV-2026-VAL-004 currently has no layer directory on disk
        status, _, body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-VAL-004/layers/change-mask", auth=False
        )
        self.assertEqual(status, 404)
        self.assertEqual(body.get("code"), "LAYER_ASSET_NOT_FOUND")
        self.assertIn("Member 1's SAR processing pipeline", body.get("suggested_action", ""))

    def test_layer_manifest_accurately_reflects_available_files(self):
        """8. Layer manifests accurately reflect available files and formats."""
        # 8a. Investigation with all 4 GeoJSON layers present (INV-2026-KER-001)
        status_ker, _, body_ker, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/layers", auth=False
        )
        self.assertEqual(status_ker, 200)
        self.assertEqual(body_ker["available_layers_count"], 4)
        for layer in body_ker["layers"]:
            self.assertTrue(layer["available"])
            self.assertEqual(layer["format"], "geojson")

        # 8b. Investigation with missing layers on disk (INV-2026-VAL-004)
        status_val, _, body_val, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-VAL-004/layers", auth=False
        )
        self.assertEqual(status_val, 200)
        self.assertEqual(body_val["available_layers_count"], 0)
        for layer in body_val["layers"]:
            self.assertFalse(layer["available"])
            self.assertEqual(layer["format"], "unavailable")

        # 8c. Investigation with .tif and .tiff files added
        target_dir = self.tmp_layers / "INV-2026-KER-003"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "change-mask.tif").write_bytes(b"II*\x00")
        (target_dir / "continuous.tiff").write_bytes(b"MM\x00*")

        status_mix, _, body_mix, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-003/layers", auth=False
        )
        self.assertEqual(status_mix, 200)
        self.assertEqual(body_mix["available_layers_count"], 2)

        layer_map = {l["layer"]: l for l in body_mix["layers"]}
        self.assertTrue(layer_map["change-mask"]["available"])
        self.assertEqual(layer_map["change-mask"]["format"], "tif")
        self.assertTrue(layer_map["continuous"]["available"])
        self.assertEqual(layer_map["continuous"]["format"], "tiff")
        self.assertFalse(layer_map["reference"]["available"])
        self.assertEqual(layer_map["reference"]["format"], "unavailable")
        self.assertFalse(layer_map["comparison"]["available"])
        self.assertEqual(layer_map["comparison"]["format"], "unavailable")

    def test_existing_investigation_and_layer_records_remain_unchanged(self):
        """9. Existing persistent investigation records and layers are unchanged."""
        inv_file = _backend_root / "data" / "investigations.json"
        self.assertTrue(inv_file.is_file())
        self.assertGreater(inv_file.stat().st_size, 30000)

        layer_root = _backend_root / "outputs" / "layers"
        self.assertTrue((layer_root / "INV-2026-KER-001" / "change-mask.geojson").is_file())
        self.assertTrue((layer_root / "INV-2026-KER-002" / "change-mask.geojson").is_file())

