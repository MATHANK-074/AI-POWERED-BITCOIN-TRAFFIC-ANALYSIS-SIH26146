from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import pandas as pd
from app.database.duckdb_manager import DuckDBManager

router = APIRouter(prefix="/api/entities", tags=["Entities"])
db = DuckDBManager()

@router.get("")
def get_entities(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    entity_type: Optional[str] = None,
    search: Optional[str] = None
):
    conn = db.get_connection()
    try:
        where_clauses = []
        params = []

        if entity_type:
            where_clauses.append("entity_type = ?")
            params.append(entity_type.lower())
        if search:
            where_clauses.append("entity_id LIKE ?")
            params.append(f"%{search}%")

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        query = f"SELECT * FROM entity_features{where_sql} ORDER BY total_amount_btc DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        df = conn.execute(query, params).df()
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient="records")
    finally:
        conn.close()

@router.get("/{entity_id}")
def get_entity_profile(entity_id: str):
    conn = db.get_connection()
    try:
        feat = conn.execute("SELECT * FROM entity_features WHERE entity_id = ?", [entity_id]).df()
        if feat.empty:
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

        feat = feat.where(pd.notnull(feat), None).to_dict(orient="records")[0]

        anom = conn.execute("SELECT * FROM anomalies WHERE entity_id = ?", [entity_id]).df()
        anom_dict = anom.where(pd.notnull(anom), None).to_dict(orient="records")[0] if not anom.empty else {}

        # Fetch recent transactions
        txs = conn.execute(
            "SELECT * FROM transactions WHERE input_wallet = ? OR output_wallet = ? OR src_ip = ? LIMIT 50",
            [entity_id, entity_id, entity_id]
        ).df()
        txs_list = txs.where(pd.notnull(txs), None).to_dict(orient="records")

        return {
            "entity_profile": feat,
            "anomaly_info": anom_dict,
            "recent_transactions": txs_list
        }
    finally:
        conn.close()
