"""
Tests for Task 3: Backend Authentication on Mutation Endpoints
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
Enforces fail-closed server configuration, X-API-Key header verification, and public GET endpoints.
"""

import os
from tests.conftest_base import BaseTestCase, TEST_API_KEY


class TestBackendAuthentication(BaseTestCase):

    def test_missing_server_key_fails_closed_500(self):
        """When BHNMISNTRA_API_KEY is unset or empty on the server, mutations fail closed with 500."""
        os.environ.pop("BHNMISNTRA_API_KEY", None)

        status, _, body, _ = self.call_api("POST", "/api/investigations", body={}, auth=False)
        self.assertEqual(status, 500)
        self.assertEqual(body["code"], "SERVER_CONFIGURATION_ERROR")
        self.assertIn("Set the 'BHNMISNTRA_API_KEY' environment variable", body["suggested_action"])

        status_eval, _, body_eval, _ = self.call_api(
            "POST",
            "/api/investigations/INV-2026-KER-001/evaluate",
            headers={"X-API-Key": "any-key"},
            body={"observations": []},
            auth=False,
        )
        self.assertEqual(status_eval, 500)
        self.assertEqual(body_eval["code"], "SERVER_CONFIGURATION_ERROR")

    def test_missing_client_header_returns_401(self):
        """Calling protected mutation endpoints without X-API-Key header returns 401."""
        status, _, body, _ = self.call_api("POST", "/api/investigations", body={}, auth=False)
        self.assertEqual(status, 401)
        self.assertEqual(body["code"], "AUTHENTICATION_REQUIRED")
        self.assertIn("Provide a valid 'X-API-Key'", body["suggested_action"])

        status_eval, _, body_eval, _ = self.call_api(
            "POST", "/api/investigations/INV-2026-KER-001/evaluate", body={}, auth=False
        )
        self.assertEqual(status_eval, 401)
        self.assertEqual(body_eval["code"], "AUTHENTICATION_REQUIRED")

    def test_invalid_client_header_returns_401(self):
        """Calling protected endpoints with incorrect X-API-Key returns 401."""
        status, _, body, _ = self.call_api(
            "POST",
            "/api/investigations",
            headers={"X-API-Key": "incorrect-secret-key-123"},
            body={},
            auth=False,
        )
        self.assertEqual(status, 401)
        self.assertEqual(body["code"], "AUTHENTICATION_REQUIRED")

    def test_valid_client_header_allows_creation(self):
        """Valid X-API-Key allows investigation creation (HTTP 201)."""
        payload = {
            "study_area_id": "kerala-floods-2018",
            "reference_date": "2018-08-08",
            "comparison_date": "2018-08-16",
        }
        status, _, body, _ = self.call_api("POST", "/api/investigations", body=payload, auth=True)
        self.assertEqual(status, 201)
        self.assertTrue(body["investigation_id"].startswith("INV-2026-KER-"))

    def test_valid_client_header_allows_evaluation(self):
        """Valid X-API-Key allows evaluation mutation (HTTP 200)."""
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

    def test_all_public_get_endpoints_require_no_auth(self):
        """All read-only GET endpoints must remain accessible without any authentication."""
        public_endpoints = [
            "/api/health",
            "/api/study-areas",
            "/api/study-areas/kerala-floods-2018",
            "/api/study-areas/kerala-floods-2018/acquisitions",
            "/api/investigations/INV-2026-KER-001",
            "/api/investigations/INV-2026-KER-001/evaluation",
            "/api/investigations/INV-2026-KER-001/layers",
            "/api/investigations/INV-2026-KER-001/layers/change-mask",
            "/api/investigations/INV-2026-KER-001/ledger",
            "/api/investigations/INV-2026-KER-001/ledger/download",
            "/api/investigations/INV-2026-KER-001/report",
        ]
        for path in public_endpoints:
            status, _, _, _ = self.call_api("GET", path, auth=False)
            self.assertEqual(status, 200, f"Public GET endpoint {path} failed without auth")

    def test_zero_secrets_in_responses(self):
        """The secret API key must never be printed or leaked in any response text or schema."""
        status, _, _, raw = self.call_api("POST", "/api/investigations", body={}, auth=False)
        self.assertNotIn(TEST_API_KEY, raw)

        status_oa, _, _, raw_oa = self.call_api("GET", "/openapi.json", auth=False)
        self.assertEqual(status_oa, 200)
        self.assertNotIn(TEST_API_KEY, raw_oa)

    def test_openapi_security_scheme_declared(self):
        """OpenAPI schema must declare APIKeyHeader for POST endpoints and none for GET endpoints."""
        status, _, schema, _ = self.call_api("GET", "/openapi.json", auth=False)
        self.assertEqual(status, 200)

        sec_schemes = schema.get("components", {}).get("securitySchemes", {})
        self.assertIn("APIKeyHeader", sec_schemes)
        self.assertEqual(sec_schemes["APIKeyHeader"]["type"], "apiKey")
        self.assertEqual(sec_schemes["APIKeyHeader"]["name"], "X-API-Key")

        # Verify POST routes require it
        post_inv_sec = schema["paths"]["/api/investigations"]["post"].get("security")
        self.assertEqual(post_inv_sec, [{"APIKeyHeader": []}])

        # Verify GET routes do not require it
        get_report_sec = schema["paths"]["/api/investigations/{investigation_id}/report"]["get"].get("security")
        self.assertIsNone(get_report_sec)

