import os
import json
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import Dict, Any, List
from app.config import REPORTS_DIR

class ReportExporter:
    def __init__(self, reports_dir: str = REPORTS_DIR):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, stats: Dict[str, Any], leads: List[Dict[str, Any]], format_type: str = "html") -> str:
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_id = f"investigation_report_{timestamp_str}"

        if format_type.lower() == "json":
            out_file = self.reports_dir / f"{report_id}.json"
            report_data = {
                "report_id": report_id,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "statistics": stats,
                "prioritized_leads": leads,
                "disclaimer": "This analytical report provides decision-support indicators for research and prioritization. Model outputs do not establish criminal conduct, identity, or ownership."
            }
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
            return str(out_file)

        elif format_type.lower() == "csv":
            out_file = self.reports_dir / f"{report_id}.csv"
            df = pd.DataFrame(leads)
            df.to_csv(out_file, index=False)
            return str(out_file)

        else:
            # HTML Exporter
            out_file = self.reports_dir / f"{report_id}.html"
            html_content = self._render_html(report_id, stats, leads)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            return str(out_file)

    def _render_html(self, report_id: str, stats: Dict[str, Any], leads: List[Dict[str, Any]]) -> str:
        leads_rows = ""
        for l in leads:
            p_level = l.get("priority_level", "Lower")
            badge_color = "#ef4444" if p_level == "High" else "#f97316" if p_level == "Elevated" else "#eab308" if p_level == "Moderate" else "#3b82f6"
            
            leads_rows += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #334155;"><strong>{l.get('lead_id')}</strong></td>
                <td style="padding: 10px; border-bottom: 1px solid #334155;"><code>{l.get('entity_id')}</code></td>
                <td style="padding: 10px; border-bottom: 1px solid #334155;">{l.get('entity_type', '').upper()}</td>
                <td style="padding: 10px; border-bottom: 1px solid #334155;">
                    <span style="background: {badge_color}; color: #ffffff; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85rem;">
                        {l.get('priority_score')}/100 ({p_level})
                    </span>
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #334155;">{l.get('anomaly_score')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #334155; max-width: 400px; font-size: 0.9rem; color: #cbd5e1;">
                    <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">{l.get('explanation')}</pre>
                </td>
            </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Bitcoin Investigation Analytical Report - {report_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 24px; margin-bottom: 24px; }}
        h1 {{ color: #38bdf8; margin-top: 0; }}
        h2 {{ color: #94a3b8; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .stat-box {{ background: #0f172a; padding: 16px; border-radius: 6px; border-left: 4px solid #38bdf8; }}
        .stat-val {{ font-size: 1.8rem; font-weight: bold; color: #f8fafc; }}
        .stat-lbl {{ font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; text-align: left; }}
        th {{ background: #0f172a; padding: 12px; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; border-bottom: 2px solid #334155; }}
        .disclaimer {{ background: #450a0a; border: 1px solid #991b1b; color: #fca5a5; padding: 16px; border-radius: 6px; font-size: 0.9rem; margin-top: 32px; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>OFFLINE BITCOIN INVESTIGATION REPORT</h1>
        <p style="color: #94a3b8;">Report Reference: <code>{report_id}</code> | Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>

    <div class="card">
        <h2>Executive Statistics Summary</h2>
        <div class="grid">
            <div class="stat-box">
                <div class="stat-val">{stats.get('total_transactions', 0):,}</div>
                <div class="stat-lbl">Total Transactions</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">{stats.get('total_wallets', 0):,}</div>
                <div class="stat-lbl">Unique Wallets</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">{stats.get('total_ips', 0):,}</div>
                <div class="stat-lbl">Unique IP Addresses</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">{stats.get('correlated_events', 0):,}</div>
                <div class="stat-lbl">Correlated Candidates</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">{stats.get('anomalies_detected', 0):,}</div>
                <div class="stat-lbl">Anomalies Detected</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>Prioritized Investigative Leads</h2>
        <table>
            <thead>
                <tr>
                    <th>Lead ID</th>
                    <th>Entity Identifier</th>
                    <th>Type</th>
                    <th>Priority Score</th>
                    <th>Anomaly Score</th>
                    <th>Lead Explanation & Supporting Evidence</th>
                </tr>
            </thead>
            <tbody>
                {leads_rows}
            </tbody>
        </table>
    </div>

    <div class="disclaimer">
        <strong>RESPONSIBLE AI DISCLAIMER & LIMITATIONS:</strong><br>
        This report is generated by an offline decision-support analytics system for research and educational purposes.
        Correlation scores, ML anomaly flags, and investigation priority metrics do not by themselves establish criminal conduct, identity, or legal ownership. Human investigator review and corroboration are required.
    </div>
</body>
</html>"""
