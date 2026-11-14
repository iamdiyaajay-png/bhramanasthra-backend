"""
Tests for Repair 4: Validation Error Message Cleanup
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)

Verifies audit Finding 7:
- Messages ending without a period receive exactly one final period.
- Messages ending with one period retain exactly one period (no double periods '..').
- Messages ending with multiple periods ('...') are trimmed to exactly one period.
- Missing or empty validation messages receive the sensible default 'Invalid request parameters.'.
- PRD Section 8 error response contract ({code, message, suggested_action}, status 422) is preserved.
- Existing API validation behavior remains fully backward-compatible.
"""

import json
from fastapi.exceptions import RequestValidationError
from tests.conftest_base import BaseTestCase
from app.schemas.errors import validation_exception_handler


class TestRepair4ValidationCleanup(BaseTestCase):
    """
    Test suite for Repair 4: validation error message period normalization and defaults.
    Guarantees 100% data isolation via BaseTestCase sandbox.
    """

    def test_message_ending_without_period_gets_one_period(self):
        """1. A validation message ending without a period gets exactly one period."""
        exc = RequestValidationError(
            [{"loc": ("body", "field_name"), "msg": "Input should be a valid string", "type": "string_type"}]
        )
        response = validation_exception_handler(None, exc)
        self.assertEqual(response.status_code, 422)

        data = json.loads(response.body.decode("utf-8"))
        message = data["message"]
        self.assertTrue(message.endswith("."), f"Message must end with a period: '{message}'")
        self.assertFalse(message.endswith(".."), f"Message must not end with double periods: '{message}'")
        self.assertEqual(message, "Validation failed for 'body.field_name': Input should be a valid string.")

    def test_message_ending_with_one_period_gets_only_one(self):
        """2. A validation message ending with one period still gets only one (no double period '..')."""
        exc = RequestValidationError(
            [{"loc": ("body", "study_area_id"), "msg": "Field required.", "type": "missing"}]
        )
        response = validation_exception_handler(None, exc)
        self.assertEqual(response.status_code, 422)

        data = json.loads(response.body.decode("utf-8"))
        message = data["message"]
        self.assertTrue(message.endswith("."), f"Message must end with a period: '{message}'")
        self.assertFalse(message.endswith(".."), f"Message must not end with double periods: '{message}'")
        self.assertEqual(message, "Validation failed for 'body.study_area_id': Field required.")

    def test_message_ending_with_multiple_periods_gets_only_one(self):
        """3. A validation message ending with multiple periods ('...') gets trimmed to exactly one."""
        exc = RequestValidationError(
            [{"loc": ("body", "date"), "msg": "Invalid date format specified....", "type": "value_error"}]
        )
        response = validation_exception_handler(None, exc)
        self.assertEqual(response.status_code, 422)

        data = json.loads(response.body.decode("utf-8"))
        message = data["message"]
        self.assertTrue(message.endswith("."), f"Message must end with a period: '{message}'")
        self.assertFalse(message.endswith(".."), f"Message must not end with multiple periods: '{message}'")
        self.assertEqual(message, "Validation failed for 'body.date': Invalid date format specified.")

    def test_missing_or_empty_validation_message_uses_default(self):
        """4. Missing, empty, or whitespace validation message uses sensible default."""
        # 4a. None / missing msg
        exc_none = RequestValidationError([{"loc": ("body", "unknown_param")}])
        resp_none = validation_exception_handler(None, exc_none)
        data_none = json.loads(resp_none.body.decode("utf-8"))
        self.assertEqual(data_none["message"], "Validation failed for 'body.unknown_param': Invalid request parameters.")
        self.assertFalse(data_none["message"].endswith(".."))

        # 4b. Empty string msg
        exc_empty = RequestValidationError([{"loc": ("body", "param"), "msg": ""}])
        resp_empty = validation_exception_handler(None, exc_empty)
        data_empty = json.loads(resp_empty.body.decode("utf-8"))
        self.assertEqual(data_empty["message"], "Validation failed for 'body.param': Invalid request parameters.")

        # 4c. Only periods and spaces in msg
        exc_dots = RequestValidationError([{"loc": ("body", "param"), "msg": " ... "}])
        resp_dots = validation_exception_handler(None, exc_dots)
        data_dots = json.loads(resp_dots.body.decode("utf-8"))
        self.assertEqual(data_dots["message"], "Validation failed for 'body.param': Invalid request parameters.")

        # 4d. Empty errors list []
        exc_empty_list = RequestValidationError([])
        resp_empty_list = validation_exception_handler(None, exc_empty_list)
        data_empty_list = json.loads(resp_empty_list.body.decode("utf-8"))
        self.assertEqual(data_empty_list["message"], "Validation failed for '': Invalid request parameters.")

    def test_error_response_structure_remains_unchanged(self):
        """5. Error response preserves PRD Section 8 3-field standard schema and status 422."""
        exc = RequestValidationError([{"loc": ("body", "test_field"), "msg": "Sample error"}])
        response = validation_exception_handler(None, exc)
        self.assertEqual(response.status_code, 422)

        data = json.loads(response.body.decode("utf-8"))
        self.assertEqual(set(data.keys()), {"code", "message", "suggested_action"})
        self.assertEqual(data["code"], "INVALID_REQUEST_PARAMETERS")
        self.assertIn("/docs", data["suggested_action"])

    def test_live_api_endpoint_validation_error_has_no_double_period(self):
        """6. Live API endpoint (POST /api/investigations) returns 422 with no double period."""
        # Omit required fields (reference_date, comparison_date)
        payload = {"study_area_id": "kerala-floods-2018"}
        status, _, body, _ = self.call_api("POST", "/api/investigations", body=payload, auth=True)
        self.assertEqual(status, 422)
        self.assertEqual(body["code"], "INVALID_REQUEST_PARAMETERS")

        message = body["message"]
        self.assertTrue(message.endswith("."), f"API error message must end with a period: '{message}'")
        self.assertFalse(message.endswith(".."), f"API error message must not have double periods: '{message}'")

