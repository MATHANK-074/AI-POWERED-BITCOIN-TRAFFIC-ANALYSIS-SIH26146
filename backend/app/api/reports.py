import io
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
from app.database.duckdb_manager import DuckDBManager

router = APIRouter(prefix="/api/export", tags=["Exports & Reports"])
db = DuckDBManager()

@router.get("/transactions/csv")
def export_transactions_csv():
    conn = db.get_connection()
    try:
        df = conn.execute("SELECT * FROM transactions").df()
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response = Response(content=stream.getvalue(), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=suspicious_transactions.csv"
        return response
    finally:
        conn.close()

@router.get("/leads/csv")
def export_leads_csv():
    conn = db.get_connection()
    try:
        df = conn.execute("SELECT * FROM investigation_leads").df()
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response = Response(content=stream.getvalue(), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=investigation_leads.csv"
        return response
    finally:
        conn.close()

@router.get("/report/html")
def export_investigation_report_html():
    conn = db.get_connection()
    try:
        stats = db.get_statistics()
        leads = conn.execute("SELECT * FROM investigation_leads ORDER BY priority_score DESC LIMIT 10").df().to_dict(orient="records")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>KRISHIGUARD Forensic Investigation Report</title>
            <style>
                body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; background-color: #f8fafc; color: #0f172a; }}
                h1 {{ color: #1e293b; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
                .stat-box {{ display: inline-block; width: 30%; background: #ffffff; padding: 15px; margin: 10px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; }}
                .stat-num {{ font-size: 24px; font-weight: bold; color: #2563eb; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #ffffff; }}
                th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; font-size: 14px; }}
                th {{ background: #f1f5f9; }}
                .critical {{ color: #dc2626; font-weight: bold; }}
                .high {{ color: #ea580c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>KRISHIGUARD - Bitcoin Forensic Investigation Summary</h1>
            <p>Generated At: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            
            <h2>System Summary Statistics</h2>
            <div class="stat-box"><div class="stat-num">{stats['total_transactions']:,}</div>Total Transactions</div>
            <div class="stat-box"><div class="stat-num">{stats['total_wallets']:,}</div>Unique Wallets</div>
            <div class="stat-box"><div class="stat-num">{stats['anomalies_detected']:,}</div>Detected Anomalies</div>
            
            <h2>Top Prioritized Investigation Leads</h2>
            <table>
                <tr>
                    <th>Lead ID</th>
                    <th>Entity ID</th>
                    <th>Priority Score</th>
                    <th>Priority Level</th>
                    <th>Anomaly Score</th>
                    <th>Confidence</th>
                </tr>
        """
        for lead in leads:
            level_cls = "critical" if lead['priority_level'] == "CRITICAL" else ("high" if lead['priority_level'] == "HIGH" else "")
            html_content += f"""
                <tr>
                    <td>{lead['lead_id']}</td>
                    <td>{lead['entity_id']}</td>
                    <td>{lead['priority_score']}</td>
                    <td class="{level_cls}">{lead['priority_level']}</td>
                    <td>{lead['anomaly_score']}</td>
                    <td>{lead['confidence_score']}</td>
                </tr>
            """
        html_content += """
            </table>
        </body>
        </html>
        """
        return Response(content=html_content, media_type="text/html")
    finally:
        conn.close()
