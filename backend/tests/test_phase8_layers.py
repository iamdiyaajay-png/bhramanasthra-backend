"""
Tests for Phase 8: Layer-Serving Endpoints, Map Assets, and Path Traversal Defense
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

from tests.conftest_base import BaseTestCase


class TestMapLayers(BaseTestCase):

    def test_list_layers_manifest(self):
        """GET /api/investigations/{id}/layers returns manifest of supported layers."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-2026-KER-001/layers", auth=False)
        self.assertEqual(status, 200)
        self.assertEqual(body["investigation_id"], "INV-2026-KER-001")
        layers = body.get("layers", [])
        self.assertEqual(len(layers), 4)

        layer_names = [l["layer"] for l in layers]
        self.assertIn("change-mask", layer_names)
        self.assertIn("continuous", layer_names)
        self.assertIn("reference", layer_names)
        self.assertIn("comparison", layer_names)

    def test_list_layers_not_found(self):
        """GET /api/investigations/{id}/layers returns 404 for unknown ID."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-UNKNOWN-999/layers", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")

    def test_get_all_canonical_layers(self):
        """GET /api/investigations/{id}/layers/{layer} retrieves all 4 supported layers."""
        canonical_layers = ["change-mask", "continuous", "reference", "comparison"]
        for layer in canonical_layers:
            status, headers, body, _ = self.call_api(
                "GET", f"/api/investigations/INV-2026-KER-001/layers/{layer}", auth=False
            )
            self.assertEqual(status, 200, f"Layer {layer} failed to serve")
            self.assertIn("application/geo+json", headers.get("content-type", ""))
            self.assertIsInstance(body, dict)
            self.assertEqual(body.get("type"), "FeatureCollection")

    def test_layer_underscore_alias(self):
        """Layer alias 'change_mask' resolves correctly to 'change-mask'."""
        status, headers, body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/layers/change_mask", auth=False
        )
        self.assertEqual(status, 200)
        self.assertIn("application/geo+json", headers.get("content-type", ""))

    def test_unsupported_layer_name(self):
        """Requesting unsupported layer returns 400 UNSUPPORTED_LAYER."""
        status, _, body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-001/layers/elevation-model", auth=False
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["code"], "UNSUPPORTED_LAYER")

    def test_missing_layer_asset_on_disk(self):
        """Requesting layer for investigation without asset returns 404 LAYER_ASSET_NOT_FOUND."""
        status, _, body, _ = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-003/layers/change-mask", auth=False
        )
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "LAYER_ASSET_NOT_FOUND")

    def test_path_traversal_blocking(self):
        """Path traversal attempts with '..' or escape sequences are blocked."""
        traversal_attempts = [
            "../../../etc/passwd",
            "..%5C..%5Cdata%5Cinvestigations.json",
            "change-mask/../../secret",
        ]
        for bad_path in traversal_attempts:
            status, _, body, _ = self.call_api(
                "GET", f"/api/investigations/INV-2026-KER-001/layers/{bad_path}", auth=False
            )
            self.assertIn(status, [400, 404], f"Traversal '{bad_path}' not blocked properly (got {status})")
