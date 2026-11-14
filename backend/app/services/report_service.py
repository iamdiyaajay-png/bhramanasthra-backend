"""
Report Generation Service for BHnMISnTRA
Generates self-contained, printable HTML evidence dossiers for investigations.
NASA Space Apps Challenge 2026: Dancing with the SARs
"""

import html
from typing import Any, Dict, List, Optional

from app.services import investigation_service, layer_service
from app.schemas.investigation import InvestigationDetail, EvidenceLedgerRecord


def _esc(value: Any, default: str = "Not available") -> str:
    """Escapes dynamic content for safe HTML rendering, handling None cleanly."""
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    return html.escape(text)


def generate_html_report(investigation_id: str) -> str:
    """
    Generates a complete, self-contained printable HTML report for an investigation.
    Draws all data dynamically from the persistent investigation state and Evidence Ledger.
    Does not recalculate evaluation or alter any records.
    """
    # 1. Retrieve investigation detail and ledger (raises 404 if not found)
    inv: InvestigationDetail = investigation_service.get_investigation_by_id(investigation_id)
    ledger: EvidenceLedgerRecord = inv.evidence_ledger

    # 2. Retrieve available layers manifest
    layers_manifest = layer_service.list_investigation_layers(investigation_id)
    available_layers = layers_manifest.get("layers", [])

    # 3. Dynamic badge styling based on Evidence Label
    label = ledger.evidence_label.strip() if ledger.evidence_label else "Unverified"
    if label == "Supported":
        badge_class = "badge-supported"
        badge_bg = "#dcfce7"
        badge_color = "#15803d"
        badge_border = "#86efac"
    elif label == "Inconclusive":
        badge_class = "badge-inconclusive"
        badge_bg = "#fef3c7"
        badge_color = "#b45309"
        badge_border = "#fde68a"
    else:
        badge_class = "badge-unverified"
        badge_bg = "#f1f5f9"
        badge_color = "#475569"
        badge_border = "#cbd5e1"

    # 4. Format reasons list
    reasons_html = ""
    if ledger.reasons_for_label:
        reasons_items = "".join(f"<li>{_esc(r)}</li>" for r in ledger.reasons_for_label)
        reasons_html = f"<ol class='reasons-list'>{reasons_items}</ol>"
    else:
        reasons_html = "<p class='muted'>No evaluation reasons recorded yet.</p>"

    # 5. Format excluded acquisitions
    excluded_html = ""
    if ledger.excluded_acquisitions:
        excluded_rows = "".join(
            f"<tr><td><code>{_esc(ex.get('acquisition_id'))}</code></td>"
            f"<td>{_esc(ex.get('date'))}</td>"
            f"<td><span class='tag-excluded'>EXCLUDED</span> {_esc(ex.get('reason'))}</td></tr>"
            for ex in ledger.excluded_acquisitions
        )
        excluded_html = f"""
        <table class='data-table'>
            <thead><tr><th>Acquisition ID</th><th>Date</th><th>Exclusion Rationale</th></tr></thead>
            <tbody>{excluded_rows}</tbody>
        </table>
        """
    else:
        excluded_html = "<p class='muted'>No satellite passes were excluded for this investigation.</p>"

    # 6. Format later valid acquisitions timeline
    later_rows = ""
    if inv.later_acquisitions:
        for acq in inv.later_acquisitions:
            status_tag = "<span class='tag-valid'>VALID</span>" if acq.valid else "<span class='tag-excluded'>EXCLUDED</span>"
            note = _esc(acq.exclusion_reason) if acq.exclusion_reason else "Valid observation pass"
            later_rows += f"""
            <tr>
                <td><code>{_esc(acq.acquisition_id)}</code></td>
                <td>{_esc(acq.date)}</td>
                <td>{status_tag}</td>
                <td>{note}</td>
            </tr>
            """
        later_table = f"""
        <table class='data-table'>
            <thead><tr><th>Acquisition ID</th><th>Date</th><th>Validity</th><th>Note</th></tr></thead>
            <tbody>{later_rows}</tbody>
        </table>
        """
    else:
        later_table = "<p class='muted'>No subsequent satellite acquisitions recorded.</p>"

    # 7. Format available map layers
    layers_rows = ""
    for lyr in available_layers:
        avail_badge = "<span class='tag-valid'>AVAILABLE</span>" if lyr.get("available") else "<span class='tag-muted'>PENDING</span>"
        layers_rows += f"""
        <tr>
            <td><strong>{_esc(lyr.get('name'))}</strong> (<code>{_esc(lyr.get('layer'))}</code>)</td>
            <td>{avail_badge}</td>
            <td>{_esc(lyr.get('format')).upper()}</td>
            <td><code>{_esc(lyr.get('endpoint'))}</code></td>
        </tr>
        """
    layers_table = f"""
    <table class='data-table'>
        <thead><tr><th>Layer</th><th>Status</th><th>Format</th><th>Serving Endpoint</th></tr></thead>
        <tbody>{layers_rows}</tbody>
    </table>
    """

    # 8. Format independent reference
    indep_ref = ledger.independent_reference
    if indep_ref and isinstance(indep_ref, dict):
        indep_rows = "".join(f"<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>" for k, v in indep_ref.items())
        indep_html = f"<table class='meta-table'><tbody>{indep_rows}</tbody></table>"
    else:
        indep_html = "<p class='muted'>Independent reference data has not been ingested (PRD Section 4: Awaiting external ground validation).</p>"

    # 9. Format limitations list
    limitations_html = ""
    if ledger.known_limitations:
        limitations_items = "".join(f"<li>{_esc(lim)}</li>" for lim in ledger.known_limitations)
        limitations_html = f"<ul class='limitations-list'>{limitations_items}</ul>"
    else:
        limitations_html = "<p class='muted'>Standard SAR limitations apply.</p>"

    # 10. Confounder flags
    confounders_str = ", ".join(_esc(f) for f in ledger.confounder_flags) if ledger.confounder_flags else "CLEAR"

    # Changed area display
    changed_area_display = (
        f"{_esc(ledger.changed_area_sq_km)} sq km"
        if ledger.changed_area_sq_km is not None
        else "Pending (Awaiting Member 1 SAR Pipeline)"
    )

    # Persistence ratio display
    persistence_ratio_str = "Not available (Evaluation pending)"
    if ledger.valid_later_acquisitions_count and ledger.valid_later_acquisitions_count >= 3 and ledger.beat_test_status == "COMPLETED":
        pct = (ledger.detected_later_acquisitions_count / ledger.valid_later_acquisitions_count) * 100
        persistence_ratio_str = f"{ledger.detected_later_acquisitions_count} / {ledger.valid_later_acquisitions_count} ({pct:.1f}%) [Threshold >= 66.7%]"

    # Provenance disclosure banner
    provenance_banner = ""
    if "ILLUSTRATIVE" in inv.data_provenance.upper() or "ILLUSTRATIVE" in ledger.data_provenance.upper():
        provenance_banner = f"""
        <div class="provenance-banner">
            <div class="banner-title">⚠️ DATA DISCLOSURE: {_esc(ledger.data_provenance)}</div>
            <div class="banner-text">
                This investigation report uses demonstrative, illustrative satellite telemetry and synthetic masks for the 
                <strong>NASA Space Apps Challenge 2026</strong>. It does not represent real ground-truth disaster claims or real-time operational satellite events.
            </div>
        </div>
        """

    # 11. Complete HTML assembly
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investigation Report — {_esc(inv.investigation_id)}</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #0284c7;
            --primary-hover: #0369a1;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.5;
            padding: 24px;
        }}
        .report-container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            padding: 40px;
        }}
        .action-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }}
        .print-button {{
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: background-color 0.15s ease;
        }}
        .print-button:hover {{ background-color: var(--primary-hover); }}
        .header-title {{ font-size: 26px; font-weight: 800; color: var(--text-main); letter-spacing: -0.5px; }}
        .header-subtitle {{ font-size: 14px; color: var(--text-muted); margin-top: 4px; }}
        .provenance-banner {{
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-left: 5px solid #d97706;
            border-radius: 6px;
            padding: 16px;
            margin: 24px 0;
        }}
        .banner-title {{ font-size: 14px; font-weight: 700; color: #b45309; text-transform: uppercase; letter-spacing: 0.5px; }}
        .banner-text {{ font-size: 13px; color: #78350f; margin-top: 6px; line-height: 1.4; }}
        .section-card {{
            margin-top: 28px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }}
        .section-heading {{
            font-size: 16px;
            font-weight: 700;
            color: #1e293b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 14px;
        }}
        .badge {{
            display: inline-block;
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 700;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: {badge_bg};
            color: {badge_color};
            border: 1px solid {badge_border};
        }}
        .meta-table, .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-top: 10px;
        }}
        .meta-table th, .meta-table td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        .meta-table th {{ width: 28%; color: var(--text-muted); font-weight: 600; }}
        .meta-table td {{ color: var(--text-main); }}
        .data-table th, .data-table td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        .data-table th {{
            background: #f8fafc;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}
        .tag-valid {{
            background: #dcfce7;
            color: #15803d;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .tag-excluded {{
            background: #fee2e2;
            color: #b91c1c;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .tag-muted {{
            background: #e2e8f0;
            color: #475569;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .reasons-list, .limitations-list {{
            margin-left: 20px;
            font-size: 13px;
            color: var(--text-main);
            margin-top: 8px;
        }}
        .reasons-list li, .limitations-list li {{ margin-bottom: 6px; }}
        .code-box {{
            background: #0f172a;
            color: #e2e8f0;
            padding: 12px 16px;
            border-radius: 6px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 8px;
        }}
        .muted {{ color: var(--text-muted); font-size: 13px; font-style: italic; }}
        .footer {{
            margin-top: 40px;
            padding-top: 16px;
            border-top: 1px solid var(--border);
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
        }}
        @media print {{
            body {{ background: white; padding: 0; color: black; font-size: 11pt; }}
            .report-container {{ border: none; box-shadow: none; padding: 0; max-width: 100%; }}
            .no-print, .print-button {{ display: none !important; }}
            .section-card {{ break-inside: avoid; page-break-inside: avoid; }}
            .data-table {{ break-inside: avoid; page-break-inside: avoid; }}
            .code-box {{ background: #f8fafc; color: #0f172a; border: 1px solid #cbd5e1; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <!-- Top Action Bar (Hidden during printing) -->
        <div class="action-bar no-print">
            <div>
                <span style="font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">
                    BHnMISnTRA Evidence Report
                </span>
            </div>
            <button onclick="window.print()" class="print-button" title="Print document or save as PDF">
                🖨️ Print / Save as PDF
            </button>
        </div>

        <!-- Header -->
        <header>
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h1 class="header-title">Surface Change Evidence Report</h1>
                    <div class="header-subtitle">
                        NASA Space Apps Challenge 2026: <em>Dancing with the SARs</em>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="badge {_esc(badge_class)}">{_esc(label)}</span>
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">
                        Status: {_esc(ledger.verification_status)}
                    </div>
                </div>
            </div>
        </header>

        {provenance_banner}

        <!-- 1. Investigation Identity & Study Area -->
        <div class="section-card">
            <h2 class="section-heading">1. Investigation & Geographic Context</h2>
            <table class="meta-table">
                <tbody>
                    <tr><th>Investigation ID</th><td><strong><code>{_esc(inv.investigation_id)}</code></strong></td></tr>
                    <tr><th>Study Area</th><td>{_esc(inv.study_area.name)} (<code>{_esc(inv.study_area.id)}</code>)</td></tr>
                    <tr><th>Phenomenon</th><td>{_esc(inv.study_area.phenomenon_type).title()} (Expected: {_esc(inv.study_area.expected_behavior).title()})</td></tr>
                    <tr><th>Bounding Box</th><td><code>{_esc(inv.study_area.bounding_box)}</code></td></tr>
                    <tr><th>CRS</th><td>{_esc(inv.study_area.crs)}</td></tr>
                    <tr><th>Data Tier</th><td>{_esc(inv.study_area.data_tier)}</td></tr>
                    <tr><th>Created At</th><td>{_esc(inv.created_at)}</td></tr>
                </tbody>
            </table>
        </div>

        <!-- 2. Satellite Sensor & Observation Passes -->
        <div class="section-card">
            <h2 class="section-heading">2. Satellite Data Provenance & Geometry</h2>
            <table class="meta-table">
                <tbody>
                    <tr><th>Satellite Mission</th><td>{_esc(ledger.satellite_mission)}</td></tr>
                    <tr><th>Sensor & Mode</th><td>{_esc(ledger.sensor)} ({_esc(ledger.mode)} Mode)</td></tr>
                    <tr><th>Polarization</th><td>{_esc(", ".join(ledger.polarization))}</td></tr>
                    <tr><th>Orbit Direction & Track</th><td>{_esc(ledger.orbit_direction)} (Track {_esc(ledger.track)})</td></tr>
                    <tr><th>Reference Pass</th><td>{_esc(ledger.reference_acquisition_date)} (<code>{_esc(ledger.reference_acquisition_id)}</code>)</td></tr>
                    <tr><th>Comparison Pass</th><td>{_esc(ledger.comparison_acquisition_date)} (<code>{_esc(ledger.comparison_acquisition_id)}</code>)</td></tr>
                </tbody>
            </table>

            <h3 style="font-size: 13px; font-weight: 600; margin-top: 16px; color: var(--text-muted);">
                Subsequent Evaluation Passes ({_esc(ledger.valid_later_acquisitions_count)} valid evaluated):
            </h3>
            {later_table}
        </div>

        <!-- 3. Beat Test & Evidence Evaluation -->
        <div class="section-card">
            <h2 class="section-heading">3. Beat Test & Temporal Evaluation (PRD Section 9)</h2>
            <table class="meta-table">
                <tbody>
                    <tr><th>Evidence Label</th><td><span class="badge {_esc(badge_class)}">{_esc(label)}</span></td></tr>
                    <tr><th>Beat Test Status</th><td>{_esc(ledger.beat_test_status)}</td></tr>
                    <tr><th>Temporal Result</th><td><code>{_esc(ledger.beat_test_result)}</code></td></tr>
                    <tr><th>Persistence Ratio</th><td><strong>{_esc(persistence_ratio_str)}</strong></td></tr>
                    <tr><th>Confounder Flags</th><td>{_esc(confounders_str)}</td></tr>
                    <tr><th>Changed Surface Area</th><td>{_esc(changed_area_display)}</td></tr>
                    <tr><th>Persistence Summary</th><td>{_esc(ledger.persistence_result)}</td></tr>
                </tbody>
            </table>

            <h3 style="font-size: 13px; font-weight: 600; margin-top: 16px; color: var(--text-muted);">
                Evaluation Justification & Label Rationale:
            </h3>
            {reasons_html}
        </div>

        <!-- 4. Excluded Observations -->
        <div class="section-card">
            <h2 class="section-heading">4. Excluded Observations & Quality Flags</h2>
            {excluded_html}
        </div>

        <!-- 5. Map Layer Assets -->
        <div class="section-card">
            <h2 class="section-heading">5. Associated Map Layers (PRD Section 3.5)</h2>
            {layers_table}
        </div>

        <!-- 6. Traceability, Independent Reference & Limitations -->
        <div class="section-card">
            <h2 class="section-heading">6. Traceability & Scientific Limitations</h2>
            <table class="meta-table">
                <tbody>
                    <tr><th>Configuration Hash</th><td><code>{_esc(ledger.configuration_hash)}</code></td></tr>
                    <tr><th>Processing Method</th><td>{_esc(ledger.processing_method)}</td></tr>
                    <tr><th>Reproduce Command</th><td><div class="code-box">{_esc(ledger.reproduce_command)}</div></td></tr>
                </tbody>
            </table>

            <h3 style="font-size: 13px; font-weight: 600; margin-top: 16px; color: var(--text-muted);">
                Independent Reference Data (PRD Section 4):
            </h3>
            {indep_html}

            <h3 style="font-size: 13px; font-weight: 600; margin-top: 16px; color: var(--text-muted);">
                Documented Radar & Methodological Limitations:
            </h3>
            {limitations_html}
        </div>

        <!-- Footer -->
        <div class="footer">
            <span>BHnMISnTRA Platform v1.0.0</span>
            <span>Generated from Evidence Ledger — Verification Status: {_esc(ledger.verification_status)}</span>
        </div>
    </div>
</body>
</html>
"""
    return html_content

