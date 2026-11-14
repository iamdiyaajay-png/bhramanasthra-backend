"""
BHnMISnTRA Test Base & Utilities
NASA Space Apps Challenge 2026: Dancing with the SARs
Provides completely isolated in-process ASGI testing with zero disk pollution.
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# Ensure backend root is on sys.path
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.main import app
import app.services.investigation_service as inv_service
import app.services.evidence_service as ev_service
import app.services.ledger_service as led_service
import app.services.layer_service as lay_service

TEST_API_KEY = "bhnmistra-test-runner-ephemeral-key"


async def request_asgi(method: str, path: str, headers: dict = None, body: dict = None):
    """
    Standard ASGI 3 in-process request dispatcher.
    Zero external network sockets, zero port contention.
    """
    headers_list = []
    if headers:
        for k, v in headers.items():
            headers_list.append((k.lower().encode("latin1"), str(v).encode("latin1")))

    body_bytes = json.dumps(body).encode("utf-8") if body is not None else b""
    if body is not None:
        headers_list.append((b"content-type", b"application/json"))
        headers_list.append((b"content-length", str(len(body_bytes)).encode("latin1")))

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "raw_path": path.encode("latin1"),
        "query_string": b"",
        "headers": headers_list,
        "server": ("127.0.0.1", 80),
        "client": ("127.0.0.1", 54321),
        "http_version": "1.1",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
    }

    sent_meta = {}
    response_chunks = []
    received = False

    async def receive():
        nonlocal received
        if not received:
            received = True
            return {
                "type": "http.request",
                "body": body_bytes,
                "more_body": False,
            }
        return {"type": "http.disconnect"}

    async def send(message):
        if message["type"] == "http.response.start":
            sent_meta["status"] = message["status"]
            sent_meta["headers"] = {
                k.decode("latin1"): v.decode("latin1") for k, v in message.get("headers", [])
            }
        elif message["type"] == "http.response.body":
            response_chunks.append(message.get("body", b""))

    try:
        await app(scope, receive, send)
    except Exception:
        # Starlette ServerErrorMiddleware re-raises unhandled 500 exceptions after sending the response
        pass

    raw_text = b"".join(response_chunks).decode("utf-8", errors="replace")
    try:
        parsed_json = json.loads(raw_text)
    except Exception:
        parsed_json = raw_text

    return sent_meta.get("status", 500), sent_meta.get("headers", {}), parsed_json, raw_text


class BaseTestCase(unittest.TestCase):
    """
    Base test case that guarantees 100% data isolation.
    Every test method runs inside a private temporary directory seeded with initial data copies.
    The real backend/data and backend/outputs directories are NEVER modified.
    """

    def setUp(self):
        # 1. Create temporary directory
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self._temp_dir_obj.name)

        self.tmp_data = self.temp_dir / "data"
        self.tmp_outputs = self.temp_dir / "outputs"
        self.tmp_ledgers = self.tmp_outputs / "ledgers"
        self.tmp_layers = self.tmp_outputs / "layers"

        self.tmp_data.mkdir(parents=True, exist_ok=True)
        self.tmp_ledgers.mkdir(parents=True, exist_ok=True)
        self.tmp_layers.mkdir(parents=True, exist_ok=True)

        # 2. Copy seed data into temporary directory
        real_data = _backend_root / "data"
        real_outputs = _backend_root / "outputs"

        if (real_data / "study_areas.json").is_file():
            shutil.copy2(real_data / "study_areas.json", self.tmp_data / "study_areas.json")
        if (real_data / "acquisitions.json").is_file():
            shutil.copy2(real_data / "acquisitions.json", self.tmp_data / "acquisitions.json")
        if (real_data / "investigations.json").is_file():
            shutil.copy2(real_data / "investigations.json", self.tmp_data / "investigations.json")

        real_ledgers = real_outputs / "ledgers"
        if real_ledgers.is_dir():
            for f in real_ledgers.glob("*.json"):
                shutil.copy2(f, self.tmp_ledgers / f.name)

        real_layers = real_outputs / "layers"
        if real_layers.is_dir():
            for d in real_layers.iterdir():
                if d.is_dir():
                    shutil.copytree(d, self.tmp_layers / d.name)

        # 3. Save original service paths
        self._orig_inv_file = inv_service.INVESTIGATIONS_FILE
        self._orig_data_dir = inv_service.DATA_DIR
        self._orig_outputs_dir = inv_service.OUTPUTS_DIR
        self._orig_inv_ledgers = inv_service.LEDGERS_DIR
        self._orig_ev_ledgers = ev_service.LEDGERS_DIR
        self._orig_led_ledgers = led_service.LEDGERS_DIR
        self._orig_lay_layers = lay_service.LAYERS_DIR
        self._orig_lay_outputs = lay_service.OUTPUTS_DIR

        # 4. Patch service paths to point to temporary directory
        inv_service.INVESTIGATIONS_FILE = self.tmp_data / "investigations.json"
        inv_service.DATA_DIR = self.tmp_data
        inv_service.OUTPUTS_DIR = self.tmp_outputs
        inv_service.LEDGERS_DIR = self.tmp_ledgers
        ev_service.LEDGERS_DIR = self.tmp_ledgers
        led_service.LEDGERS_DIR = self.tmp_ledgers
        lay_service.LAYERS_DIR = self.tmp_layers
        lay_service.OUTPUTS_DIR = self.tmp_outputs

        # 5. Manage environment variable for authentication
        self._orig_env_key = os.environ.get("BHNMISNTRA_API_KEY")
        os.environ["BHNMISNTRA_API_KEY"] = TEST_API_KEY

    def tearDown(self):
        # 1. Restore original service paths
        inv_service.INVESTIGATIONS_FILE = self._orig_inv_file
        inv_service.DATA_DIR = self._orig_data_dir
        inv_service.OUTPUTS_DIR = self._orig_outputs_dir
        inv_service.LEDGERS_DIR = self._orig_inv_ledgers
        ev_service.LEDGERS_DIR = self._orig_ev_ledgers
        led_service.LEDGERS_DIR = self._orig_led_ledgers
        lay_service.LAYERS_DIR = self._orig_lay_layers
        lay_service.OUTPUTS_DIR = self._orig_lay_outputs

        # 2. Restore original environment variable
        if self._orig_env_key is None:
            os.environ.pop("BHNMISNTRA_API_KEY", None)
        else:
            os.environ["BHNMISNTRA_API_KEY"] = self._orig_env_key

        # 3. Clean up temporary directory
        try:
            self._temp_dir_obj.cleanup()
        except Exception:
            pass

    def call_api(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        auth: bool = True,
    ) -> Tuple[int, Dict[str, str], Any, str]:
        """
        Executes an in-process ASGI request against the FastAPI application.
        Automatically injects test authentication header when auth=True and method is POST/PUT/DELETE.
        """
        req_headers = dict(headers or {})
        if auth and "x-api-key" not in {k.lower(): v for k, v in req_headers.items()}:
            req_headers["X-API-Key"] = TEST_API_KEY

        return asyncio.run(request_asgi(method, path, headers=req_headers, body=body))
