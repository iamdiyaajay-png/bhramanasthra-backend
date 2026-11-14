# BHRAMANASTHRA (BHnMISnTRA) — Repository Integration Handoff Document

**Project**: BHRAMANASTHRA — Radar Evidence & Surface Change Platform  
**Challenge**: NASA Space Apps Challenge 2026 — *"Dancing with the SARs"*  
**Standard**: NASA Space Apps PRD v3  
**Architecture Lead**: Gemini 3.8 Flash High  
**Status**: Backend & Evidence Ledger Locked (91 / 91 Tests Passing, 100% Data Isolation)  
**Date**: November 2026  

---

## 1. Repository Purpose & Technology Stack

### Purpose
BHRAMANASTHRA is an enterprise-grade scientific backend and Evidence Ledger platform designed to ingest Synthetic Aperture Radar (SAR) satellite data (Copernicus Sentinel-1 and NASA-ISRO NISAR), detect surface changes (flood inundation and landslide scarring), evaluate temporal persistence using the **SAR Beat Test** (PRD Section 9), and produce traceable **Evidence Ledgers** (PRD Section 13) and audit-ready printable reports.

### Technology Stack
- **Language**: Python 3.12+ (tested on Python 3.12.10)
- **API Framework**: FastAPI 0.162.6 (Starlette 1.10.0 ASGI)
- **ASGI Server**: Uvicorn 0.54.0 (Standard)
- **Data Validation & Schemas**: Pydantic 2.14.3
- **Configuration & Environment**: python-dotenv 1.2.4
- **Form Handling**: python-multipart 0.0.33
- **Testing Engine**: Python Standard Library `unittest` (in-process ASGI dispatcher, 100% sandboxed temporary filesystem, zero network contention, zero external test dependencies)
- **Storage Layer**: Atomic JSON document persistence (`os.replace`, `os.fsync`) with automated `.corrupt.<timestamp>` backups and per-study-area sequence ID allocators

---

## 2. Complete Directory Structure

```text
nasa/
├── .gitignore                          # Protects .env, .env.*, .venv, caches, artifacts
├── AGENTS.md                           # Multi-agent directives & RACI role boundaries
├── GEMINI.md                           # System architect instructions & cheat sheet triggers
├── INTEGRATION_HANDOFF.md              # This integration document
├── backend/
│   ├── .env.example                    # Sample environment template (tracked in git)
│   ├── requirements.txt                # Production backend dependencies
│   ├── app/
│   │   ├── __init__.py                 # Application package init
│   │   ├── main.py                     # FastAPI application factory, CORS, CSP middleware
│   │   ├── dependencies.py             # Header-based API key auth (X-API-Key) & fail-closed guards
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── investigations.py       # Investigation lifecycle, layer serving, report endpoints
│   │   │   ├── ledger.py               # Standalone Evidence Ledger retrieval and download
│   │   │   └── study_areas.py          # Study areas catalog & satellite acquisitions timeline
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── errors.py               # PRD Section 8 standardized 3-field ErrorResponse & handlers
│   │   │   ├── evaluation.py           # Beat Test observations & three-state evaluation schemas
│   │   │   ├── investigation.py        # Investigation creation, detail, and ledger schemas
│   │   │   └── study_area.py           # Study area & satellite acquisition models
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── evidence_service.py     # Beat Test persistence math & three-state label mapping
│   │       ├── investigation_service.py# Investigation lifecycle, atomic writes, sequence ID scanner
│   │       ├── layer_service.py        # Spatial layer resolution, GeoTIFF/GeoJSON MIME streaming
│   │       ├── ledger_service.py       # PRD Section 13 Evidence Ledger generation & download
│   │       ├── report_service.py       # Printable HTML investigation report generator
│   │       └── study_area_service.py   # Catalog query and orbit geometry filtering
│   ├── data/
│   │   ├── acquisitions.json           # Catalog of Sentinel-1 repeat-pass satellite acquisitions
│   │   ├── investigations.json         # Master persistent investigation registry
│   │   └── study_areas.json            # Monitored regions (Kerala, Valencia, Wayanad)
│   ├── outputs/
│   │   ├── layers/
│   │   │   ├── INV-2026-KER-001/       # 4 canonical GeoJSON layers (change-mask, continuous, etc.)
│   │   │   └── INV-2026-KER-002/       # 4 canonical GeoJSON layers
│   │   └── ledgers/                    # Dedicated Evidence Ledger JSON documents (KER-001 to 008, VAL-004)
│   └── tests/
│       ├── __init__.py
│       ├── conftest_base.py            # Sandboxed BaseTestCase & ASGI 3 in-process request dispatcher
│       ├── run_all.py                  # Master test runner with pre/post data footprint hash verification
│       ├── test_phase4_study_areas.py  # Health check & study area endpoints (7 tests)
│       ├── test_phase5_investigations.py # Investigation creation & geometry validation (6 tests)
│       ├── test_phase6_ledger.py       # Evidence Ledger JSON schema & download (6 tests)
│       ├── test_phase7_beat_test.py    # Temporal persistence math & confounders (6 tests)
│       ├── test_phase8_layers.py       # Layer serving & path traversal protection (7 tests)
│       ├── test_task2_report.py        # Printable HTML report generation & XSS sanitization (6 tests)
│       ├── test_task3_auth.py          # API key header authentication & fail-closed 500 (6 tests)
│       ├── test_task5_security.py      # CORS, CSP, exception masking, boundary validation (12 tests)
│       ├── test_repair1_data_safety.py # Corrupt JSON shields, atomic writes, collision guards (6 tests)
│       ├── test_repair2_evaluation_validation.py # Beat Test behavior, non-negative area, notes (12 tests)
│       ├── test_repair3_layers_and_deps.py # python-dotenv dependency, .tif/.tiff dual serving (9 tests)
│       └── test_repair4_validation_cleanup.py # Validation message period normalization (6 tests)
├── brain/                              # Project governance & persistent team memory
│   ├── DECISIONS.md                    # Architecture decision records
│   ├── HANDOFF.md                      # Shift handoff log
│   ├── MAP.md                          # Multi-member system architecture & RACI matrix
│   ├── PREVIOUS_PROJECTS_STUDY.md      # Lessons learned from past hackathons
│   ├── PROJECT.md                      # Mission statement, scientific objectives, and non-goals
│   ├── STATUS.md                       # Master milestone status
│   ├── STATUS_member1_frontend.md      # Member 1 workstream status
│   ├── STATUS_member2_backend.md      # Member 2 workstream status (Complete)
│   ├── STATUS_member3_science_ml.md    # Member 3 workstream status
│   ├── STATUS_member4_qa_docs.md       # Member 4 workstream status
│   └── topics/
│       ├── design/PRODUCTION_PAGES_CHECKLIST.md # 11 mandatory production-grade pages
│       └── operations/RUNBOOK.md       # Operational procedures and deployment guides
└── .agents/skills/                     # Installed agent skills (taste-skill, 21st, headroom, etc.)
```

