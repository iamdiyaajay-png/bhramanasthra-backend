"""
Layer Service for BHnMISnTRA
Handles map layer asset resolution, validation, path-traversal prevention, and file serving.
NASA Space Apps Challenge 2026: Dancing with the SARs
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import re

from app.schemas.errors import AppException
from app.services.investigation_service import _load_all_investigations

# Root directory for persistent layer assets
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
LAYERS_DIR = OUTPUTS_DIR / "layers"

LAYERS_DIR.mkdir(parents=True, exist_ok=True)

# PRD v3 Supported Canonical Map Layers
CANONICAL_LAYERS = {
    "change-mask": {
        "name": "Change Detection Mask",
        "description": "Thresholded dual-pol SAR amplitude change mask identifying detected surface change extent.",
        "media_type": "application/geo+json",
        "extensions": [".geojson", ".json", ".png", ".tif", ".tiff"],
    },
    "continuous": {
        "name": "Continuous Amplitude Difference",
        "description": "Continuous SAR backscatter intensity difference (Delta dB) across the monitored study area.",
        "media_type": "application/geo+json",
        "extensions": [".geojson", ".json", ".png", ".tif", ".tiff"],
    },
    "reference": {
        "name": "Reference Baseline Pass",
        "description": "Pre-event baseline satellite acquisition observation extent and backscatter calibration.",
        "media_type": "application/geo+json",
        "extensions": [".geojson", ".json", ".png", ".tif", ".tiff"],
    },
    "comparison": {
        "name": "Comparison Event Pass",
        "description": "Post-event / event-peak satellite acquisition observation extent and backscatter response.",
        "media_type": "application/geo+json",
        "extensions": [".geojson", ".json", ".png", ".tif", ".tiff"],
    },
}

# Alias mapping for developer & frontend compatibility
LAYER_ALIASES = {
    "change-mask": "change-mask",
    "change_mask": "change-mask",
    "mask": "change-mask",
    "continuous": "continuous",
    "continuous-layer": "continuous",
    "continuous_layer": "continuous",
    "difference": "continuous",
    "reference": "reference",
    "reference-sar": "reference",
    "reference_sar": "reference",
    "baseline": "reference",
    "comparison": "comparison",
    "comparison-sar": "comparison",
    "comparison_sar": "comparison",
    "event": "comparison",
}

# Investigation ID security pattern (defense-in-depth against path traversal)
INVESTIGATION_ID_PATTERN = re.compile(r"^INV-\d{4}-[A-Z0-9]+-\d{3}$")


def normalize_and_validate_layer_name(layer: str) -> str:
    """
    Validates layer name against canonical whitelist. Rejects path traversal and unsupported names.
    """
    if not layer or not isinstance(layer, str):
        raise AppException(
            status_code=400,
            code="UNSUPPORTED_LAYER",
            message="Layer name cannot be empty.",
            suggested_action="Specify one of the supported layers: 'change-mask', 'continuous', 'reference', 'comparison'.",
        )

    # Sanitize and detect traversal patterns early
    cleaned = layer.strip().lower()
    if "/" in cleaned or "\\" in cleaned or ".." in cleaned:
        raise AppException(
            status_code=400,
            code="INVALID_LAYER_NAME",
            message=f"Invalid layer path '{layer}'. Directory traversal sequences are strictly prohibited.",
            suggested_action="Use standard layer names: 'change-mask', 'continuous', 'reference', 'comparison'.",
        )

    canonical = LAYER_ALIASES.get(cleaned)
    if not canonical or canonical not in CANONICAL_LAYERS:
        supported_list = sorted(list(CANONICAL_LAYERS.keys()))
        raise AppException(
            status_code=400,
            code="UNSUPPORTED_LAYER",
            message=f"Layer '{layer}' is not supported. Supported layers are: {', '.join(supported_list)}.",
            suggested_action=f"Select one of the valid map layers: {', '.join(supported_list)}.",
        )

    return canonical


def get_layer_asset_path(investigation_id: str, layer: str) -> Tuple[Path, str]:
    """
    Resolves the physical file path for the requested investigation layer asset.
    Validates investigation existence, layer name, and directory safety.
    Returns (file_path, content_type).
    """
    # 1. Validate Investigation ID existence
    investigations_db = _load_all_investigations()
    if investigation_id not in investigations_db:
        raise AppException(
            status_code=404,
            code="INVESTIGATION_NOT_FOUND",
            message=f"Investigation '{investigation_id}' was not found in the platform registry.",
            suggested_action="Verify the investigation ID or create a new investigation with POST /api/investigations.",
        )

    # Security check on investigation ID string format
    if not INVESTIGATION_ID_PATTERN.match(investigation_id):
        raise AppException(
            status_code=400,
            code="INVALID_INVESTIGATION_ID",
            message=f"Malformed investigation ID '{investigation_id}'. Must match standard pattern 'INV-YYYY-XXX-NNN'.",
            suggested_action="Check the investigation ID format.",
        )

    # 2. Validate and normalize layer name
    canonical_layer = normalize_and_validate_layer_name(layer)
    layer_meta = CANONICAL_LAYERS[canonical_layer]

    # 3. Construct safe target path
    investigation_layer_dir = LAYERS_DIR / investigation_id

    # Security check: verify path is strictly inside LAYERS_DIR
    try:
        resolved_dir = investigation_layer_dir.resolve()
        if not resolved_dir.is_relative_to(LAYERS_DIR.resolve()):
            raise AppException(
                status_code=400,
                code="PATH_TRAVERSAL_DETECTED",
                message="Directory traversal path detected and blocked.",
                suggested_action="Access resources through standard platform API endpoints.",
            )
    except (ValueError, RuntimeError):
        raise AppException(
            status_code=400,
            code="INVALID_PATH",
            message="Invalid path specification.",
            suggested_action="Check request parameters.",
        )

    # 4. Search for existing asset across supported extensions
    matched_file: Optional[Path] = None
    media_type = layer_meta["media_type"]

    for ext in layer_meta["extensions"]:
        candidate = investigation_layer_dir / f"{canonical_layer}{ext}"
        if candidate.is_file():
            matched_file = candidate
            if ext == ".geojson":
                media_type = "application/geo+json"
            elif ext == ".json":
                media_type = "application/json"
            elif ext == ".png":
                media_type = "image/png"
            elif ext in [".tif", ".tiff"]:
                media_type = "image/tiff"
            break

    if not matched_file:
        raise AppException(
            status_code=404,
            code="LAYER_ASSET_NOT_FOUND",
            message=(
                f"Map layer asset '{canonical_layer}' for investigation '{investigation_id}' "
                f"has not been generated or is not present on disk."
            ),
            suggested_action=(
                "Wait for Member 1's SAR processing pipeline to produce this layer asset, "
                "or verify that the investigation has been processed."
            ),
        )

    return matched_file, media_type


def list_investigation_layers(investigation_id: str) -> Dict[str, Any]:
    """
    Returns the manifest of available map layers for an investigation.
    """
    investigations_db = _load_all_investigations()
    if investigation_id not in investigations_db:
        raise AppException(
            status_code=404,
            code="INVESTIGATION_NOT_FOUND",
            message=f"Investigation '{investigation_id}' was not found in the platform registry.",
            suggested_action="Verify the investigation ID or create a new investigation with POST /api/investigations.",
        )

    investigation_layer_dir = LAYERS_DIR / investigation_id
    layers_manifest = []

    for canonical_name, meta in CANONICAL_LAYERS.items():
        is_available = False
        detected_ext = None
        for ext in meta["extensions"]:
            if (investigation_layer_dir / f"{canonical_name}{ext}").is_file():
                is_available = True
                detected_ext = ext
                break

        layers_manifest.append({
            "layer": canonical_name,
            "name": meta["name"],
            "description": meta["description"],
            "available": is_available,
            "format": detected_ext[1:] if detected_ext else "unavailable",
            "endpoint": f"/api/investigations/{investigation_id}/layers/{canonical_name}",
            "data_provenance": "ILLUSTRATIVE — NOT REAL DATA",
        })

    return {
        "investigation_id": investigation_id,
        "total_layers": len(CANONICAL_LAYERS),
        "available_layers_count": sum(1 for l in layers_manifest if l["available"]),
        "layers": layers_manifest,
        "data_provenance": "ILLUSTRATIVE — NOT REAL DATA",
    }

