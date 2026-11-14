# BHRAMANASTHRA Compliance Architecture & NASA Space Apps Directives

> **Official Master Document**: Refer to root [COMPLIANCE.md](file:///c:/Users/jasmi/OneDrive/Documents/nasa/COMPLIANCE.md) for full legal text, citations, asset registries, and 7-slide deck copy.

## Summary of 5 Mandatory Project Constraints

### 1. NASA Data Integrity & NISAR Separation
- **Official NASA Sources**: NASA Alaska Satellite Facility (ASF) DAAC and NASA Earthdata Cloud.
- **Sentinel-1 vs. NISAR Strict Isolation**:
  - Sentinel-1: C-band ($\lambda = 5.6\text{ cm}$), ESA-operated, historical flood baseline (2018/2024). *Never describe Sentinel-1 as NISAR*.
  - NISAR: Dual L-band ($\lambda = 24\text{ cm}$, NASA) and S-band ($9.3\text{ cm}$, ISRO). Evaluates vegetation canopy penetration and landslide slip (Wayanad).
- **Prohibition on Fabrication**: Unavailable on-orbit observations are never synthesized or fabricated; they are honestly flagged as `ILLUSTRATIVE — NOT REAL DATA` or `SAMPLE SCIENCE DATA — NASA JPL / ASF`.

### 2. Demonstration Limit: $\le 7$ Slides OR $\le 30$ Seconds Video
- **7-Slide Master Deck**:
  - Slide 1: Title & Challenge Identity (NASA Space Apps 2026, Universal Event, 4 Members)
  - Slide 2: The Challenge: Cloud Cover & Radar Ambiguity
  - Slide 3: The Solution: The SAR Beat Test Engine (PRD v3 persistence math)
  - Slide 4: Authentic NASA Data: Sentinel-1 vs. NISAR Separation
  - Slide 5: Scientific Traceability: The Evidence Ledger & 3-State Labels
  - Slide 6: Platform Performance & Real Impact (91/91 tests passing, 7.4s runtime)
  - Slide 7: Team Roster, Compliance Checklist & Open Science Link

### 3. AI Disclosure & Ethical Standards
- Disclosed Tools: Google Gemini 3.8 Flash High (System Architect & Backend), Antigravity 2.0 (Testing & Sandbox), Anthropic Claude (Planning & Ideation).
- Zero Generative AI in SAR Math: Beat Test persistence calculations and radar metrics are 100% deterministic code.
- AI Watermarking: Any AI-generated visual mockup carries `[AI-GENERATED — FOR CONCEPTUAL ILLUSTRATION ONLY]`.
- NASA Branding: **Strictly ZERO AI generation or modification of NASA logos or insignia** (14 CFR § 1221).

### 4. Asset Rights & Licensing
- All assets must have explicit open access or public domain rights.
- **Attribution alone does NOT grant permission.**
- NASA Data & Photography: Public Domain (17 U.S.C. § 105).
- Copernicus Sentinel Data: Free, full, open access (EU Regulation No 377/2014).
- Software: MIT / ISC / BSD-3.
- Basemaps: CartoDB (CC BY 4.0) & OpenStreetMap (ODbL).

### 5. Team Eligibility: Universal Event
- Requirement: 2 to 6 participants registered for the same Universal Event.
- BHRAMANASTHRA Roster: Exactly 4 participants (Members 1–4) registered under Universal Event for Global Judging.

### 6. Honest Status of Unmet Items
- Operational on-orbit NISAR science observations for 2018 historical floods do not exist in nature.
- Missing `.tif` layers for secondary investigations (`KER-003` to `KER-008` and `VAL-004`) return HTTP 404 with guidance rather than mock rasters.