---

## 3. Main Entry Point & Startup Commands

### Entry Point
- **FastAPI ASGI Instance**: `backend/app/main.py:app`

### Local Development Startup
```powershell
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Start development server with hot-reload
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Health & Documentation Verification
- **API Health Check**: `http://127.0.0.1:8000/api/health`
- **Interactive OpenAPI Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## 4. Dependencies & Version Requirements

From [backend/requirements.txt](file:///c:/Users/jasmi/OneDrive/Documents/nasa/backend/requirements.txt):

```text
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.9.0
python-multipart>=0.0.9
python-dotenv>=1.0.0
```

### Environment Compatibility
- **Python**: $\ge 3.12$
- **Testing**: Zero third-party test runners or libraries required (`pytest`, `requests`, and `httpx` are not required; tests run via Python standard library `unittest` and `asyncio`).

---

## 5. Environment Variables

Configure environment variables in `backend/.env` (or root `.env`). Refer to `backend/.env.example`:

| Variable Name | Required? | Default / Example | Purpose |
|---|---|---|---|
| `BHNMISNTRA_API_KEY` | **YES** (for mutations) | `<64-character-hex-string>` | Server-side master API key used to authenticate mutating endpoints (`POST /api/investigations`, `POST /api/investigations/{id}/evaluate`). Constant-time comparison via `secrets.compare_digest`. Mutations fail closed with HTTP 500 if unconfigured. |
| `BHNMISNTRA_CORS_ORIGINS` | Optional | `http://localhost:5173,http://localhost:3000` | Comma-separated list of additional trusted origins allowed to make browser requests. Header-based auth uses `allow_credentials=False`. |
| `BHNMISNTRA_ENV` | Optional | `development` | Environment mode (`development` or `production`). |

> [!WARNING]
> Never commit actual `.env` files to git. `.gitignore` strictly excludes `.env` and `.env.*` while allowing `.env.example`.

---

## 6. APIs Provided (Exported Routes)

All error responses strictly comply with the **PRD Section 8 Three-Field Format**:
```json
{
  "code": "STRING_ERROR_CODE",
  "message": "Human-readable description ending with exactly one period.",
  "suggested_action": "Actionable guidance for the user or client developer."
}
```

### Public Read-Only Endpoints (Zero Authentication Required)
1. `GET /` — Welcome landing and pointers to API documentation.
2. `GET /api/health` — Platform health check, challenge name, and version.
3. `GET /api/study-areas` — List of all monitored study areas, bounding boxes, and expected behaviors.
4. `GET /api/study-areas/{study_area_id}` — Details for a specific study area.
5. `GET /api/study-areas/{study_area_id}/acquisitions` — Complete timeline of satellite repeat-passes.
6. `GET /api/investigations/{investigation_id}` — Full investigation state, metadata, and status.
7. `GET /api/investigations/{investigation_id}/evaluation` — Beat Test evaluation results, three-state label, and rationale.
8. `GET /api/investigations/{investigation_id}/layers` — Manifest of available canonical map layers and formats.
9. `GET /api/investigations/{investigation_id}/layers/{layer}` — Serves spatial asset (`.geojson`, `.tif`, `.tiff`, `.png`).
10. `GET /api/investigations/{investigation_id}/ledger` — Standalone Evidence Ledger JSON document.
11. `GET /api/investigations/{investigation_id}/ledger/download` — Downloads Evidence Ledger with attachment headers.
12. `GET /api/investigations/{investigation_id}/report` — Self-contained printable HTML audit report.

### Protected Mutation Endpoints (Requires `X-API-Key` Header)
1. `POST /api/investigations` — Creates a new investigation and initializes its Evidence Ledger.
2. `POST /api/investigations/{investigation_id}/evaluate` — Ingests observations, computes Beat Test temporal persistence, and sets the evidence label.

---

## 7. Expected Inputs & Outputs

### 1. Create Investigation (`POST /api/investigations`)
- **Headers**: `X-API-Key: <BHNMISNTRA_API_KEY>`, `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "study_area_id": "kerala-floods-2018",
    "reference_date": "2018-08-08",
    "comparison_date": "2018-08-16"
  }
  ```
- **Validation Rules**:
  - `study_area_id` must exist in `study_areas.json` (else HTTP 404).
  - `comparison_date` must be strictly greater than `reference_date` (else HTTP 400 `INVALID_DATE_RANGE`).
  - Reference pass and comparison pass must share identical `track` and `orbit_direction` (else HTTP 400 `INCONSISTENT_ORBIT_GEOMETRY`).
- **Response (HTTP 201)**:
  ```json
  {
    "investigation_id": "INV-2026-KER-009",
    "status": "CREATED",
    "created_at": "2026-11-14T18:00:00Z",
    "evidence_ledger": { ... },
    "layers_endpoint": "/api/investigations/INV-2026-KER-009/layers",
    "evaluation_endpoint": "/api/investigations/INV-2026-KER-009/evaluation",
    "report_endpoint": "/api/investigations/INV-2026-KER-009/report"
  }
  ```

### 2. Evaluate Investigation (`POST /api/investigations/{id}/evaluate`)
- **Headers**: `X-API-Key: <BHNMISNTRA_API_KEY>`, `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "changed_area_sq_km": 34.8,
    "observations": [
      {"acquisition_id": "S1A_01", "date": "2018-08-28", "valid": true, "change_detected": true},
      {"acquisition_id": "S1A_02", "date": "2018-09-09", "valid": true, "change_detected": true},
      {"acquisition_id": "S1A_03", "date": "2018-09-21", "valid": true, "change_detected": false}
    ],
    "confounder_flags": ["CLEAR"],
    "notes": "Sentinel-1A dual-pol amplitude ratio calibrated against Copernicus DEM."
  }
  ```
- **Validation Rules**:
  - `changed_area_sq_km` must be $\ge 0.0$ (else HTTP 422 `INVALID_REQUEST_PARAMETERS`).
  - All observation dates must be strictly greater than `comparison_date` (else HTTP 400 `INVALID_OBSERVATION_DATE`).
  - Observations must match official acquisitions for the study area (else HTTP 400 `ACQUISITION_NOT_IN_STUDY_AREA`).
- **Response (HTTP 200)**:
  ```json
  {
    "investigation_id": "INV-2026-KER-009",
    "evidence_label": "Supported",
    "verification_status": "VERIFIED",
    "beat_test_status": "COMPLETED",
    "beat_test_result": "matches",
    "valid_observations_count": 3,
    "detected_observations_count": 2,
    "persistence_ratio": 0.6667,
    "persistence_threshold": 0.667,
    "meets_persistence_threshold": true,
    "excluded_acquisitions": [],
    "confounder_flags": ["CLEAR"],
    "confounders_clear": true,
    "reasons_for_label": [
      "Sufficient post-event observations available: 3 valid satellite acquisitions evaluated (minimum required: 3).",
      "Beat Test passed for receding phenomenon: initial surface change detected in 2/3 valid passes (66.7%) followed by documented recession in subsequent acquisitions.",
      "Confounder check clear: no severe weather, ionospheric noise, or steep topographic distortion flagged."
    ],
    "changed_area_sq_km": 34.8,
    "notes": "Sentinel-1A dual-pol amplitude ratio calibrated against Copernicus DEM.",
    "data_provenance": "ILLUSTRATIVE — NOT REAL DATA"
  }
  ```

### 3. Serve Map Layer (`GET /api/investigations/{id}/layers/{layer}`)
- **Path Parameters**: `layer` $\in$ `{change-mask, continuous, reference, comparison}` (aliases like `mask`, `difference` supported).
- **MIME Deliveries**:
  - `.tif` / `.tiff` $\rightarrow$ `Content-Type: image/tiff`
  - `.geojson` $\rightarrow$ `Content-Type: application/geo+json`
  - `.png` $\rightarrow$ `Content-Type: image/png`
- **If Missing on Disk**: Returns HTTP 404 with code `LAYER_ASSET_NOT_FOUND` and suggested action directing the user to await pipeline generation.

---

## 8. Test Suite & Verification

### Running the Test Suite
From the repository root:
```powershell
backend\.venv\Scripts\python.exe backend\tests\run_all.py
```

### Safety & Sandboxing Guarantees
- Tests execute inside private temporary directories created via `tempfile.TemporaryDirectory`.
- Service storage paths are dynamically patched during tests.
- Persistent competition files under `backend/data/` and `backend/outputs/` are **never written to or deleted** by tests.
- Master runner performs automated pre- and post-test file hash/mtime audits.

### Current Test Results
- **Total Test Cases**: 91
- **Passed**: 91 (100%)
- **Failed**: 0
- **Errors**: 0
- **Data Footprint Status**: `PASS (100% Unmodified)`

---

## 9. External Services & Database Architecture

- **No External Database Required**: Operates using lightweight, atomic file-based persistence:
  - `backend/data/investigations.json`
  - `backend/outputs/ledgers/{investigation_id}.json`
- **Data Protection Mechanisms**:
  - Writes are buffered to `.tmp.<uuid>` files, synced to physical media via `os.fsync`, and replaced atomically with `os.replace`.
  - Corrupted database files are preserved in-place, timestamped `.corrupt.<timestamp>` copies are created, and API calls fail closed with HTTP 500 without resetting the database.
- **External Satellite Gateway**: Optional proxy connectivity to NASA Alaska Satellite Facility (ASF) DAAC or ESA Copernicus Hub for acquiring raw Sentinel-1 GRD granules.

---

## 10. Known Blockers & Integration Checklist

### Outstanding Dependencies for External Repositories
1. **Real SAR Pipeline Generation (Member 3 / Science Lead)**:
   - Investigations `INV-2026-VAL-004` (Valencia) and `INV-2026-KER-003` to `KER-008` (Kerala repeat passes) currently return HTTP 404 for map layers because pipeline output rasters have not yet been produced.
   - Once the scientific pipeline executes, copy generated files into:
     ```text
     backend/outputs/layers/<investigation_id>/change-mask.tif
     backend/outputs/layers/<investigation_id>/continuous.tif
     backend/outputs/layers/<investigation_id>/reference.tif
     backend/outputs/layers/<investigation_id>/comparison.tif
     ```
2. **Frontend UI Data Binding (Member 1 / Frontend Lead)**:
   - Bind study area selection to `GET /api/study-areas`.
   - Bind pass selection to `GET /api/study-areas/{id}/acquisitions`.
   - Trigger new investigations via `POST /api/investigations` with header `X-API-Key`.
   - Render spatial map layers in MapLibre / Leaflet by pointing image/vector tile sources directly to `GET /api/investigations/{id}/layers/{layer}`.
   - Display three-state evidence badges using `GET /api/investigations/{id}/evaluation`.
3. **Transition to Real Provenance**:
   - Existing demonstration investigations currently disclose `"data_provenance": "ILLUSTRATIVE — NOT REAL DATA"`.
   - When authentic Sentinel-1/NISAR granules are processed, update `data_provenance` in `investigations.json` and the corresponding Evidence Ledger to `"COPERNICUS SENTINEL-1 SAR (NASA ASF / ESA)"`.

---

*Handoff document prepared and saved to `INTEGRATION_HANDOFF.md`.*

