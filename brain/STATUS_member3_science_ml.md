# Member 3 Workstream: Science & Machine Learning

**Owner**: Member 3 (Science & ML Lead)  
**Challenge**: NASA Space Apps Challenge 2026: *"Dancing with the SARs"*  
**Active Skills**: `headroom`, `project-brain`  
**Optimization Target**: Authentic SAR backscatter calibration, multi-temporal persistence modeling, Headroom payload compaction

## Current Focus
Integrating authentic NASA SAR data from the Alaska Satellite Facility (ASF) DAAC, strictly separating historical Sentinel-1 from contemporary NISAR observations, and maintaining zero fabrication of unavailable observations.

## Mandatory Compliance Protocols (PRD v3 & Space Apps 2026)
- **NASA Data Gateway**: Ingest radar telemetry via NASA ASF DAAC Vertex API and NASA Earthdata Cloud.
- **Sensor Isolation**:
  - **Sentinel-1 (C-SAR)**: C-band ($\lambda = 5.6\text{ cm}$), ESA mission mirrored via NASA ASF; used for historical Kerala 2018 and Valencia 2024 flood inundation baselines. *Never describe Sentinel-1 as NISAR*.
  - **NISAR (NASA-ISRO SAR)**: Dual L-band ($\lambda = 24\text{ cm}$, NASA JPL) and S-band ($9.3\text{ cm}$, ISRO SAC); evaluates canopy penetration and surface slip in Wayanad 2024.
- **Zero Fabrication**: If real on-orbit observations are pending or not downlinked, honestly report `"data_provenance": "ILLUSTRATIVE — NOT REAL DATA"` or `"SAMPLE SCIENCE DATA — NASA JPL / ASF"`. Never synthesize mock data as verified real observations.

## Tasks & Progress

- [x] Context & token compression engine (`headroom`) adapted for Gemini 3.8 Flash High.
- [x] Data boundaries identified: NASA ASF DAAC Vertex portal and Copernicus Open Access Hub.
- [x] Challenge topic confirmed: *Dancing with the SARs* (SAR Beat Test temporal persistence).
- [x] Scientific Beat Test algorithm implemented in `backend/app/services/evidence_service.py` (PRD Section 9).
- [x] Receding vs. sustained phenomenon logic verified (Repair 2).
- [x] Spatial layer resolution for `.tif`, `.tiff`, and `.geojson` implemented (Repair 3).
- [x] Master compliance document compiled: [COMPLIANCE.md](file:///c:/Users/jasmi/OneDrive/Documents/nasa/COMPLIANCE.md).
- [ ] Process physical GeoTIFF change rasters for secondary investigations (`INV-2026-VAL-004` and `KER-003` to `KER-008`).
- [ ] Ingest full-resolution Copernicus DEM 30m tiles for Wayanad slope correction.
- [ ] Transition demonstration investigations to verified on-orbit data once granules are processed.

## Blockers & Open Items (Honest Reporting)
- Physical `.tif` raster layers for Valencia (`VAL-004`) and Kerala repeat passes (`KER-003` to `KER-008`) are pending generation; backend honestly serves HTTP 404 `LAYER_ASSET_NOT_FOUND` as designed.
- Full operational on-orbit NISAR science data is contemporary/post-launch; historical 2018 floods are strictly evaluated using authentic Sentinel-1 C-band from NASA ASF.

