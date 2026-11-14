# NASA Hackathon Project Definition — BHRAMANASTHRA

## 1. Project Overview & Mission Statement
**BHRAMANASTHRA** (`BHnMISnTRA`) is an advanced, production-grade radar evidence and surface change analysis platform engineered for the **NASA Space Apps Challenge 2026: *"Dancing with the SARs"*** by a dedicated **4-member multidisciplinary team** registered for the **Universal Event**. The platform ingests Synthetic Aperture Radar (SAR) repeat-pass satellite observations (Copernicus Sentinel-1 and NASA-ISRO NISAR), detects surface change (flood inundation and landslide scarring), evaluates multi-temporal persistence via the **SAR Beat Test** (PRD Section 9), and maintains tamper-evident, reproducible **Evidence Ledgers** (PRD Section 13) with audit-ready printable reports.

## 2. Mandatory Official Compliance Constraints
All workstreams must strictly adhere to [COMPLIANCE.md](file:///c:/Users/jasmi/OneDrive/Documents/nasa/COMPLIANCE.md):
1. **NASA Data Sources**: Incorporate NASA Alaska Satellite Facility (ASF) DAAC and NASA Earthdata Cloud.
2. **Sentinel-1 vs. NISAR Isolation**: Keep historical Sentinel-1 (C-band) and contemporary NISAR (L-band/S-band) strictly separate. **Never describe Sentinel-1 as NISAR**.
3. **Zero Fabrication**: Record dataset identifiers, dates, processing steps, and limitations. Never fabricate unavailable observations.
4. **Demonstration Limit**: Final submission demo must be either a **video $\le 30$ seconds** OR a **presentation $\le 7$ slides** (inclusive of title and closing slides).
5. **AI Disclosure**: Disclose all AI tools and uses. AI-generated visual media must carry a visible `[AI-GENERATED]` watermark. **Never generate or modify NASA branding using AI** (14 CFR § 1221).
6. **Asset Rights**: All assets must have verified licenses (public domain, open access, MIT, ISC). **Attribution alone does not grant permission**.
7. **Team Eligibility**: Maintain exactly 2–6 participants (BHRAMANASTHRA has 4 members) registered for the same Universal Event.

## 3. Core Technical Objectives
- **Scientific Rigor**: Implement PRD v3 SAR Beat Test temporal persistence math with automatic confounder checks.
- **High-End Aesthetic & UI/UX**: Leverage `taste-skill`, `21st-ui`, and `awesome-design-md` to build an interface that feels like a modern mission control center (SpaceX / Linear grade), eliminating generic "AI slop".
- **Enterprise-Grade Security**: Enforce strict backend authentication on all protected routes and guarantee **ZERO exposed private API keys** in frontend client bundles.
- **Production Completeness**: Implement high-value production-grade pages often forgotten by hackathon teams (404, Error boundaries, empty states, system diagnostics, team credits, onboarding tour).
- **Token & Performance Optimization**: Utilize `headroom` context compression to handle dense telemetry payloads and logs without degrading model reasoning.

## 4. Team Division of Responsibilities (4 Members)
- **Member 1 (Frontend & Interaction Lead)**: UI/UX, Tailwind CSS, 3D visualization, component styling, responsive layouts, map layers.
- **Member 2 (Backend & Security Lead)**: NASA API proxying, data safety shields, atomic JSON storage, Evidence Ledger service, backend authentication.
- **Member 3 (Science & ML Lead)**: NASA ASF DAAC datasets, NISAR vs Sentinel-1 modeling, SAR Beat Test persistence equations, Headroom compaction.
- **Member 4 (QA, Presentation & Operations Lead)**: End-to-end Playwright tests, 7-slide pitch presentation deck, production-grade pages, documentation, compliance audit.

## 5. Non-Goals (Scope Boundaries)
- No hardcoded API keys or external secrets committed to source control or exposed in client bundles.
- No untested or unverified mock data presented as verified NASA telemetry; zero fabricated satellite observations.
- No AI-generated or modified NASA logos or official insignia.
- No presentation exceeding 7 slides or demo video exceeding 30 seconds.
- No running automated penetration tests without explicit user confirmation.

