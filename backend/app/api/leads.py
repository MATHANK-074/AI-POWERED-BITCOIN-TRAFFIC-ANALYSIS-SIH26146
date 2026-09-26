import json
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import pandas as pd
from app.database.duckdb_manager import DuckDBManager

router = APIRouter(prefix="/api/leads", tags=["Investigative Leads"])
db = DuckDBManager()

@router.get("")
def get_investigation_leads(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    priority_level: Optional[str] = None
):
    conn = db.get_connection()
    try:
        where_clauses = []
        params = []

        if priority_level:
            where_clauses.append("priority_level = ?")
            params.append(priority_level.upper())

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        query = f"SELECT * FROM investigation_leads{where_sql} ORDER BY priority_score DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        df = conn.execute(query, params).df()
        df = df.where(pd.notnull(df), None)

        records = df.to_dict(orient="records")
        for r in records:
            if r.get("reasons") and isinstance(r["reasons"], str):
                try:
                    r["reasons"] = json.loads(r["reasons"])
                except Exception:
                    pass
        return records
    finally:
        conn.close()

@router.get("/{lead_id}")
def get_lead_by_id(lead_id: str):
    conn = db.get_connection()
    try:
        df = conn.execute("SELECT * FROM investigation_leads WHERE lead_id = ? OR entity_id = ?", [lead_id, lead_id]).df()
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")

        df = df.where(pd.notnull(df), None)
        record = df.to_dict(orient="records")[0]
        if record.get("reasons") and isinstance(record["reasons"], str):
            try:
                record["reasons"] = json.loads(record["reasons"])
            except Exception:
                pass
        return record
    finally:
        conn.close()
