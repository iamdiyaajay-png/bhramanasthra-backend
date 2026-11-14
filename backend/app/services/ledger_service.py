"""
Evidence Ledger Service
Handles persistent storage, retrieval, and file export for Evidence Ledgers.
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
"""

import json
from pathlib import Path
from typing import Tuple

from app.schemas.investigation import EvidenceLedgerRecord
from app.schemas.errors import AppException
from app.services.investigation_service import _load_all_investigations, LEDGERS_DIR


def get_ledger_by_investigation_id(investigation_id: str) -> EvidenceLedgerRecord:
    """
    Retrieves the complete Evidence Ledger record for an investigation.
    Reads from persistent storage.
    """
    investigations_db = _load_all_investigations()

    if investigation_id not in investigations_db:
        raise AppException(
            status_code=404,
            code="INVESTIGATION_NOT_FOUND",
            message=f"Investigation '{investigation_id}' was not found in the platform registry.",
            suggested_action="Verify the investigation ID or create a new investigation with POST /api/investigations.",
        )

    record = investigations_db[investigation_id]
    if "ledger" not in record:
        raise AppException(
            status_code=404,
            code="LEDGER_NOT_FOUND",
            message=f"Evidence Ledger for investigation '{investigation_id}' could not be located.",
            suggested_action="Check if the investigation was properly initialized.",
        )

    return EvidenceLedgerRecord(**record["ledger"])


def get_ledger_file_for_download(investigation_id: str) -> Tuple[Path, str]:
    """
    Returns the file path and download filename for an investigation's Evidence Ledger.
    Ensures the standalone JSON file exists on disk in outputs/ledgers/.
    """
    # 1. Verify investigation exists and retrieve ledger
    ledger_record = get_ledger_by_investigation_id(investigation_id)

    # 2. Ensure the outputs/ledgers directory exists
    LEDGERS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = LEDGERS_DIR / f"{investigation_id}.json"

    # Always ensure the file on disk matches the persistent database
    if not file_path.exists():
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(ledger_record.model_dump(), f, indent=2)

    download_filename = f"evidence-ledger-{investigation_id}.json"
    return file_path, download_filename

