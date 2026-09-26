from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional
from app.storage.database import DatabaseManager

router = APIRouter(prefix="/api/wallets", tags=["Wallets"])
db = DatabaseManager()

@router.get("")
def get_wallets(
    query: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500)
):
    conn = db.get_connection()
    try:
        where_sql = " WHERE entity_type = 'wallet'"
        params = []

        if query:
            where_sql += " AND entity_id LIKE ?"
            params.append(f"%{query.strip()}%")

        total_count = conn.execute(f"SELECT COUNT(*) FROM entity_features{where_sql}", params).fetchone()[0]

        offset = (page - 1) * limit
        params_paged = params + [limit, offset]

        sql = f"""
            SELECT ef.*, a.anomaly_score, a.is_anomaly, a.cluster_id
            FROM entity_features ef
            LEFT JOIN anomalies a ON ef.entity_id = a.entity_id
            {where_sql}
            ORDER BY ef.tx_count DESC
            LIMIT ? OFFSET ?
        """
        df = conn.execute(sql, params_paged).df()
        records = df.to_dict(orient="records") if not df.empty else []

        return {
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit,
            "data": records
        }
    finally:
        conn.close()

@router.get("/{wallet_id}")
def get_wallet_detail(wallet_id: str):
    conn = db.get_connection()
    try:
        feat_res = conn.execute("SELECT * FROM entity_features WHERE entity_id = ?", [wallet_id]).df()
        if feat_res.empty:
            raise HTTPException(status_code=404, detail=f"Wallet {wallet_id} not found")
        
        wallet_data = feat_res.iloc[0].to_dict()

        # Join Anomaly data
        anom_res = conn.execute("SELECT * FROM anomalies WHERE entity_id = ?", [wallet_id]).df()
        if not anom_res.empty:
            wallet_data.update(anom_res.iloc[0].to_dict())

        # Recent transactions (incoming & outgoing)
        tx_res = conn.execute(
            "SELECT * FROM transactions WHERE input_wallet = ? OR output_wallet = ? ORDER BY transaction_timestamp DESC LIMIT 100",
            [wallet_id, wallet_id]
        ).df()
        wallet_data["recent_transactions"] = tx_res.to_dict(orient="records") if not tx_res.empty else []

        # Leads if prioritized
        lead_res = conn.execute("SELECT * FROM investigation_leads WHERE entity_id = ?", [wallet_id]).df()
        wallet_data["investigation_leads"] = lead_res.to_dict(orient="records") if not lead_res.empty else []

        return wallet_data
    finally:
        conn.close()
