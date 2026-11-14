"""
Tests for Task 5: Backend Security Hardening
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
Covers SEC-01 (CORS), SEC-02 (Global Exception Handlers), SEC-03 (Security Headers),
SEC-04 (Dynamic Auth Config), and SEC-05 (Boundary Validation).
"""

import os
from unittest.mock import patch

from tests.conftest_base import BaseTestCase, TEST_API_KEY
from app.dependencies import get_server_api_key


class TestBackendSecurityHardening(BaseTestCase):

    # -------------------------------------------------------------------------
    # SEC-03: Security Headers Middleware
    # -------------------------------------------------------------------------
    def test_security_headers_present(self):
        """Responses must include X-Content-Type-Options, X-Frame-Options, Referrer-Policy, and CSP."""
        status, headers, body, _ = self.call_api("GET", "/api/health", auth=False)
        self.assertEqual(status, 200)

        # Headers may be lowercased by ASGI dispatcher
        lower_headers = {k.lower(): v for k, v in headers.items()}

        self.assertIn("x-content-type-options", lower_headers)
        self.assertEqual(lower_headers["x-content-type-options"], "nosniff")

        self.assertIn("x-frame-options", lower_headers)
        self.assertEqual(lower_headers["x-frame-options"], "SAMEORIGIN")

        self.assertIn("referrer-policy", lower_headers)
        self.assertEqual(lower_headers["referrer-policy"], "strict-origin-when-cross-origin")

        self.assertIn("content-security-policy", lower_headers)
        csp = lower_headers["content-security-policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("'unsafe-inline'", csp)  # Required for printable report & print triggers

    # -------------------------------------------------------------------------
    # SEC-01: Explicit CORS Configuration
    # -------------------------------------------------------------------------
    def test_cors_allowed_development_origin(self):
        """Explicit development origins (e.g. Vite 5173, Next 3000) receive CORS headers."""
        status, headers, _, _ = self.call_api(
            "GET",
            "/api/health",
            headers={"Origin": "http://localhost:5173"},
            auth=False,
        )
        self.assertEqual(status, 200)
        lower_headers = {k.lower(): v for k, v in headers.items()}
        self.assertEqual(lower_headers.get("access-control-allow-origin"), "http://localhost:5173")

        # Test another trusted dev origin
        status, headers, _, _ = self.call_api(
            "GET",
            "/api/health",
            headers={"Origin": "http://localhost:3000"},
            auth=False,
        )
        self.assertEqual(status, 200)
        lower_headers = {k.lower(): v for k, v in headers.items()}
        self.assertEqual(lower_headers.get("access-control-allow-origin"), "http://localhost:3000")

    def test_cors_disallowed_origin_rejected(self):
        """Untrusted or malicious origins must NOT receive Access-Control-Allow-Origin."""
        status, headers, _, _ = self.call_api(
            "GET",
            "/api/health",
            headers={"Origin": "https://malicious-attacker.com"},
            auth=False,
        )
        self.assertEqual(status, 200)
        lower_headers = {k.lower(): v for k, v in headers.items()}
        self.assertNotIn("access-control-allow-origin", lower_headers)

    def test_cors_no_credentials(self):
        """Header-based API-key auth must not enable allow_credentials=True in CORS."""
        status, headers, _, _ = self.call_api(
            "GET",
            "/api/health",
            headers={"Origin": "http://localhost:5173"},
            auth=False,
        )
        self.assertEqual(status, 200)
        lower_headers = {k.lower(): v for k, v in headers.items()}
        self.assertNotEqual(lower_headers.get("access-control-allow-credentials"), "true")

    # -------------------------------------------------------------------------
    # SEC-02: Global Exception Handler & Starlette HTTP Exception Handler
    # -------------------------------------------------------------------------
    def test_route_not_found_returns_standard_3_field_schema(self):
        """Request to unknown route returns HTTP 404 with standard PRD Section 8 3-field schema."""
        status, _, body, _ = self.call_api("GET", "/api/nonexistent-route-endpoint-xyz", auth=False)
        self.assertEqual(status, 404)
        self.assertIn("code", body)
        self.assertIn("message", body)
        self.assertIn("suggested_action", body)
        self.assertEqual(body["code"], "NOT_FOUND")

    def test_method_not_allowed_returns_standard_3_field_schema(self):
        """Request with unallowed method returns HTTP 405 with standard 3-field schema."""
        status, _, body, _ = self.call_api("DELETE", "/api/health", auth=False)
        self.assertEqual(status, 405)
        self.assertIn("code", body)
        self.assertIn("message", body)
        self.assertIn("suggested_action", body)
        self.assertEqual(body["code"], "METHOD_NOT_ALLOWED")

    def test_global_exception_handler_catches_unhandled_error_without_leak(self):
        """Unhandled exceptions return 500 INTERNAL_SERVER_ERROR without leaking tracebacks or paths."""
        with patch("app.services.study_area_service.get_all_study_areas", side_effect=RuntimeError("Secret internal error")):
            status, _, body, raw_text = self.call_api("GET", "/api/study-areas", auth=False)

        self.assertEqual(status, 500)
        self.assertEqual(body["code"], "INTERNAL_SERVER_ERROR")
        self.assertIn("unexpected server error", body["message"])
        self.assertIn("suggested_action", body)

        # Zero leaks of traceback, internal file paths, or exception text to client
        self.assertNotIn("Secret internal error", raw_text)
        self.assertNotIn("Traceback", raw_text)
        self.assertNotIn("study_area_service.py", raw_text)

    # -------------------------------------------------------------------------
    # SEC-04: Auth Config & Dynamic .env Check
    # -------------------------------------------------------------------------
    def test_auth_get_server_api_key_returns_clean_key(self):
        """get_server_api_key retrieves trimmed environment key without hardcoded defaults."""
        os.environ["BHNMISNTRA_API_KEY"] = "  test-active-key  "
        key = get_server_api_key()
        self.assertEqual(key, "test-active-key")

    # -------------------------------------------------------------------------
    # SEC-05: Boundary Validation for Investigation ID
    # -------------------------------------------------------------------------
    def test_investigation_id_valid_pattern_unknown_returns_404(self):
        """Syntactically valid but unknown investigation ID preserves the 404 INVESTIGATION_NOT_FOUND contract."""
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-UNKNOWN-999", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")

    def test_investigation_id_invalid_characters_rejected_422(self):
        """Unsafe characters and path traversal sequences in investigation_id are rejected with 422."""
        bad_ids = [
            "INV$SPECIAL",
            "INV!BAD",
            "INV SPACE",
            "INV;DROP_TABLE",
        ]
        for bad_id in bad_ids:
            status, _, body, _ = self.call_api("GET", f"/api/investigations/{bad_id}", auth=False)
            self.assertEqual(status, 422, f"Expected 422 for bad id '{bad_id}', got {status}")
            self.assertEqual(body["code"], "INVALID_REQUEST_PARAMETERS")

    def test_investigation_report_boundary_validation(self):
        """Report endpoint enforces boundary validation and preserves 404 for unknown IDs."""
        # 404 for valid format but non-existent
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-UNKNOWN-999/report", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")

        # 422 for invalid format
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV$BAD/report", auth=False)
        self.assertEqual(status, 422)
        self.assertEqual(body["code"], "INVALID_REQUEST_PARAMETERS")

    def test_ledger_endpoints_boundary_validation(self):
        """Ledger and download endpoints enforce boundary validation and preserve 404."""
        # Ledger GET
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-UNKNOWN-999/ledger", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")

        status, _, body, _ = self.call_api("GET", "/api/investigations/INV$BAD/ledger", auth=False)
        self.assertEqual(status, 422)
        self.assertEqual(body["code"], "INVALID_REQUEST_PARAMETERS")

        # Ledger Download GET
        status, _, body, _ = self.call_api("GET", "/api/investigations/INV-UNKNOWN-999/ledger/download", auth=False)
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")

        status, _, body, _ = self.call_api("GET", "/api/investigations/INV$BAD/ledger/download", auth=False)
        self.assertEqual(status, 422)
        self.assertEqual(body["code"], "INVALID_REQUEST_PARAMETERS")

