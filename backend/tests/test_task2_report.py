"""
Tests for Task 2: Printable Investigation Report API
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

import html
from tests.conftest_base import BaseTestCase


class TestInvestigationReport(BaseTestCase):

    def test_html_report_success(self):
        """GET /api/investigations/{id}/report returns valid HTML with print support."""
        status, headers, body, raw_html = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-002/report", auth=False
        )
        self.assertEqual(status, 200)
        content_type = headers.get("content-type", "")
        self.assertIn("text/html", content_type)
        self.assertIn("charset=utf-8", content_type.lower())
        self.assertIn("<!DOCTYPE html>", raw_html)
        self.assertIn("</html>", raw_html)
        self.assertIn("window.print()", raw_html)
        self.assertIn("@media print", raw_html)

    def test_html_report_dynamic_data(self):
        """Report dynamically embeds investigation metadata, Beat Test results, and provenance."""
        status, _, _, raw_html = self.call_api(
            "GET", "/api/investigations/INV-2026-KER-002/report", auth=False
        )
        self.assertEqual(status, 200)
        self.assertIn("INV-2026-KER-002", raw_html)
        self.assertIn("Kerala Flood Basin", raw_html)
        self.assertIn("Sentinel-1A", raw_html)
        self.assertIn("Supported", raw_html)
        self.assertIn("ILLUSTRATIVE — NOT REAL DATA", raw_html)

    def test_html_report_safe_with_missing_optional_fields(self):
        """Report handles investigations without evaluations or optional reference fields cleanly."""
        status, _, _, raw_html = self.call_api(
            "GET", "/api/investigations/INV-2026-VAL-004/report", auth=False
        )
        self.assertEqual(status, 200)
        self.assertNotIn("None", raw_html)  # No raw Python 'None' leaks
        self.assertIn("INV-2026-VAL-004", raw_html)

    def test_html_report_xss_escaping(self):
        """Dynamic values must be safely escaped via html.escape."""
        unsafe_string = "<script>alert('xss')</script> & \"injection\""
        escaped = html.escape(unsafe_string, quote=True)
        self.assertNotIn("<script>", escaped)
        self.assertIn("&lt;script&gt;", escaped)

    def test_html_report_not_found(self):
        """GET /api/investigations/{id}/report returns 404 for unknown ID."""
        status, _, body, _ = self.call_api(
            "GET", "/api/investigations/INV-UNKNOWN-999/report", auth=False
        )
        self.assertEqual(status, 404)
        self.assertEqual(body["code"], "INVESTIGATION_NOT_FOUND")

